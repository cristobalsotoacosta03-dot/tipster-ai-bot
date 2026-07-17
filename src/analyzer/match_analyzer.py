"""
Match Analyzer - Core analysis engine.
Integrates StatsFetcher, PromptEngine, ClaudeClient, and CacheManager
to provide complete match analysis workflow.
"""
from typing import Dict, Any, Optional
from dataclasses import asdict
from datetime import datetime

from config.settings import settings
from src.utils.logger import logger
from src.data.stats_fetcher import StatsFetcher
from src.data.cache_manager import CacheManager
from src.data.providers.base import build_match_data
from src.data.providers.football_data_org import FootballDataOrgProvider
from src.data.providers.thesportsdb import TheSportsDbProvider
from src.data.odds_provider import OddsProvider
from src.analyzer.prompt_engine import PromptEngine
from src.analyzer.claude_client import ClaudeClient


class MatchAnalyzer:
    """
    Core match analysis engine.
    Orchestrates the complete analysis workflow:
    1. Fetch match data (API-Football, falling back to other free sources
       when a team can't be found there)
    2. Check cache
    3. Generate prompt
    4. Get AI analysis
    5. Cache results
    """

    def __init__(self):
        """Initialize all components."""
        self.cache_manager = CacheManager()
        self.stats_fetcher = StatsFetcher(cache_manager=self.cache_manager)
        self.prompt_engine = PromptEngine()
        self.claude_client = ClaudeClient()

        # Free, legitimate fallback sources - only used when API-Football
        # can't find one of the two teams. Each is a no-op if its API key
        # isn't configured.
        self.fallback_providers = []
        if settings.football_data_org_key:
            self.fallback_providers.append(FootballDataOrgProvider(cache_manager=self.cache_manager))
        if settings.thesportsdb_api_key:
            self.fallback_providers.append(TheSportsDbProvider(cache_manager=self.cache_manager))

        # Optional real bookmaker odds, used only to compare the model's
        # confidence against the market - never required for /analisis.
        self.odds_provider = OddsProvider(cache_manager=self.cache_manager) if settings.odds_api_key else None

        logger.info(
            f"Match Analyzer initialized with all components "
            f"({len(self.fallback_providers)} fallback data source(s) enabled)"
        )
    
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
            match_data = await self._fetch_match_data(home_team, away_team)

            if not match_data:
                logger.error("Failed to fetch match data")
                return None

            if self.odds_provider:
                match_data["market_odds"] = await self._fetch_market_odds(home_team, away_team)

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
                "timestamp": datetime.now().isoformat(),
            }
            
            # Cache the result
            logger.info("Caching analysis result...")
            await self.cache_manager.cache_analysis(match_id, result)
            
            logger.info(f"Analysis completed successfully for {home_team} vs {away_team}")
            return result
            
        except Exception as e:
            logger.error(f"Error in match analysis: {e}", exc_info=True)
            return None

    async def _fetch_match_data(self, home_team: str, away_team: str) -> Optional[Dict[str, Any]]:
        """Try API-Football first; only if it can't resolve both teams
        (not found, or free-tier quota exhausted), try the configured free
        fallback providers in order."""
        data = await self.stats_fetcher.get_match_data(home_team, away_team)
        if data is not None:
            return data

        if not self.fallback_providers:
            return None

        logger.warning(
            f"API-Football couldn't resolve '{home_team}' vs '{away_team}', "
            f"trying {len(self.fallback_providers)} fallback source(s)..."
        )
        for provider in self.fallback_providers:
            try:
                data = await self._fetch_from_fallback(provider, home_team, away_team)
            except Exception as e:
                logger.error(f"Fallback provider {provider.__class__.__name__} failed: {e}", exc_info=True)
                data = None
            if data is not None:
                logger.info(f"Match data resolved via fallback provider {provider.__class__.__name__}")
                return data

        return None

    async def _fetch_from_fallback(self, provider, home_team: str, away_team: str) -> Optional[Dict[str, Any]]:
        home_ref = await provider.find_team(home_team)
        away_ref = await provider.find_team(away_team)
        if not home_ref or not away_ref:
            return None

        home_league = await provider.get_league_context(home_ref.id, home_ref.country)
        away_league = await provider.get_league_context(away_ref.id, away_ref.country)
        home_form = await provider.get_recent_form(home_ref.id)
        away_form = await provider.get_recent_form(away_ref.id)
        h2h = await provider.get_head_to_head(home_ref.id, away_ref.id)
        home_injuries = await provider.get_injuries(home_ref.id, home_league["season"] if home_league else 0)
        away_injuries = await provider.get_injuries(away_ref.id, away_league["season"] if away_league else 0)

        return build_match_data(
            home_ref=home_ref,
            away_ref=away_ref,
            league_name=home_league["league_name"] if home_league else None,
            home_form=home_form,
            away_form=away_form,
            h2h=h2h,
            home_injuries=home_injuries,
            away_injuries=away_injuries,
            source=provider.__class__.__name__,
        )

    async def _fetch_market_odds(self, home_team: str, away_team: str) -> Optional[Dict[str, Any]]:
        """Best-effort real bookmaker odds - never blocks or fails the
        analysis if The Odds API is unreachable or doesn't have this match."""
        try:
            return await self.odds_provider.find_match_odds(home_team, away_team)
        except Exception as e:
            logger.error(f"Error fetching market odds: {e}", exc_info=True)
            return None

    async def get_team_analysis(self, team_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a team's real recent form and league standing (league/season are
        resolved dynamically for the team, not assumed).

        Args:
            team_name: Team name

        Returns:
            Team analysis dictionary
        """
        try:
            logger.info(f"Fetching team analysis for {team_name}")

            team_info = await self.stats_fetcher.get_team_info(team_name)
            if not team_info:
                return None

            cache_key = f"team_analysis:{team_name.lower()}"
            cached = await self.cache_manager.get(cache_key)
            if cached:
                logger.info(f"Returning cached team analysis for {team_name}")
                return cached

            league = await self.stats_fetcher.resolve_league_context(
                team_info["id"], team_info.get("country")
            )
            form = await self.stats_fetcher.get_recent_form(team_info["id"])
            standing = None
            if league:
                standing = await self.stats_fetcher.get_standing_for_team(
                    league["league_id"], league["season"], team_info["id"]
                )

            analysis = {
                "team_info": team_info,
                "league_context": league,
                "standing": standing,
                "form": asdict(form),
                "timestamp": datetime.now().isoformat(),
            }

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
    
    async def close(self) -> None:
        """Close HTTP sessions for the primary, every fallback provider, and
        the odds provider (if enabled)."""
        await self.stats_fetcher.close()
        for provider in self.fallback_providers:
            await provider.close()
        if self.odds_provider:
            await self.odds_provider.close()

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