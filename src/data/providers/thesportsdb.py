"""
TheSportsDB provider (https://www.thesportsdb.com/).
Free tier: requires a personal API key from a free account (no cost). Only
the last 5 events per team are available for free, so form/h2h coverage
here is shallow by design - it's a fallback, not a replacement for
API-Football.

Used by MatchAnalyzer only as a fallback when API-Football can't find one of
the two teams (see src/analyzer/match_analyzer.py).
"""
from typing import Any, Dict, List, Optional
import logging

import aiohttp

from config.settings import settings
from src.data.providers.base import FixtureResult, HeadToHead, TeamForm, TeamRef, derive_form

logger = logging.getLogger(__name__)


class TheSportsDbProvider:
    """Fallback data source backed by TheSportsDB's free tier."""

    def __init__(self, cache_manager=None):
        self.api_key = settings.thesportsdb_api_key
        self.base_url = f"https://www.thesportsdb.com/api/v1/json/{self.api_key}"
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache_manager = cache_manager
        # Populated by find_team - league id/name are returned directly by
        # the team search, no extra request needed.
        self._team_league_cache: Dict[int, Dict[str, Any]] = {}

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
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
                logger.error(f"TheSportsDB error: {response.status}")
                return None
        except Exception as e:
            logger.error(f"Error making request to TheSportsDB {path}: {e}", exc_info=True)
            return None

    def _current_season(self) -> int:
        from datetime import datetime
        now = datetime.now()
        return now.year if now.month >= 8 else now.year - 1

    async def find_team(self, name: str) -> Optional[TeamRef]:
        cache_key = f"tsdb_team:{name.lower()}"
        if self.cache_manager:
            cached = await self.cache_manager.get(cache_key)
            if cached:
                team_id = cached["id"]
                self._team_league_cache[team_id] = cached.get("league_context")
                return TeamRef(id=team_id, name=cached["name"], country=cached.get("country"))

        data = await self._make_request("searchteams.php", {"t": name})
        teams = (data or {}).get("teams") or []
        if not teams:
            return None

        team = teams[0]
        try:
            team_id = int(team.get("idTeam"))
        except (TypeError, ValueError):
            return None

        league_context = None
        if team.get("idLeague") and team.get("strLeague"):
            league_context = {
                "league_id": team.get("idLeague"),
                "league_name": team.get("strLeague"),
                "season": self._current_season(),
            }
        self._team_league_cache[team_id] = league_context

        if self.cache_manager:
            await self.cache_manager.set(cache_key, {
                "id": team_id,
                "name": team.get("strTeam"),
                "country": team.get("strCountry"),
                "league_context": league_context,
            }, ttl=86400)

        return TeamRef(id=team_id, name=team.get("strTeam"), country=team.get("strCountry"))

    async def get_league_context(self, team_id: int, country: Optional[str] = None) -> Optional[Dict[str, Any]]:
        return self._team_league_cache.get(team_id)

    async def _get_last_events(self, team_id: int) -> List[Dict[str, Any]]:
        """TheSportsDB's free eventslast endpoint always returns (at most)
        the last 5 events - there's no `last` parameter to request more."""
        data = await self._make_request("eventslast.php", {"id": team_id})
        return (data or {}).get("results") or []

    def _to_generic_fixture(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            home_id = int(event.get("idHomeTeam"))
            away_id = int(event.get("idAwayTeam"))
        except (TypeError, ValueError):
            return None
        return {
            "date": event.get("dateEvent", ""),
            "home_id": home_id,
            "home_name": event.get("strHomeTeam", "Local"),
            "away_id": away_id,
            "away_name": event.get("strAwayTeam", "Visitante"),
            "home_goals": int(event.get("intHomeScore") or 0),
            "away_goals": int(event.get("intAwayScore") or 0),
        }

    async def get_recent_form(self, team_id: int, last: int = 5) -> TeamForm:
        events = await self._get_last_events(team_id)
        fixtures = [f for f in (self._to_generic_fixture(e) for e in events[:last]) if f is not None]
        return derive_form(team_id, fixtures)

    async def get_head_to_head(self, home_id: int, away_id: int, last: int = 5) -> HeadToHead:
        """Best-effort only: filtered from the home team's last 5 events,
        since TheSportsDB's free tier has no dedicated h2h-by-pair endpoint
        and no way to fetch a deeper match history for free."""
        events = await self._get_last_events(home_id)
        fixtures = [f for f in (self._to_generic_fixture(e) for e in events) if f is not None]

        h2h_fixtures = [f for f in fixtures if away_id in (f["home_id"], f["away_id"])][:last]

        if not h2h_fixtures:
            return HeadToHead(matches=[], summary_text="Sin historial reciente")

        results: List[FixtureResult] = []
        lines = []
        btts_count = over_2_5_count = 0

        for fx in h2h_fixtures:
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

        total = len(h2h_fixtures)
        return HeadToHead(
            matches=results,
            summary_text="\n".join(lines),
            btts_pct=round(100 * btts_count / total, 1),
            over_2_5_pct=round(100 * over_2_5_count / total, 1),
        )

    async def get_injuries(self, team_id: int, season: int) -> List[Dict[str, Any]]:
        """Not available on TheSportsDB's free tier - honestly empty,
        never fabricated."""
        return []
