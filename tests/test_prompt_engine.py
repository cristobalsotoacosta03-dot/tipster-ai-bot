"""
Tests for Prompt Engine.
"""
import pytest
from src.analyzer.prompt_engine import PromptEngine


class TestPromptEngine:
    """Test suite for PromptEngine."""
    
    @pytest.fixture
    def prompt_engine(self):
        """Create PromptEngine instance."""
        return PromptEngine()
    
    @pytest.fixture
    def sample_match_data(self):
        """Create sample match data for testing."""
        return {
            "home_team": "Real Madrid",
            "away_team": "Barcelona",
            "league_name": "La Liga",
            "matchday": 15,
            "match_date": "2024-12-15 21:00",
            "stadium": "Santiago Bernabéu",
            "referee": "Mateu Lahoz",
            "referee_style": "Equilibrado",
            "total_matchdays": 38,
            "home_formation": "4-3-3",
            "away_formation": "4-2-3-1",
            "home_position": 2,
            "away_position": 3,
            "home_points": 38,
            "away_points": 35,
            "home_form": "WWWDW",
            "away_form": "DWWWL",
            "home_goals_for": 35,
            "away_goals_for": 32,
            "home_goals_against": 15,
            "away_goals_against": 18,
            "home_xg": 1.8,
            "away_xg": 1.6,
            "home_xga": 1.0,
            "away_xga": 1.2,
            "home_xg_last5": 2.0,
            "away_xg_last5": 1.5,
            "home_ppda": 9,
            "away_ppda": 11,
            "home_possession": 55,
            "away_possession": 45,
            "home_rest_days": 7,
            "away_rest_days": 5,
            "home_injuries": [],
            "away_injuries": []
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
        assert "PPDA" in prompt
        assert "xG" in prompt
    
    def test_generate_express_prompt(self, prompt_engine, sample_match_data):
        """Test express prompt generation."""
        prompt = prompt_engine.generate_express_prompt(sample_match_data)
        
        assert prompt is not None
        assert len(prompt) > 0
        assert "ANÁLISIS RÁPIDO" in prompt
        assert "Real Madrid" in prompt
        assert "Barcelona" in prompt
    
    def test_generate_premium_prompt(self, prompt_engine, sample_match_data):
        """Test premium prompt generation."""
        prompt = prompt_engine.generate_premium_prompt(sample_match_data)
        
        assert prompt is not None
        assert len(prompt) > 0
        assert "ANÁLISIS PREMIUM" in prompt
        assert "Real Madrid" in prompt
        assert "Barcelona" in prompt
    
    def test_tactical_analysis_enrichment(self, prompt_engine, sample_match_data):
        """Test tactical analysis enrichment."""
        enriched = prompt_engine._enrich_with_tactical_analysis(sample_match_data)
        
        assert enriched is not None
        assert "home_play_style" in enriched
        assert "away_play_style" in enriched
        assert "home_pressing_intensity" in enriched
        assert "away_pressing_intensity" in enriched
        assert "fatigue_advantage" in enriched
        assert "xg_differential" in enriched
    
    def test_physical_advantage_calculation(self, prompt_engine, sample_match_data):
        """Test physical advantage calculation."""
        advantage = prompt_engine._calculate_fatigue_advantage(sample_match_data)
        
        assert advantage is not None
        assert isinstance(advantage, str)
        # Home team has more rest days (7 vs 5)
        assert "LOCAL" in advantage or "local" in advantage.lower()
    
    def test_xg_differential_calculation(self, prompt_engine, sample_match_data):
        """Test xG differential calculation."""
        xg_diff = prompt_engine._calculate_xg_differential(sample_match_data)
        
        assert xg_diff is not None
        assert isinstance(xg_diff, str)
        # Home xG (1.8) > Away xG (1.6), diff = 0.2
        assert "+" in xg_diff or "0.20" in xg_diff
    
    def test_confidence_calculation(self, prompt_engine, sample_match_data):
        """Test confidence level calculation."""
        confidence = prompt_engine._calculate_confidence(sample_match_data)
        
        assert confidence is not None
        assert isinstance(confidence, int)
        assert 0 <= confidence <= 100
    
    def test_stake_calculation(self, prompt_engine, sample_match_data):
        """Test stake calculation."""
        stake = prompt_engine._calculate_stake(sample_match_data)
        
        assert stake is not None
        assert isinstance(stake, int)
        assert 1 <= stake <= 5
    
    def test_presssing_intensity_calculation(self, prompt_engine):
        """Test pressing intensity calculation."""
        # Low PPDA = high pressing
        intensity = prompt_engine._calculate_pressing_intensity({"home_ppda": 8}, "home")
        assert "Muy alto" in intensity or "Alto" in intensity
        
        # High PPDA = low pressing
        intensity = prompt_engine._calculate_pressing_intensity({"home_ppda": 13}, "home")
        assert "Bajo" in intensity
    
    def test_injury_analysis(self, prompt_engine):
        """Test injury analysis."""
        # No injuries
        analysis = prompt_engine._analyze_injuries({"home_injuries": []}, "home")
        assert "Sin bajas" in analysis
        
        # With injuries
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
        match_data = {"home_rest_days": 10, "away_rest_days": 3, "home_xg": 1.5, "away_xg": 1.5, "home_ppda": 10, "away_ppda": 10}
        factor = prompt_engine._identify_decisive_factor(match_data)
        assert "descanso" in factor.lower() or "física" in factor.lower()
        
        # xG advantage
        match_data = {"home_rest_days": 7, "away_rest_days": 7, "home_xg": 2.0, "away_xg": 1.2, "home_ppda": 10, "away_ppda": 10}
        factor = prompt_engine._identify_decisive_factor(match_data)
        assert "ofensiva" in factor.lower() or "xg" in factor.lower()