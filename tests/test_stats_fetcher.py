"""
Tests for StatsFetcher.
All API-Football calls are mocked via `_make_request` - no real network
requests, so these run without an API key and don't touch the free quota.
"""
from unittest.mock import AsyncMock
import pytest

from src.data.stats_fetcher import StatsFetcher
from src.data.providers.base import derive_form


class TestStatsFetcher:
    """Test suite for StatsFetcher."""

    @pytest.fixture
    def fetcher(self):
        return StatsFetcher()

    # ==================== LEAGUE/SEASON RESOLUTION ====================

    @pytest.mark.asyncio
    async def test_resolve_league_context_picks_active_domestic_league(self, fetcher):
        """Should pick the current-season domestic league matching the
        team's country, not assume a fixed league (previous hardcoded bug)."""
        fetcher._make_request = AsyncMock(return_value=[
            {
                "league": {"id": 2, "name": "Champions League", "type": "Cup"},
                "country": {"name": "World"},
                "seasons": [{"year": 2025, "current": True}],
            },
            {
                "league": {"id": 140, "name": "La Liga", "type": "League"},
                "country": {"name": "Spain"},
                "seasons": [{"year": 2025, "current": True}],
            },
        ])

        context = await fetcher.resolve_league_context(541, country="Spain")

        assert context == {"league_id": 140, "league_name": "La Liga", "season": 2025}

    @pytest.mark.asyncio
    async def test_resolve_league_context_returns_none_on_api_failure(self, fetcher):
        """No fallback to a guessed league - None means 'unknown', not Premier League."""
        fetcher._make_request = AsyncMock(return_value=None)
        context = await fetcher.resolve_league_context(541, country="Spain")
        assert context is None

    def test_current_season_dynamic(self, fetcher):
        """Season must be derived from today's date, never hardcoded 2024."""
        import datetime
        expected = datetime.datetime.now().year if datetime.datetime.now().month >= 8 else datetime.datetime.now().year - 1
        assert fetcher._current_season() == expected

    # ==================== FORM DERIVATION ====================

    def test_derive_form_from_fixtures(self, fetcher):
        team_id = 1
        fixtures = [
            {"date": "2025-01-01T20:00:00+00:00", "home_id": 1, "home_name": "A", "away_id": 2, "away_name": "B", "home_goals": 2, "away_goals": 0},
            {"date": "2025-01-08T20:00:00+00:00", "home_id": 3, "home_name": "C", "away_id": 1, "away_name": "A", "home_goals": 1, "away_goals": 1},
            {"date": "2025-01-15T20:00:00+00:00", "home_id": 1, "home_name": "A", "away_id": 4, "away_name": "D", "home_goals": 0, "away_goals": 2},
        ]

        form = derive_form(team_id, fixtures)

        assert form.form_string == "WDL"
        assert form.wins == 1
        assert form.draws == 1
        assert form.losses == 1
        assert form.goals_for == 3  # 2 + 1 + 0
        assert form.goals_against == 3  # 0 + 1 + 2
        assert form.played == 3

    @pytest.mark.asyncio
    async def test_get_recent_form_no_fixtures(self, fetcher):
        fetcher._make_request = AsyncMock(return_value=None)
        form = await fetcher.get_recent_form(1)
        assert form.played == 0
        assert form.form_string == ""

    # ==================== HEAD TO HEAD ====================

    @pytest.mark.asyncio
    async def test_get_head_to_head_structured(self, fetcher):
        fetcher._make_request = AsyncMock(return_value=[
            {
                "fixture": {"date": "2025-01-01T20:00:00+00:00"},
                "teams": {"home": {"id": 1, "name": "A"}, "away": {"id": 2, "name": "B"}},
                "goals": {"home": 2, "away": 1},
            },
            {
                "fixture": {"date": "2024-06-01T20:00:00+00:00"},
                "teams": {"home": {"id": 2, "name": "B"}, "away": {"id": 1, "name": "A"}},
                "goals": {"home": 0, "away": 0},
            },
        ])

        h2h = await fetcher.get_head_to_head(1, 2)

        assert len(h2h.matches) == 2
        assert h2h.btts_pct == 50.0  # only the 2-1 match has both teams scoring
        assert h2h.over_2_5_pct == 50.0  # only the 2-1 match totals > 2.5
        assert "A 2-1 B" in h2h.summary_text

    @pytest.mark.asyncio
    async def test_get_head_to_head_no_history(self, fetcher):
        fetcher._make_request = AsyncMock(return_value=None)
        h2h = await fetcher.get_head_to_head(1, 2)
        assert h2h.matches == []
        assert h2h.summary_text == "Sin historial reciente"
        assert h2h.btts_pct is None

    # ==================== TEAM INFO / TYPO CORRECTION ====================

    @pytest.mark.asyncio
    async def test_get_team_info_retries_with_corrected_typo(self, fetcher):
        """A misspelled well-known team should be retried with the
        corrected name instead of failing outright."""
        calls = []

        async def fake_request(endpoint, params=None):
            calls.append(params["search"])
            if params["search"] == "Real Madrid":
                return [{"team": {"id": 541, "name": "Real Madrid", "country": "Spain"}}]
            return []

        fetcher._make_request = AsyncMock(side_effect=fake_request)
        info = await fetcher.get_team_info("Real Madrd")

        assert calls == ["Real Madrd", "Real Madrid"]
        assert info["name"] == "Real Madrid"

    @pytest.mark.asyncio
    async def test_get_team_info_no_retry_when_found_first_try(self, fetcher):
        fetcher._make_request = AsyncMock(
            return_value=[{"team": {"id": 529, "name": "Barcelona", "country": "Spain"}}]
        )
        info = await fetcher.get_team_info("Barcelona")

        fetcher._make_request.assert_awaited_once()
        assert info["name"] == "Barcelona"

    @pytest.mark.asyncio
    async def test_get_team_info_unrelated_name_stays_not_found(self, fetcher):
        fetcher._make_request = AsyncMock(return_value=[])
        info = await fetcher.get_team_info("xyzqwerty123")

        assert info is None
        # No known-team is close enough, so it should not retry with a guess.
        fetcher._make_request.assert_awaited_once()

    # ==================== LEAGUE STANDINGS ====================

    @pytest.mark.asyncio
    async def test_get_league_table_parses_real_api_shape(self, fetcher):
        """Regression test: standings[0] is the list of teams directly
        (API-Football's real shape). A previous extra `.get("all", [])`
        here made every real call raise AttributeError, silently caught
        and returning [] - standings were always empty in production."""
        fetcher._make_request = AsyncMock(return_value=[{
            "league": {
                "standings": [[
                    {
                        "rank": 1,
                        "team": {"id": 541, "name": "Real Madrid"},
                        "points": 70,
                        "all": {"played": 30, "win": 22, "draw": 4, "lose": 4,
                                 "goals": {"for": 60, "against": 25}},
                    },
                ]]
            }
        }])

        table = await fetcher.get_league_table(140, 2025)

        assert len(table) == 1
        assert table[0]["team_name"] == "Real Madrid"
        assert table[0]["played"] == 30
        assert table[0]["won"] == 22
        assert table[0]["goals_for"] == 60

    @pytest.mark.asyncio
    async def test_get_league_table_empty_on_no_data(self, fetcher):
        fetcher._make_request = AsyncMock(return_value=None)
        assert await fetcher.get_league_table(140, 2025) == []

    # ==================== MATCH DATA ====================

    @pytest.mark.asyncio
    async def test_get_match_data_team_not_found(self, fetcher):
        fetcher.get_team_info = AsyncMock(return_value=None)
        result = await fetcher.get_match_data("Nonexistent FC", "Barcelona")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_match_data_no_invented_placeholders(self, fetcher):
        """The old hardcoded league_id=39/season=2024 and fabricated fields
        (formation, referee, weather, motivation) must not appear."""
        async def fake_team_info(name):
            return {"id": 1, "name": name, "country": "Spain", "venue_name": "Stadium"} if name == "Real Madrid" \
                else {"id": 2, "name": name, "country": "Spain", "venue_name": "Stadium 2"}

        fetcher.get_team_info = AsyncMock(side_effect=fake_team_info)
        fetcher.resolve_league_context = AsyncMock(return_value=None)
        fetcher.get_recent_form = AsyncMock(return_value=derive_form(1, []))
        fetcher.get_standing_for_team = AsyncMock(return_value=None)
        fetcher._make_request = AsyncMock(return_value=None)
        fetcher.get_injuries = AsyncMock(return_value=[])

        from src.data.providers.base import HeadToHead
        fetcher.get_head_to_head = AsyncMock(return_value=HeadToHead(matches=[], summary_text="Sin historial reciente"))

        match_data = await fetcher.get_match_data("Real Madrid", "Barcelona")

        assert match_data is not None
        assert match_data["league_name"] is None  # unresolved, not fabricated "Premier League"
        for forbidden_key in (
            "matchday", "referee", "home_formation", "away_formation",
            "weather", "home_motivation", "away_motivation", "home_xg", "home_ppda",
        ):
            assert forbidden_key not in match_data
