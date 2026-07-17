"""
Football Statistics Fetcher.
Connects to API-Football's free tier (direct API-Sports account, via
dashboard.api-football.com - NOT RapidAPI) to retrieve real fixtures,
head-to-head history, standings, and injuries for match analysis.

Design note: earlier versions of this module also returned "advanced"
metrics (xG, PPDA, possession, physical/set-piece stats) and contextual
fields (referee, weather, formation, matchday). Those were never part of
API-Football's actual response schema for this tier - they were silent
`dict.get(key, fabricated_default)` fallbacks that always returned the
fabricated default and were presented to the user/Claude as real data.
They have been removed rather than kept as fake numbers. Only fields the
API genuinely returns (team info, fixtures, standings, head-to-head,
injuries) are used, and everything derived from them (form, rest days,
BTTS/over-under trends) is computed from real match results.
"""
from typing import Dict, Any, List, Optional
import aiohttp
import logging
from datetime import datetime

from config.settings import settings
from src.data.providers.base import (
    FixtureResult,
    HeadToHead,
    TeamForm,
    TeamRef,
    build_match_data,
    derive_form,
)

logger = logging.getLogger(__name__)


class StatsFetcher:
    """
    Fetches football data from API-Football's free tier.
    Provides team info, real recent fixtures/form, standings, head-to-head
    and injuries. Implements the `MatchDataProvider` contract informally
    (see src/data/providers/base.py).
    """

    def __init__(self, cache_manager=None):
        """Initialize stats fetcher with API configuration.

        Args:
            cache_manager: optional CacheManager instance. When provided,
                team info and league context are cached to stay within the
                free tier's 100 requests/day budget.
        """
        self.api_key = settings.api_football_key
        # Direct API-Sports host (dashboard.api-football.com), not RapidAPI -
        # these are two different auth schemes for the same underlying data.
        # A RapidAPI-issued key would need X-RapidAPI-Key/X-RapidAPI-Host
        # against api-football-v1.p.rapidapi.com instead.
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            "x-apisports-key": self.api_key,
        }
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache_manager = cache_manager
        logger.info("Stats Fetcher initialized")

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session

    async def close(self) -> None:
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()

    def _current_season(self) -> int:
        """European season year: the season that started in August of the
        prior calendar year is still the 'current' one until the following
        August."""
        now = datetime.now()
        return now.year if now.month >= 8 else now.year - 1

    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Any]:
        """
        Make API request to API-Football.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            API response data or None if error
        """
        try:
            session = await self._get_session()
            url = f"{self.base_url}/{endpoint}"

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("response", [])
                elif response.status == 429:
                    logger.warning("Rate limit exceeded for API-Football")
                    return None
                else:
                    logger.error(f"API-Football error: {response.status}")
                    return None

        except Exception as e:
            logger.error(f"Error making request to {endpoint}: {e}", exc_info=True)
            return None

    async def get_team_info(self, team_name: str) -> Optional[Dict[str, Any]]:
        """
        Get team information by name (id, name, country, venue). Cached
        24h when a cache_manager is available, since a team's identity
        never changes intra-season.
        """
        if self.cache_manager:
            cached = await self.cache_manager.get_cached_team_info(team_name)
            if cached:
                return cached

        try:
            data = await self._make_request("teams", {"search": team_name})

            if not data or len(data) == 0:
                logger.warning(f"Team not found: {team_name}")
                return None

            team = data[0].get("team", {})

            info = {
                "id": team.get("id"),
                "name": team.get("name"),
                "country": team.get("country"),
                "logo": team.get("logo"),
                "venue_name": team.get("venue_name", ""),
                "venue_capacity": team.get("venue_capacity", 0),
            }

            if self.cache_manager:
                await self.cache_manager.cache_team_info(team_name, info)

            return info

        except Exception as e:
            logger.error(f"Error getting team info for {team_name}: {e}", exc_info=True)
            return None

    async def resolve_league_context(
        self, team_id: int, country: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Resolve the domestic league a team is currently playing in, and the
        current season year, instead of assuming a fixed league/season.

        Returns:
            {"league_id": int, "league_name": int, "season": int} or None
            if it can't be determined (never falls back to a guessed league).
        """
        cache_key = f"league_context:{team_id}"
        if self.cache_manager:
            cached = await self.cache_manager.get(cache_key)
            if cached:
                return cached

        try:
            data = await self._make_request("leagues", {"team": team_id})

            if not data:
                return None

            candidates = []
            for entry in data:
                league = entry.get("league", {})
                if league.get("type") != "League":
                    continue
                for season in entry.get("seasons", []):
                    if season.get("current"):
                        candidates.append({
                            "league_id": league.get("id"),
                            "league_name": league.get("name"),
                            "season": season.get("year"),
                            "country": entry.get("country", {}).get("name"),
                        })

            if not candidates:
                return None

            # Prefer the domestic league matching the team's own country
            # (avoids picking an international cup the team also plays in).
            match = next(
                (c for c in candidates if country and c.get("country") == country),
                candidates[0],
            )

            context = {
                "league_id": match["league_id"],
                "league_name": match["league_name"],
                "season": match["season"],
            }

            if self.cache_manager:
                await self.cache_manager.set(cache_key, context, ttl=86400)

            return context

        except Exception as e:
            logger.error(f"Error resolving league context for team {team_id}: {e}", exc_info=True)
            return None

    async def get_recent_fixtures(self, team_id: int, last: int = 5) -> List[Dict[str, Any]]:
        """Get a team's last N completed fixtures (real results)."""
        try:
            data = await self._make_request("fixtures", {"team": team_id, "last": last})
            if not data:
                return []

            fixtures = []
            for fx in data:
                home = fx.get("teams", {}).get("home", {})
                away = fx.get("teams", {}).get("away", {})
                goals = fx.get("goals", {})
                fixtures.append({
                    "date": fx.get("fixture", {}).get("date", ""),
                    "home_id": home.get("id"),
                    "home_name": home.get("name", "Local"),
                    "away_id": away.get("id"),
                    "away_name": away.get("name", "Visitante"),
                    "home_goals": goals.get("home") if goals.get("home") is not None else 0,
                    "away_goals": goals.get("away") if goals.get("away") is not None else 0,
                })
            return fixtures

        except Exception as e:
            logger.error(f"Error getting recent fixtures for team {team_id}: {e}", exc_info=True)
            return []

    async def get_recent_form(self, team_id: int, last: int = 5) -> TeamForm:
        """Fetch recent fixtures and derive real form from them."""
        fixtures = await self.get_recent_fixtures(team_id, last=last)
        return derive_form(team_id, fixtures)

    async def get_standing_for_team(
        self, league_id: int, season: int, team_id: int
    ) -> Optional[Dict[str, Any]]:
        """Look up a team's real row in the league standings table."""
        table = await self.get_league_table(league_id, season)
        for row in table:
            if row.get("team_id") == team_id:
                return row
        return None

    async def get_match_data(
        self,
        home_team: str,
        away_team: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get complete match data for analysis, built entirely from real
        API-Football responses (no fabricated placeholders).
        """
        try:
            logger.info(f"Fetching match data: {home_team} vs {away_team}")

            home_info = await self.get_team_info(home_team)
            away_info = await self.get_team_info(away_team)

            if not home_info or not away_info:
                logger.error("Could not find one or both teams")
                return None

            home_league = await self.resolve_league_context(home_info["id"], home_info.get("country"))
            away_league = await self.resolve_league_context(away_info["id"], away_info.get("country"))

            home_form = await self.get_recent_form(home_info["id"])
            away_form = await self.get_recent_form(away_info["id"])

            home_standing = None
            if home_league:
                home_standing = await self.get_standing_for_team(
                    home_league["league_id"], home_league["season"], home_info["id"]
                )
            away_standing = None
            if away_league:
                away_standing = await self.get_standing_for_team(
                    away_league["league_id"], away_league["season"], away_info["id"]
                )

            h2h = await self.get_head_to_head(home_info["id"], away_info["id"])

            home_season = home_league["season"] if home_league else self._current_season()
            away_season = away_league["season"] if away_league else self._current_season()
            home_injuries = await self.get_injuries(home_info["id"], home_season)
            away_injuries = await self.get_injuries(away_info["id"], away_season)

            match_data = build_match_data(
                home_ref=TeamRef(id=home_info["id"], name=home_info["name"], country=home_info.get("country")),
                away_ref=TeamRef(id=away_info["id"], name=away_info["name"], country=away_info.get("country")),
                league_name=home_league["league_name"] if home_league else None,
                home_form=home_form,
                away_form=away_form,
                h2h=h2h,
                home_injuries=home_injuries,
                away_injuries=away_injuries,
                home_standing=home_standing,
                away_standing=away_standing,
                stadium=home_info.get("venue_name"),
                source="api_football",
            )

            logger.info(f"Match data fetched successfully for {home_team} vs {away_team}")
            return match_data

        except Exception as e:
            logger.error(f"Error fetching match data: {e}", exc_info=True)
            return None

    async def get_head_to_head(self, home_team_id: int, away_team_id: int, last: int = 5) -> HeadToHead:
        """
        Get structured + formatted head-to-head history between two teams,
        including real BTTS/over-2.5 rates derived from those same matches.
        """
        try:
            data = await self._make_request(
                "fixtures/headtohead",
                {"h2h": f"{home_team_id}-{away_team_id}"}
            )

            if not data:
                return HeadToHead(matches=[], summary_text="Sin historial reciente")

            recent = data[:last]

            matches: List[FixtureResult] = []
            lines = []
            btts_count = 0
            over_2_5_count = 0

            for match in recent:
                home_goals = match.get("goals", {}).get("home") or 0
                away_goals = match.get("goals", {}).get("away") or 0
                home_name = match.get("teams", {}).get("home", {}).get("name", "Local")
                away_name = match.get("teams", {}).get("away", {}).get("name", "Visitante")
                match_home_id = match.get("teams", {}).get("home", {}).get("id")

                matches.append(FixtureResult(
                    date=match.get("fixture", {}).get("date", ""),
                    home_name=home_name,
                    away_name=away_name,
                    home_goals=home_goals,
                    away_goals=away_goals,
                    is_home_for_ref_team=(match_home_id == home_team_id),
                ))
                lines.append(f"{home_name} {home_goals}-{away_goals} {away_name}")

                if home_goals > 0 and away_goals > 0:
                    btts_count += 1
                if home_goals + away_goals > 2.5:
                    over_2_5_count += 1

            total = len(matches)
            btts_pct = round(100 * btts_count / total, 1) if total else None
            over_2_5_pct = round(100 * over_2_5_count / total, 1) if total else None

            return HeadToHead(
                matches=matches,
                summary_text="\n".join(lines) if lines else "Sin historial reciente",
                btts_pct=btts_pct,
                over_2_5_pct=over_2_5_pct,
            )

        except Exception as e:
            logger.error(f"Error getting head-to-head: {e}", exc_info=True)
            return HeadToHead(matches=[], summary_text="Error al cargar historial")

    async def get_injuries(self, team_id: int, season: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get current injuries for a team.

        Args:
            team_id: Team ID
            season: Season year (defaults to the current season)

        Returns:
            List of injury dictionaries
        """
        try:
            season = season if season is not None else self._current_season()

            data = await self._make_request(
                "injuries",
                {
                    "team": team_id,
                    "season": season
                }
            )

            if not data:
                return []

            injuries = []
            for injury_data in data[:5]:  # Top 5 injuries
                injury = injury_data.get("injury", {})
                player = injury_data.get("player", {})

                injuries.append({
                    "player": player.get("name", "Unknown"),
                    "position": player.get("position", ""),
                    "injury_type": injury.get("type", ""),
                    "reason": injury.get("reason", ""),
                    "date": injury_data.get("date", ""),
                    "is_key_player": self._is_key_player(player.get("name", "")),
                    "impact": self._assess_injury_impact(player.get("position", ""))
                })

            return injuries

        except Exception as e:
            logger.error(f"Error getting injuries for team {team_id}: {e}", exc_info=True)
            return []

    def _is_key_player(self, player_name: str) -> bool:
        """Determine if a player is a key player (simplified)."""
        # In production, this would use a database of key players
        key_players_keywords = ["messi", "ronaldo", "mbappé", "haaland", "de bruyne", "mbappe"]
        return any(keyword in player_name.lower() for keyword in key_players_keywords)

    def _assess_injury_impact(self, position: str) -> str:
        """Assess impact of injury based on position."""
        key_positions = ["Goalkeeper", "Center-Back", "Striker", "Attacking Midfielder"]

        if any(pos in position for pos in key_positions):
            return "Alto"
        else:
            return "Medio"

    async def get_live_matches(self, league_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get live matches (for real-time tracking).

        Args:
            league_id: Optional league ID filter

        Returns:
            List of live matches
        """
        try:
            params = {"live": "all"}
            if league_id:
                params["league"] = league_id

            data = await self._make_request("fixtures", params)

            if not data:
                return []

            matches = []
            for fixture in data:
                match = {
                    "fixture_id": fixture.get("fixture", {}).get("id"),
                    "home_team": fixture.get("teams", {}).get("home", {}).get("name"),
                    "away_team": fixture.get("teams", {}).get("away", {}).get("name"),
                    "score": fixture.get("goals", {}),
                    "minute": fixture.get("fixture", {}).get("status", {}).get("elapsed", 0),
                    "status": fixture.get("fixture", {}).get("status", {}).get("short"),
                }
                matches.append(match)

            return matches

        except Exception as e:
            logger.error(f"Error getting live matches: {e}", exc_info=True)
            return []

    async def get_league_table(self, league_id: int, season: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get league standings.

        Args:
            league_id: League ID
            season: Season year (defaults to the current season)

        Returns:
            List of teams with standings
        """
        try:
            season = season if season is not None else self._current_season()

            data = await self._make_request(
                "standings",
                {"league": league_id, "season": season}
            )

            if not data:
                return []

            standings = []
            for team_data in data[0].get("league", {}).get("standings", [{}])[0].get("all", []):
                team = team_data.get("team", {})
                standings.append({
                    "position": team_data.get("rank"),
                    "team_id": team.get("id"),
                    "team_name": team.get("name"),
                    "points": team_data.get("points"),
                    "played": team_data.get("all", {}).get("played", 0),
                    "won": team_data.get("all", {}).get("win", 0),
                    "drawn": team_data.get("all", {}).get("draw", 0),
                    "lost": team_data.get("all", {}).get("lose", 0),
                    "goals_for": team_data.get("all", {}).get("goals", {}).get("for", 0),
                    "goals_against": team_data.get("all", {}).get("goals", {}).get("against", 0),
                })

            return standings

        except Exception as e:
            logger.error(f"Error getting league table: {e}", exc_info=True)
            return []

    async def health_check(self) -> bool:
        """
        Check if API-Football is accessible.

        Returns:
            True if API is working, False otherwise
        """
        try:
            data = await self._make_request("status")
            return data is not None
        except Exception as e:
            logger.error(f"API-Football health check failed: {e}")
            return False
