"""
Tests for Analysis Formatters.
"""
import pytest
from src.bot.formatters import AnalysisFormatter, MessageBuilder


class TestAnalysisFormatter:
    """Test suite for AnalysisFormatter."""
    
    @pytest.fixture
    def formatter(self):
        """Create AnalysisFormatter instance."""
        return AnalysisFormatter()
    
    @pytest.fixture
    def sample_analysis_result(self):
        """Create sample analysis result."""
        return {
            "match_id": "real_madrid_vs_barcelona",
            "home_team": "Real Madrid",
            "away_team": "Barcelona",
            "analysis_type": "full",
            "analysis": "Este es un análisis de prueba con contenido táctico detallado...",
            "match_data": {
                "home_team": "Real Madrid",
                "away_team": "Barcelona",
                "home_xg": 1.8,
                "away_xg": 1.6,
                "home_ppda": 9,
                "away_ppda": 11,
                "home_rest_days": 7,
                "away_rest_days": 5
            },
            "from_cache": False
        }
    
    def test_formatter_initialization(self, formatter):
        """Test formatter initialization."""
        assert formatter is not None
        assert formatter.max_message_length == 4096
    
    def test_format_analysis_for_telegram_free(self, formatter, sample_analysis_result):
        """Test formatting for free users."""
        formatted = formatter.format_analysis_for_telegram(
            sample_analysis_result,
            user_is_vip=False
        )
        
        assert formatted is not None
        assert "Real Madrid" in formatted
        assert "Barcelona" in formatted
        assert "ANÁLISIS:" in formatted
        assert "Lo que ve un jugador de Preferente" in formatted
    
    def test_format_analysis_for_telegram_vip(self, formatter, sample_analysis_result):
        """Test formatting for VIP users."""
        formatted = formatter.format_analysis_for_telegram(
            sample_analysis_result,
            user_is_vip=True
        )
        
        assert formatted is not None
        assert "ANÁLISIS PREMIUM - VIP" in formatted
    
    def test_preferente_insight_generation(self, formatter):
        """Test Preferente-style insight generation."""
        match_data = {
            "home_team": "Real Madrid",
            "away_team": "Barcelona",
            "home_xg": 1.8,
            "away_xg": 1.6,
            "home_ppda": 9,
            "away_ppda": 11,
            "home_rest_days": 7,
            "away_rest_days": 5
        }
        
        insight = formatter._generate_preferente_insight(match_data)
        
        assert insight is not None
        assert "Lo que ve un jugador de Preferente" in insight
        assert "Real Madrid" in insight or "Barcelona" in insight
    
    def test_vip_hook_generation(self, formatter):
        """Test VIP hook generation."""
        match_data = {
            "home_team": "Real Madrid",
            "away_team": "Barcelona"
        }
        
        # Express hook
        hook = formatter._generate_vip_hook(match_data, "express")
        assert "¿Quieres el análisis COMPLETO?" in hook
        assert "€29.99" in hook
        
        # Full hook
        hook = formatter._generate_vip_hook(match_data, "full")
        assert "ANÁLISIS PREMIUM DISPONIBLE" in hook
        assert "€29.99" in hook
    
    def test_error_message_formatting(self, formatter):
        """Test error message formatting."""
        error_msg = formatter.format_error("general")
        assert "❌" in error_msg
        
        error_msg = formatter.format_error("limit_reached")
        assert "Límite" in error_msg or "límite" in error_msg
    
    def test_limit_message_formatting(self, formatter):
        """Test limit message formatting."""
        msg = formatter.format_limit_message(2, 2)
        assert "2/2" in msg
        assert "€29.99" in msg
    
    def test_success_message_formatting(self, formatter):
        """Test success message formatting."""
        msg = formatter.format_success_message("express")
        assert "✅" in msg
        
        msg = formatter.format_success_message("premium")
        assert "✅" in msg


class TestMessageBuilder:
    """Test suite for MessageBuilder."""
    
    def test_build_vip_promo_keyboard(self):
        """Test VIP promo keyboard building."""
        keyboard = MessageBuilder.build_vip_promo_keyboard()
        
        assert keyboard is not None
        assert "inline_keyboard" in keyboard
        assert len(keyboard["inline_keyboard"]) > 0
    
    def test_build_analysis_keyboard_with_vip(self):
        """Test analysis keyboard for VIP users."""
        keyboard = MessageBuilder.build_analysis_keyboard("match_123", has_vip=True)
        
        assert keyboard is not None
        assert "inline_keyboard" in keyboard
        # Should only have refresh button for VIP
        assert len(keyboard["inline_keyboard"]) == 1
    
    def test_build_analysis_keyboard_without_vip(self):
        """Test analysis keyboard for free users."""
        keyboard = MessageBuilder.build_analysis_keyboard("match_123", has_vip=False)
        
        assert keyboard is not None
        assert "inline_keyboard" in keyboard
        # Should have refresh + VIP promo buttons
        assert len(keyboard["inline_keyboard"]) == 2