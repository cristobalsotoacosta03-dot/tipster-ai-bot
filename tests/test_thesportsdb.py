"""
Tests for the TheSportsDB fallback provider.
All HTTP calls are mocked - no real network requests, no API key required.
"""
from unittest.mock import AsyncMock
import pytest

from src.data.providers.thesportsdb import TheSportsDbProvider


class TestTheSportsDbProvider:

    @pytest.fixture
    def provider(self):
        return TheSportsDbProvider()

    @pytest.mark.asyncio
    async def test_find_team_success(self, provider):
        provider._make_request = AsyncMock(return_value={
            "teams": [{
                "idTeam": "133602",
                "strTeam": "Arsenal",
                "strCountry": "England",
                "idLeague": "4328",
                "strLeague": "English Premier League",
            }]
        })

        ref = await provider.find_team("Arsenal")

        assert ref is not None
        assert ref.id == 133602
        assert ref.name == "Arsenal"
        assert ref.country == "England"

        league = await provider.get_league_context(133602)
        assert league["league_id"] == "4328"
        assert league["league_name"] == "English Premier League"

    @pytest.mark.asyncio
    async def test_find_team_not_found_returns_none(self, provider):
        provider._make_request = AsyncMock(return_value={"teams": None})
        ref = await provider.find_team("Nonexistent FC")
        assert ref is None

    @pytest.mark.asyncio
    async def test_get_recent_form_from_last_events(self, provider):
        provider._make_request = AsyncMock(return_value={
            "results": [
                {
                    "dateEvent": "2025-01-01",
                    "idHomeTeam": "133602", "strHomeTeam": "Arsenal",
                    "idAwayTeam": "133615", "strAwayTeam": "Chelsea",
                    "intHomeScore": "3", "intAwayScore": "1",
                },
                {
                    "dateEvent": "2025-01-08",
                    "idHomeTeam": "133616", "strHomeTeam": "Liverpool",
                    "idAwayTeam": "133602", "strAwayTeam": "Arsenal",
                    "intHomeScore": "2", "intAwayScore": "2",
                },
            ]
        })

        form = await provider.get_recent_form(133602)

        assert form.form_string == "WD"
        assert form.goals_for == 5  # 3 + 2
        assert form.goals_against == 3  # 1 + 2

    @pytest.mark.asyncio
    async def test_get_head_to_head_filters_by_opponent(self, provider):
        provider._make_request = AsyncMock(return_value={
            "results": [
                {
                    "dateEvent": "2025-01-01",
                    "idHomeTeam": "133602", "strHomeTeam": "Arsenal",
                    "idAwayTeam": "133615", "strAwayTeam": "Chelsea",
                    "intHomeScore": "3", "intAwayScore": "1",
                },
                {
                    "dateEvent": "2025-01-08",
                    "idHomeTeam": "133602", "strHomeTeam": "Arsenal",
                    "idAwayTeam": "999999", "strAwayTeam": "Unrelated FC",
                    "intHomeScore": "0", "intAwayScore": "0",
                },
            ]
        })

        h2h = await provider.get_head_to_head(133602, 133615)

        assert len(h2h.matches) == 1
        assert "Chelsea" in h2h.summary_text

    @pytest.mark.asyncio
    async def test_get_head_to_head_no_matches(self, provider):
        provider._make_request = AsyncMock(return_value={"results": []})
        h2h = await provider.get_head_to_head(133602, 133615)
        assert h2h.matches == []
        assert h2h.summary_text == "Sin historial reciente"

    @pytest.mark.asyncio
    async def test_get_injuries_not_supported(self, provider):
        """TheSportsDB's free tier has no injury data - must return an
        honest empty list, never a fabricated one."""
        injuries = await provider.get_injuries(133602, 2025)
        assert injuries == []
