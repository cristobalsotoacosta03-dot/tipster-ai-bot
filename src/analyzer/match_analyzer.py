"""
Match Analyzer - Core analysis engine.
Integrates StatsFetcher, PromptEngine, ClaudeClient, and CacheManager
to provide complete match analysis workflow.
"""
from typing import Dict, Any, Optional
import logging

from config.settings import settings
from src.utils.logger import logger
from src.data.stats_fetcher import StatsFetcher
from src.data.cache_manager import CacheManager
from src.analyzer.prompt_engine import PromptEngine
from src.analyzer.claude_client import ClaudeClient


class MatchAnalyzer:
    """
    Core match analysis engine.
    Orchestrates the complete analysis workflow:
    1. Fetch match data
    2. Check cache
    3. Generate prompt
    4. Get AI analysis
    5. Cache results
    """
    
    def __init__(self):
        """Initialize all components."""
        self.stats_fetcher = StatsFetcher()
        self.cache_manager = CacheManager()
        self.prompt_engine = PromptEngine()
        self.claude_client = ClaudeClient()
        
        logger.info("Match Analyzer initialized with all components")
    
    async def analyze_match(
        self,
        home_team: str,
        away_team: str,
        analysis_type: str = "full"
    ) -> Optional[Dict[str, Any]]:
        """
        Perform complete match analysis.
        
        Args:
            home_team: Home team name
            away_team: Away team name
            analysis_type: Type of analysis (full, express, premium)
            
        Returns:
            Analysis result dictionary
        """
        try:
            logger.info(f"Starting analysis: {home_team} vs {away_team} ({analysis_type})")
            
            # Generate match ID for caching
            match_id = self._generate_match_id(home_team, away_team)
            
            # Check cache first
            cached_analysis = await self.cache_manager.get_cached_analysis(match_id)
            if cached_analysis:
                logger.info(f"Returning cached analysis for {match_id}")
                cached_analysis["from_cache"] = True
                return cached_analysis
            
            # Fetch match data
            logger.info("Fetching match data...")
            match_data = await self.stats_fetcher.get_match_data(home_team, away_team)
            
            if not match_data:
                logger.error("Failed to fetch match data")
                return None
            
            # Generate prompt based on analysis type
            logger.info(f"Generating {analysis_type} prompt...")
            if analysis_type == "express":
                prompt = self.prompt_engine.generate_express_prompt(match_data)
            elif analysis_type == "premium":
                prompt = self.prompt_engine.generate_premium_prompt(match_data)
            else:
                prompt = self.prompt_engine.generate_full_analysis_prompt(match_data)
            
            # Get analysis from Claude
            logger.info("Requesting analysis from Claude...")
            analysis_text = await self.claude_client.analyze_match(prompt)
            
            if not analysis_text:
                logger.error("Failed to get analysis from Claude")
                return None
            
            # Build result
            result = {
                "match_id": match_id,
                "home_team": home_team,
                "away_team": away_team,
                "analysis_type": analysis_type,
                "analysis": analysis_text,
                "match_data": match_data,
                "prompt_used": prompt,
                "confidence_level": self.prompt_engine.calculate_confidence(match_data),
                "stake": self.prompt_engine.calculate_stake(match_data),
                "from_cache": False,
                "timestamp": logging.Formatter().formatTime(logging.LogRecord(
                    name="", level=0, pathname="", lineno=0, msg="", args=(), exc_info=None
                )),
            }
            
            # Cache the result
            logger.info("Caching analysis result...")
            await self.cache_manager.cache_analysis(match_id, result)
            
            logger.info(f"Analysis completed successfully for {home_team} vs {away_team}")
            return result
            
        except Exception as e:
            logger.error(f"Error in match analysis: {e}", exc_info=True)
            return None
    
    async def get_team_analysis(
        self,
        team_name: str,
        league_id: int = 39,
        season: int = 2024
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed team analysis.
        
        Args:
            team_name: Team name
            league_id: League ID
            season: Season year
            
        Returns:
            Team analysis dictionary
        """
        try:
            logger.info(f"Fetching team analysis for {team_name}")
            
            # Check cache
            cache_key = f"team_analysis:{team_name.lower()}:{league_id}:{season}"
            cached = await self.cache_manager.get(cache_key)
            if cached:
                logger.info(f"Returning cached team analysis for {team_name}")
                return cached
            
            # Get team info
            team_info = await self.stats_fetcher.get_team_info(team_name)
            if not team_info:
                return None
            
            # Get team statistics
            stats = await self.stats_fetcher.get_team_statistics(
                team_info["id"], league_id, season
            )
            
            if not stats:
                return None
            
            # Build analysis
            analysis = {
                "team_info": team_info,
                "statistics": stats,
                "timestamp": datetime.now().isoformat(),
            }
            
            # Cache result
            await self.cache_manager.set(cache_key, analysis, ttl=3600)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error getting team analysis: {e}", exc_info=True)
            return None
    
    def _generate_match_id(self, home_team: str, away_team: str) -> str:
        """
        Generate unique match ID for caching.
        
        Args:
            home_team: Home team name
            away_team: Away team name
            
        Returns:
            Match ID string
        """
        # Normalize team names
        home = home_team.lower().strip()
        away = away_team.lower().strip()
        
        # Create ID
        match_id = f"{home}_vs_{away}"
        
        return match_id
    
    async def health_check(self) -> Dict[str, bool]:
        """
        Check health of all components.
        
        Returns:
            Dictionary with health status of each component
        """
        results = {}
        
        try:
            # Check Claude
            results["claude"] = await self.claude_client.health_check()
        except Exception as e:
            logger.error(f"Claude health check failed: {e}")
            results["claude"] = False
        
        try:
            # Check Stats Fetcher
            results["stats_fetcher"] = await self.stats_fetcher.health_check()
        except Exception as e:
            logger.error(f"Stats Fetcher health check failed: {e}")
            results["stats_fetcher"] = False
        
        try:
            # Check Cache
            results["cache"] = await self.cache_manager.health_check()
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            results["cache"] = False
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get analyzer statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            "prompt_engine": self.prompt_engine.get_prompt_stats(),
            "cache_manager": self.cache_manager.get_stats(),
        }


# Import datetime for timestamp
from datetime import datetime