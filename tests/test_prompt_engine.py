"""
Tests for Prompt Engine.
"""
import pytest
from src.analyzer.prompt_engine import PromptEngine, NOT_AVAILABLE


class TestPromptEngine:
    """Test suite for PromptEngine."""

    @pytest.fixture
    def prompt_engine(self):
        """Create PromptEngine instance."""
        return PromptEngine()

    @pytest.fixture
    def sample_match_data(self):
        """Sample match data shaped like what StatsFetcher.get_match_data
        now actually returns - real fields only, no fabricated metrics."""
        return {
            "home_team": "Real Madrid",
            "away_team": "Barcelona",
            "league_name": "La Liga",
            "match_date": "2024-12-15 21:00",
            "stadium": "Santiago Bernabéu",
            "home_position": 2,
            "away_position": 3,
            "home_points": 38,
            "away_points": 35,
            "home_played": 17,
            "away_played": 17,
            "home_form": "WWWDW",
            "away_form": "DWWWL",
            "home_goals_for": 12,
            "away_goals_for": 9,
            "home_goals_against": 4,
            "away_goals_against": 6,
            "home_avg_goals_for": 2.4,
            "away_avg_goals_for": 1.8,
            "home_avg_goals_against": 0.8,
            "away_avg_goals_against": 1.2,
            "home_rest_days": 7,
            "away_rest_days": 5,
            "home_injuries": [],
            "away_injuries": [],
            "head_to_head": "Real Madrid 2-1 Barcelona\nBarcelona 3-1 Real Madrid",
            "h2h_structured": {
                "matches": [
                    {"home_goals": 2, "away_goals": 1, "is_home_for_ref_team": True},
                    {"home_goals": 3, "away_goals": 1, "is_home_for_ref_team": False},
                ],
                "summary_text": "Real Madrid 2-1 Barcelona\nBarcelona 3-1 Real Madrid",
                "btts_pct": 100.0,
                "over_2_5_pct": 50.0,
            },
        }

    @pytest.fixture
    def sparse_match_data(self):
        """Match data missing most derived signals (e.g. a team with no
        recent fixtures found) - should degrade gracefully, not crash or
        fabricate numbers."""
        return {
            "home_team": "Equipo A",
            "away_team": "Equipo B",
            "league_name": None,
            "home_position": None,
            "away_position": None,
            "home_points": None,
            "away_points": None,
            "home_played": None,
            "away_played": None,
            "home_form": "",
            "away_form": "",
            "home_goals_for": 0,
            "away_goals_for": 0,
            "home_goals_against": 0,
            "away_goals_against": 0,
            "home_avg_goals_for": None,
            "away_avg_goals_for": None,
            "home_avg_goals_against": None,
            "away_avg_goals_against": None,
            "home_rest_days": None,
            "away_rest_days": None,
            "home_injuries": [],
            "away_injuries": [],
            "head_to_head": "Sin historial reciente",
            "h2h_structured": {"matches": [], "summary_text": "Sin historial reciente", "btts_pct": None, "over_2_5_pct": None},
        }

    def test_prompt_engine_initialization(self, prompt_engine):
        """Test PromptEngine initialization."""
        assert prompt_engine is not None
        assert len(prompt_engine.templates) == 3
        assert "full_analysis" in prompt_engine.templates
        assert "express" in prompt_engine.templates
        assert "premium" in prompt_engine.templates

    def test_generate_full_analysis_prompt(self, prompt_engine, sample_match_data):
        """Test full analysis prompt generation."""
        prompt = prompt_engine.generate_full_analysis_prompt(sample_match_data)

        assert prompt is not None
        assert len(prompt) > 0
        assert "Real Madrid" in prompt
        assert "Barcelona" in prompt
        assert "ANÁLISIS TÁCTICO" in prompt
        # No leftover unfilled $placeholders leaked into the prompt.
        assert "$" not in prompt

    def test_generate_express_prompt(self, prompt_engine, sample_match_data):
        """Test express prompt generation."""
        prompt = prompt_engine.generate_express_prompt(sample_match_data)

        assert prompt is not None
        assert len(prompt) > 0
        assert "ANÁLISIS RÁPIDO" in prompt
        assert "Real Madrid" in prompt
        assert "Barcelona" in prompt
        assert "$" not in prompt

    def test_generate_premium_prompt(self, prompt_engine, sample_match_data):
        """Test premium prompt generation - all sections must be filled,
        not left as literal $placeholder text (previous bug)."""
        prompt = prompt_engine.generate_premium_prompt(sample_match_data)

        assert prompt is not None
        assert len(prompt) > 0
        assert "ANÁLISIS PREMIUM" in prompt
        assert "Real Madrid" in prompt
        assert "Barcelona" in prompt
        assert "$" not in prompt

    def test_prompts_degrade_gracefully_with_sparse_data(self, prompt_engine, sparse_match_data):
        """No exceptions and no invented numbers when most real signals are missing."""
        full = prompt_engine.generate_full_analysis_prompt(sparse_match_data)
        express = prompt_engine.generate_express_prompt(sparse_match_data)
        premium = prompt_engine.generate_premium_prompt(sparse_match_data)

        for prompt in (full, express, premium):
            assert "$" not in prompt
            assert "None" not in prompt

    def test_tactical_analysis_enrichment(self, prompt_engine, sample_match_data):
        """Test tactical analysis enrichment."""
        enriched = prompt_engine._enrich_with_tactical_analysis(sample_match_data)

        assert enriched is not None
        assert "fatigue_advantage" in enriched
        assert "tactical_advantage" in enriched
        assert "goal_differential_analysis" in enriched

    def test_physical_advantage_calculation(self, prompt_engine, sample_match_data):
        """Test physical advantage calculation."""
        advantage = prompt_engine._calculate_fatigue_advantage(sample_match_data)

        assert advantage is not None
        assert isinstance(advantage, str)
        # Home team has more rest days (7 vs 5)
        assert "LOCAL" in advantage

    def test_physical_advantage_unavailable_without_rest_days(self, prompt_engine):
        """When rest days aren't known, say so instead of assuming a default."""
        advantage = prompt_engine._calculate_fatigue_advantage({"home_rest_days": None, "away_rest_days": None})
        assert advantage == NOT_AVAILABLE

    def test_goal_differential_analysis(self, prompt_engine, sample_match_data):
        """Home team scores more on average recently -> should be flagged."""
        analysis = prompt_engine._goal_differential_analysis(sample_match_data)
        assert "Real Madrid" in analysis

    def test_confidence_calculation(self, prompt_engine, sample_match_data):
        """Test confidence level calculation."""
        confidence = prompt_engine._calculate_confidence(sample_match_data)

        assert confidence is not None
        assert isinstance(confidence, int)
        assert 0 <= confidence <= 100

    def test_confidence_is_low_with_no_real_signals(self, prompt_engine):
        """No real signals available -> confidence should not be inflated to a neutral default."""
        confidence = prompt_engine._calculate_confidence({})
        assert confidence == 30

    def test_stake_calculation(self, prompt_engine, sample_match_data):
        """Test stake calculation."""
        stake = prompt_engine._calculate_stake(sample_match_data)

        assert stake is not None
        assert isinstance(stake, int)
        assert 1 <= stake <= 5

    def test_injury_analysis(self, prompt_engine):
        """Test injury analysis."""
        analysis = prompt_engine._analyze_injuries({"home_injuries": []}, "home")
        assert "Sin bajas" in analysis

        injuries = [
            {"player": "Player 1", "position": "Striker", "impact": "Alto"},
            {"player": "Player 2", "position": "Midfielder", "impact": "Medio"}
        ]
        analysis = prompt_engine._analyze_injuries({"home_injuries": injuries}, "home")
        assert "Player 1" in analysis
        assert "Player 2" in analysis

    def test_prompt_stats(self, prompt_engine):
        """Test prompt statistics."""
        stats = prompt_engine.get_prompt_stats()

        assert stats is not None
        assert "total_templates" in stats
        assert stats["total_templates"] == 3
        assert "full_analysis_length" in stats
        assert "express_length" in stats
        assert "premium_length" in stats

    def test_decisive_factor_identification(self, prompt_engine):
        """Test decisive factor identification."""
        # Rest advantage
        match_data = {"home_rest_days": 10, "away_rest_days": 3, "home_avg_goals_for": 1.5, "away_avg_goals_for": 1.5}
        factor = prompt_engine._identify_decisive_factor(match_data)
        assert "descanso" in factor.lower() or "física" in factor.lower()

        # Goal production advantage
        match_data = {"home_rest_days": 7, "away_rest_days": 7, "home_avg_goals_for": 2.5, "away_avg_goals_for": 1.0}
        factor = prompt_engine._identify_decisive_factor(match_data)
        assert "ofensiva" in factor.lower()

    def test_win_conditions_from_h2h(self, prompt_engine, sample_match_data):
        """Real Madrid won 1 of the 2 sample h2h matches as home team's perspective."""
        h2h = sample_match_data["h2h_structured"]
        conditions = prompt_engine._win_conditions(h2h, "Real Madrid", for_home=True)
        assert "1" in conditions

    def test_recurring_pattern_no_history(self, prompt_engine):
        pattern = prompt_engine._recurring_pattern({"matches": [], "btts_pct": None, "over_2_5_pct": None})
        assert "Sin historial" in pattern

    def test_market_odds_summary_not_available_without_odds(self, prompt_engine):
        summary = prompt_engine._market_odds_summary({})
        assert summary == NOT_AVAILABLE

    def test_market_odds_summary_with_real_odds(self, prompt_engine, sample_match_data):
        sample_match_data["market_odds"] = {
            "bookmakers_count": 3,
            "avg_decimal_odds": {"Real Madrid": 2.1, "Draw": 3.4, "Barcelona": 3.7},
            "implied_probability_pct": {"Real Madrid": 47.6, "Draw": 29.4, "Barcelona": 27.0},
        }
        summary = prompt_engine._market_odds_summary(sample_match_data)
        assert "3 casa(s)" in summary
        assert "Real Madrid" in summary
        assert "47.6%" in summary

    def test_full_prompt_includes_market_odds_when_present(self, prompt_engine, sample_match_data):
        sample_match_data["market_odds"] = {
            "bookmakers_count": 2,
            "avg_decimal_odds": {"Real Madrid": 2.1},
            "implied_probability_pct": {"Real Madrid": 47.6},
        }
        prompt = prompt_engine.generate_full_analysis_prompt(sample_match_data)
        assert "47.6%" in prompt
        assert "$" not in prompt
