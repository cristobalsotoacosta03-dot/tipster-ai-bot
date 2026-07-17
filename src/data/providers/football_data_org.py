"""
football-data.org provider (https://www.football-data.org/).
Free tier: requires a personal API key from a free account (X-Auth-Token
header), no cost. The free plan only covers ~12 top competitions and has no
team-name-search endpoint, so team lookup is done by listing each free
competition's teams and matching by name - real data, just scoped to what
the free plan actually exposes.

Used by MatchAnalyzer only as a fallback when API-Football can't find one of
the two teams (see src/analyzer/match_analyzer.py).
"""
from typing import Any, Dict, List, Optional
import logging

import aiohttp

from config.settings import settings
from src.data.providers.base import FixtureResult, HeadToHead, TeamForm, TeamRef, derive_form

logger = logging.getLogger(__name__)

# Competitions included in football-data.org's free tier. This list is
# stable but not guaranteed forever - if it changes, find_team will simply
# fail to find teams outside it (degrades to "not found", never fabricates).
FREE_COMPETITIONS = [
    "PL", "ELC", "PD", "SA", "BL1", "FL1",
    "DED", "PPL", "BSA", "CL", "EC", "WC",
]


class FootballDataOrgProvider:
    """Fallback data source backed by football-data.org's free tier."""

    def __init__(self, cache_manager=None):
        self.api_key = settings.football_data_org_key
        self.base_url = "https://api.football-data.org/v4"
        self.headers = {"X-Auth-Token": self.api_key or ""}
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache_manager = cache_manager
        # Populated by find_team - lets get_league_context answer without
        # another request for teams found in this process's lifetime.
        self._team_league_cache: Dict[int, Dict[str, Any]] = {}

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session

    async def close(self) -> None:
        if self.session and not self.session.closed:
            await self.session.close()

    async def _make_request(self, path: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/{path}", params=params) as response:
                if response.status == 200:
                    return await response.json()
                if response.status == 429:
                    logger.warning("Rate limit exceeded for football-data.org")
                    return None
                logger.error(f"football-data.org error: {response.status}")
                return None
        except Exception as e:
            logger.error(f"Error making request to football-data.org {path}: {e}", exc_info=True)
            return None

    async def _get_competition_teams(self, code: str) -> Dict[str, Any]:
        """Returns {"competition_name": str, "season_year": int|None, "teams": [...]}."""
        cache_key = f"fdo_teams:{code}"
        if self.cache_manager:
            cached = await self.cache_manager.get(cache_key)
            if cached is not None:
                return cached

        data = await self._make_request(f"competitions/{code}/teams")
        if not data:
            return {"competition_name": code, "season_year": None, "teams": []}

        season_start = (data.get("season") or {}).get("startDate", "")
        result = {
            "competition_name": (data.get("competition") or {}).get("name", code),
            "season_year": int(season_start[:4]) if season_start[:4].isdigit() else None,
            "teams": data.get("teams", []),
        }

        if self.cache_manager and result["teams"]:
            await self.cache_manager.set(cache_key, result, ttl=86400)

        return result

    async def find_team(self, name: str) -> Optional[TeamRef]:
        """Search for a team by name across the free tier's competitions.
        No dedicated search endpoint exists on the free plan, so this scans
        each competition's roster (cached 24h) and matches by name."""
        needle = name.strip().lower()

        for code in FREE_COMPETITIONS:
            comp = await self._get_competition_teams(code)
            for team in comp["teams"]:
                team_name = (team.get("name") or "").lower()
                short_name = (team.get("shortName") or "").lower()
                if needle == team_name or needle == short_name or needle in team_name:
                    team_id = team.get("id")
                    self._team_league_cache[team_id] = {
                        "league_id": code,
                        "league_name": comp["competition_name"],
                        "season": comp["season_year"],
                    }
                    return TeamRef(
                        id=team_id,
                        name=team.get("name"),
                        country=team.get("area", {}).get("name"),
                    )
        return None

    async def get_league_context(self, team_id: int, country: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Only known for teams already resolved via find_team in this
        process (football-data.org's free tier has no direct
        "team's current league" lookup)."""
        return self._team_league_cache.get(team_id)

    async def _get_finished_matches(self, team_id: int, limit: int) -> List[Dict[str, Any]]:
        data = await self._make_request(
            f"teams/{team_id}/matches", {"status": "FINISHED", "limit": limit}
        )
        return data.get("matches", []) if data else []

    def _to_generic_fixture(self, match: Dict[str, Any]) -> Dict[str, Any]:
        score = match.get("score", {}).get("fullTime", {})
        return {
            "date": match.get("utcDate", ""),
            "home_id": match.get("homeTeam", {}).get("id"),
            "home_name": match.get("homeTeam", {}).get("name", "Local"),
            "away_id": match.get("awayTeam", {}).get("id"),
            "away_name": match.get("awayTeam", {}).get("name", "Visitante"),
            "home_goals": score.get("home") if score.get("home") is not None else 0,
            "away_goals": score.get("away") if score.get("away") is not None else 0,
        }

    async def get_recent_form(self, team_id: int, last: int = 5) -> TeamForm:
        matches = await self._get_finished_matches(team_id, last)
        fixtures = [self._to_generic_fixture(m) for m in matches]
        return derive_form(team_id, fixtures)

    async def get_head_to_head(self, home_id: int, away_id: int, last: int = 5) -> HeadToHead:
        """No direct h2h-by-team-pair endpoint on the free tier - filter the
        home team's recent finished matches for the away team as opponent."""
        matches = await self._get_finished_matches(home_id, 50)

        h2h_matches = [
            m for m in matches
            if away_id in (m.get("homeTeam", {}).get("id"), m.get("awayTeam", {}).get("id"))
        ][:last]

        if not h2h_matches:
            return HeadToHead(matches=[], summary_text="Sin historial reciente")

        results: List[FixtureResult] = []
        lines = []
        btts_count = over_2_5_count = 0

        for match in h2h_matches:
            fx = self._to_generic_fixture(match)
            results.append(FixtureResult(
                date=fx["date"],
                home_name=fx["home_name"],
                away_name=fx["away_name"],
                home_goals=fx["home_goals"],
                away_goals=fx["away_goals"],
                is_home_for_ref_team=(fx["home_id"] == home_id),
            ))
            lines.append(f"{fx['home_name']} {fx['home_goals']}-{fx['away_goals']} {fx['away_name']}")
            if fx["home_goals"] > 0 and fx["away_goals"] > 0:
                btts_count += 1
            if fx["home_goals"] + fx["away_goals"] > 2.5:
                over_2_5_count += 1

        total = len(h2h_matches)
        return HeadToHead(
            matches=results,
            summary_text="\n".join(lines),
            btts_pct=round(100 * btts_count / total, 1),
            over_2_5_pct=round(100 * over_2_5_count / total, 1),
        )

    async def get_injuries(self, team_id: int, season: int) -> List[Dict[str, Any]]:
        """Not available on football-data.org's free tier - honestly empty,
        never fabricated."""
        return []
