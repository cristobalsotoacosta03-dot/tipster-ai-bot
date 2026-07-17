"""
Tests for the football-data.org fallback provider.
All HTTP calls are mocked - no real network requests, no API key required.
"""
from unittest.mock import AsyncMock
import pytest

from src.data.providers.football_data_org import FootballDataOrgProvider


class TestFootballDataOrgProvider:

    @pytest.fixture
    def provider(self):
        return FootballDataOrgProvider()

    @pytest.mark.asyncio
    async def test_find_team_scans_free_competitions_and_matches_by_name(self, provider):
        async def fake_get_competition_teams(code):
            if code == "PD":
                return {
                    "competition_name": "Primera Division",
                    "season_year": 2025,
                    "teams": [
                        {"id": 86, "name": "Real Madrid CF", "shortName": "Real Madrid", "area": {"name": "Spain"}},
                    ],
                }
            return {"competition_name": code, "season_year": None, "teams": []}

        provider._get_competition_teams = fake_get_competition_teams

        ref = await provider.find_team("Real Madrid")

        assert ref is not None
        assert ref.id == 86
        assert ref.name == "Real Madrid CF"
        assert ref.country == "Spain"

        league = await provider.get_league_context(86)
        assert league == {"league_id": "PD", "league_name": "Primera Division", "season": 2025}

    @pytest.mark.asyncio
    async def test_find_team_not_found_returns_none(self, provider):
        provider._get_competition_teams = AsyncMock(return_value={"competition_name": "x", "season_year": None, "teams": []})
        ref = await provider.find_team("Nonexistent FC")
        assert ref is None

    @pytest.mark.asyncio
    async def test_get_recent_form_derives_from_finished_matches(self, provider):
        provider._get_finished_matches = AsyncMock(return_value=[
            {
                "utcDate": "2025-01-01T20:00:00Z",
                "homeTeam": {"id": 86, "name": "Real Madrid CF"},
                "awayTeam": {"id": 81, "name": "FC Barcelona"},
                "score": {"fullTime": {"home": 2, "away": 1}},
            },
            {
                "utcDate": "2025-01-08T20:00:00Z",
                "homeTeam": {"id": 90, "name": "Other FC"},
                "awayTeam": {"id": 86, "name": "Real Madrid CF"},
                "score": {"fullTime": {"home": 0, "away": 0}},
            },
        ])

        form = await provider.get_recent_form(86)

        assert form.form_string == "WD"
        assert form.wins == 1
        assert form.draws == 1
        assert form.goals_for == 2  # 2 (home win) + 0 (away draw)
        assert form.goals_against == 1

    @pytest.mark.asyncio
    async def test_get_head_to_head_filters_by_opponent(self, provider):
        provider._get_finished_matches = AsyncMock(return_value=[
            {
                "utcDate": "2025-01-01T20:00:00Z",
                "homeTeam": {"id": 86, "name": "Real Madrid CF"},
                "awayTeam": {"id": 81, "name": "FC Barcelona"},
                "score": {"fullTime": {"home": 2, "away": 1}},
            },
            {
                "utcDate": "2025-01-08T20:00:00Z",
                "homeTeam": {"id": 86, "name": "Real Madrid CF"},
                "awayTeam": {"id": 999, "name": "Unrelated FC"},
                "score": {"fullTime": {"home": 3, "away": 0}},
            },
        ])

        h2h = await provider.get_head_to_head(86, 81)

        assert len(h2h.matches) == 1
        assert "Barcelona" in h2h.summary_text

    @pytest.mark.asyncio
    async def test_get_head_to_head_no_matches(self, provider):
        provider._get_finished_matches = AsyncMock(return_value=[])
        h2h = await provider.get_head_to_head(86, 81)
        assert h2h.matches == []
        assert h2h.summary_text == "Sin historial reciente"

    @pytest.mark.asyncio
    async def test_get_injuries_not_supported(self, provider):
        """football-data.org's free tier has no injury data - must return
        an honest empty list, never a fabricated one."""
        injuries = await provider.get_injuries(86, 2025)
        assert injuries == []
