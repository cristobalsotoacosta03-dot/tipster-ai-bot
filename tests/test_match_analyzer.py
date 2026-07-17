"""
Tests for MatchAnalyzer.
All sub-components (stats fetcher, prompt engine, Claude client, cache) are
mocked - no real network calls, no API keys required.
"""
from datetime import datetime
from unittest.mock import AsyncMock
import pytest

from src.analyzer.match_analyzer import MatchAnalyzer


class TestMatchAnalyzer:
    """Test suite for MatchAnalyzer."""

    @pytest.fixture
    def analyzer(self):
        analyzer = MatchAnalyzer()
        analyzer.cache_manager.get_cached_analysis = AsyncMock(return_value=None)
        analyzer.cache_manager.cache_analysis = AsyncMock(return_value=True)
        analyzer.stats_fetcher.get_match_data = AsyncMock(return_value={
            "home_team": "Real Madrid",
            "away_team": "Barcelona",
            "home_avg_goals_for": 2.0,
            "away_avg_goals_for": 1.0,
            "home_rest_days": 7,
            "away_rest_days": 5,
            "home_injuries": [],
            "away_injuries": [],
            "h2h_structured": {"matches": [], "summary_text": "Sin historial reciente", "btts_pct": None, "over_2_5_pct": None},
        })
        analyzer.claude_client.analyze_match = AsyncMock(return_value="Análisis generado por Claude.")
        return analyzer

    @pytest.mark.asyncio
    async def test_analyze_match_full_pipeline(self, analyzer):
        """Cache miss -> fetch data -> build prompt -> call Claude -> cache result."""
        result = await analyzer.analyze_match("Real Madrid", "Barcelona", analysis_type="full")

        assert result is not None
        assert result["home_team"] == "Real Madrid"
        assert result["away_team"] == "Barcelona"
        assert result["analysis"] == "Análisis generado por Claude."
        assert result["from_cache"] is False
        assert 1 <= result["stake"] <= 5
        assert 0 <= result["confidence_level"] <= 100

        # Timestamp must be a real, parseable ISO datetime (fixes the old
        # logging.Formatter().formatTime(LogRecord(...)) hack).
        datetime.fromisoformat(result["timestamp"])

        analyzer.stats_fetcher.get_match_data.assert_awaited_once_with("Real Madrid", "Barcelona")
        analyzer.claude_client.analyze_match.assert_awaited_once()
        analyzer.cache_manager.cache_analysis.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_analyze_match_cache_hit_skips_pipeline(self, analyzer):
        """A cache hit must short-circuit and not touch stats/Claude at all."""
        analyzer.cache_manager.get_cached_analysis = AsyncMock(return_value={
            "home_team": "Real Madrid",
            "away_team": "Barcelona",
            "analysis": "cached",
        })

        result = await analyzer.analyze_match("Real Madrid", "Barcelona")

        assert result["from_cache"] is True
        analyzer.stats_fetcher.get_match_data.assert_not_awaited()
        analyzer.claude_client.analyze_match.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_analyze_match_returns_none_when_data_fetch_fails(self, analyzer):
        """Team not found / API failure must return None, not raise."""
        analyzer.stats_fetcher.get_match_data = AsyncMock(return_value=None)

        result = await analyzer.analyze_match("Unknown FC", "Barcelona")

        assert result is None
        analyzer.claude_client.analyze_match.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_analyze_match_returns_none_when_claude_fails(self, analyzer):
        """Claude disabled/rate-limited/etc. must return None, not raise or
        fabricate a fallback analysis."""
        analyzer.claude_client.analyze_match = AsyncMock(return_value=None)

        result = await analyzer.analyze_match("Real Madrid", "Barcelona")

        assert result is None

    @pytest.mark.asyncio
    async def test_express_and_premium_analysis_types_use_their_own_prompt(self, analyzer):
        for analysis_type in ("express", "premium", "full"):
            result = await analyzer.analyze_match("Real Madrid", "Barcelona", analysis_type=analysis_type)
            assert result["analysis_type"] == analysis_type


class TestMatchAnalyzerFallbackProviders:
    """MatchAnalyzer must only try fallback data sources when API-Football
    itself can't resolve both teams, and must use them transparently."""

    @pytest.fixture
    def analyzer(self):
        analyzer = MatchAnalyzer()
        analyzer.cache_manager.get_cached_analysis = AsyncMock(return_value=None)
        analyzer.cache_manager.cache_analysis = AsyncMock(return_value=True)
        analyzer.claude_client.analyze_match = AsyncMock(return_value="Análisis generado por Claude.")
        return analyzer

    def _fake_provider(self, found: bool):
        from src.data.providers.base import HeadToHead, TeamForm, TeamRef

        provider = AsyncMock()
        if found:
            provider.find_team = AsyncMock(side_effect=[
                TeamRef(id=1, name="Real Madrid", country="Spain"),
                TeamRef(id=2, name="Barcelona", country="Spain"),
            ])
        else:
            provider.find_team = AsyncMock(return_value=None)
        provider.get_league_context = AsyncMock(return_value=None)
        provider.get_recent_form = AsyncMock(return_value=TeamForm(
            form_string="WWD", played=3, wins=2, draws=1, losses=0,
            goals_for=6, goals_against=2, avg_goals_for=2.0, avg_goals_against=0.67,
        ))
        provider.get_head_to_head = AsyncMock(return_value=HeadToHead(matches=[], summary_text="Sin historial reciente"))
        provider.get_injuries = AsyncMock(return_value=[])
        return provider

    @pytest.mark.asyncio
    async def test_primary_success_never_touches_fallbacks(self, analyzer):
        analyzer.stats_fetcher.get_match_data = AsyncMock(return_value={
            "home_team": "Real Madrid", "away_team": "Barcelona",
            "home_injuries": [], "away_injuries": [],
            "h2h_structured": {"matches": [], "summary_text": "x", "btts_pct": None, "over_2_5_pct": None},
        })
        fallback = self._fake_provider(found=True)
        analyzer.fallback_providers = [fallback]

        result = await analyzer.analyze_match("Real Madrid", "Barcelona")

        assert result is not None
        fallback.find_team.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_falls_back_when_primary_cannot_find_teams(self, analyzer):
        analyzer.stats_fetcher.get_match_data = AsyncMock(return_value=None)
        fallback = self._fake_provider(found=True)
        analyzer.fallback_providers = [fallback]

        result = await analyzer.analyze_match("Real Madrid", "Barcelona")

        assert result is not None
        assert result["home_team"] == "Real Madrid"
        assert result["match_data"]["data_source"] == "AsyncMock"

    @pytest.mark.asyncio
    async def test_tries_next_fallback_when_first_fails(self, analyzer):
        analyzer.stats_fetcher.get_match_data = AsyncMock(return_value=None)
        failing = self._fake_provider(found=False)
        working = self._fake_provider(found=True)
        analyzer.fallback_providers = [failing, working]

        result = await analyzer.analyze_match("Real Madrid", "Barcelona")

        assert result is not None
        working.find_team.assert_awaited()

    @pytest.mark.asyncio
    async def test_returns_none_when_primary_and_all_fallbacks_fail(self, analyzer):
        analyzer.stats_fetcher.get_match_data = AsyncMock(return_value=None)
        analyzer.fallback_providers = [self._fake_provider(found=False), self._fake_provider(found=False)]

        result = await analyzer.analyze_match("Real Madrid", "Barcelona")

        assert result is None
        analyzer.claude_client.analyze_match.assert_not_awaited()


class TestMatchAnalyzerOddsEnrichment:
    """Market odds are optional and must never block the analysis."""

    @pytest.fixture
    def analyzer(self):
        analyzer = MatchAnalyzer()
        analyzer.cache_manager.get_cached_analysis = AsyncMock(return_value=None)
        analyzer.cache_manager.cache_analysis = AsyncMock(return_value=True)
        analyzer.stats_fetcher.get_match_data = AsyncMock(return_value={
            "home_team": "Real Madrid", "away_team": "Barcelona",
            "home_injuries": [], "away_injuries": [],
            "h2h_structured": {"matches": [], "summary_text": "x", "btts_pct": None, "over_2_5_pct": None},
        })
        analyzer.claude_client.analyze_match = AsyncMock(return_value="Análisis.")
        return analyzer

    @pytest.mark.asyncio
    async def test_no_odds_provider_leaves_match_data_untouched(self, analyzer):
        analyzer.odds_provider = None
        result = await analyzer.analyze_match("Real Madrid", "Barcelona")
        assert "market_odds" not in result["match_data"]

    @pytest.mark.asyncio
    async def test_odds_provider_enriches_match_data(self, analyzer):
        analyzer.odds_provider = AsyncMock()
        analyzer.odds_provider.find_match_odds = AsyncMock(return_value={
            "bookmakers_count": 2, "avg_decimal_odds": {"Real Madrid": 2.0}, "implied_probability_pct": {"Real Madrid": 50.0},
        })

        result = await analyzer.analyze_match("Real Madrid", "Barcelona")

        assert result["match_data"]["market_odds"]["bookmakers_count"] == 2

    @pytest.mark.asyncio
    async def test_odds_provider_failure_does_not_break_analysis(self, analyzer):
        analyzer.odds_provider = AsyncMock()
        analyzer.odds_provider.find_match_odds = AsyncMock(side_effect=Exception("The Odds API down"))

        result = await analyzer.analyze_match("Real Madrid", "Barcelona")

        assert result is not None
        assert result["match_data"]["market_odds"] is None


class TestGenerateMatchId:
    """Accented/punctuated team names must normalize to the same cache key
    as their plain-ASCII equivalent, or the cache silently misses."""

    @pytest.fixture
    def analyzer(self):
        return MatchAnalyzer()

    def test_accents_are_stripped(self, analyzer):
        assert analyzer._generate_match_id("Atlético", "River Plate") == \
            analyzer._generate_match_id("Atletico", "River Plate")

    def test_matches_diacritics_across_scripts(self, analyzer):
        assert analyzer._generate_match_id("São Paulo", "Flamengo") == \
            analyzer._generate_match_id("Sao Paulo", "Flamengo")

    def test_case_and_whitespace_insensitive(self, analyzer):
        assert analyzer._generate_match_id("Real Madrid", "Barcelona") == \
            analyzer._generate_match_id("  real madrid  ", "BARCELONA")

    def test_different_teams_produce_different_ids(self, analyzer):
        assert analyzer._generate_match_id("Real Madrid", "Barcelona") != \
            analyzer._generate_match_id("Real Madrid", "Sevilla")
