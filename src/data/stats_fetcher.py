"""
Football Statistics Fetcher.
Connects to API-Football to retrieve real-time match data, team statistics,
and historical information for analysis.
"""
from typing import Dict, Any, List, Optional
import aiohttp
import logging
from datetime import datetime, timedelta

from config.settings import settings

logger = logging.getLogger(__name__)


class StatsFetcher:
    """
    Fetches football statistics from API-Football.
    Provides team data, match information, and historical statistics.
    """
    
    def __init__(self):
        """Initialize stats fetcher with API configuration."""
        self.api_key = settings.api_football_key
        self.base_url = "https://api-football-v1.p.rapidapi.com/v3"
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }
        self.session: Optional[aiohttp.ClientSession] = None
        logger.info("Stats Fetcher initialized")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session
    
    async def close(self) -> None:
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make API request to API-Football.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            API response data or None if error
        """
        try:
            session = await self._get_session()
            url = f"{self.base_url}/{endpoint}"
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("response", [])
                elif response.status == 429:
                    logger.warning("Rate limit exceeded for API-Football")
                    return None
                else:
                    logger.error(f"API-Football error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error making request to {endpoint}: {e}", exc_info=True)
            return None
    
    async def get_team_info(self, team_name: str) -> Optional[Dict[str, Any]]:
        """
        Get team information by name.
        
        Args:
            team_name: Team name to search
            
        Returns:
            Team information dictionary
        """
        try:
            # Search for team
            data = await self._make_request("teams", {"search": team_name})
            
            if not data or len(data) == 0:
                logger.warning(f"Team not found: {team_name}")
                return None
            
            team = data[0].get("team", {})
            
            return {
                "id": team.get("id"),
                "name": team.get("name"),
                "country": team.get("country"),
                "logo": team.get("logo"),
                "venue_name": team.get("venue_name", ""),
                "venue_capacity": team.get("venue_capacity", 0),
            }
            
        except Exception as e:
            logger.error(f"Error getting team info for {team_name}: {e}", exc_info=True)
            return None
    
    async def get_team_statistics(
        self,
        team_id: int,
        league_id: int,
        season: int = 2024
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed team statistics for a specific league and season.
        
        Args:
            team_id: Team ID
            league_id: League ID
            season: Season year
            
        Returns:
            Team statistics dictionary
        """
        try:
            data = await self._make_request(
                "teams/statistics",
                {
                    "team": team_id,
                    "league": league_id,
                    "season": season
                }
            )
            
            if not data:
                return None
            
            # Extract relevant statistics
            stats = {
                # Position and points
                "position": data.get("league", {}).get("standings", {}).get("regular", [{}])[0].get("rank", 10),
                "points": data.get("league", {}).get("standings", {}).get("regular", [{}])[0].get("points", 0),
                
                # Form
                "form": data.get("form", ""),
                
                # Goals
                "goals_for": data.get("goals", {}).get("for", {}).get("total", {}).get("total", 0),
                "goals_against": data.get("goals", {}).get("against", {}).get("total", {}).get("total", 0),
                
                # xG (if available)
                "xg": data.get("xg", 1.5),
                "xga": data.get("xga", 1.2),
                
                # Advanced metrics
                "ppda": data.get("ppda", {}).get("attacks", 10),
                "possession": data.get("possession", {}).get("total", 50),
                "territorial_presence": data.get("territorial_presence", 45),
                "progressive_carries": data.get("progressive_carries", 150),
                
                # Shots
                "shots_on_target": data.get("shots", {}).get("on_target", {}).get("total", {}).get("average", 5),
                "shots_in_box_against": data.get("shots", {}).get("inside_box", {}).get("against", {}).get("total", 3),
                
                # Big chances
                "big_chances_scored": data.get("big_chances", {}).get("scored", 10),
                "big_chances_missed": data.get("big_chances", {}).get("missed", 5),
                "big_chances_conversion": self._calculate_big_chances_conversion(
                    data.get("big_chances", {}).get("scored", 10),
                    data.get("big_chances", {}).get("missed", 5)
                ),
                
                # Goalkeeper
                "gk_saves": data.get("goalkeeper", {}).get("saves", {}).get("total", 50),
                
                # Set pieces
                "corners_goals": data.get("set_pieces", {}).get("corners", {}).get("goals", 5),
                "freekicks_goals": data.get("set_pieces", {}).get("freekicks", {}).get("goals", 3),
                "set_pieces_efficiency": self._assess_set_pieces_efficiency(data.get("set_pieces", {})),
                
                # Physical metrics (simplified - would need separate API in production)
                "avg_distance_km": data.get("physical", {}).get("avg_distance", 105),
                "sprints_last3": data.get("physical", {}).get("sprints", 450),
                "rotations": data.get("lineups", {}).get("rotations", 3),
                
                # Recent xG
                "xg_last5": data.get("xg", {}).get("last5", 1.5),
                
                # Conversion rate
                "conversion_rate": self._calculate_conversion_rate(
                    data.get("goals", {}).get("for", {}).get("total", {}).get("total", 0),
                    data.get("shots", {}).get("total", {}).get("total", 100)
                ),
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting team statistics for team {team_id}: {e}", exc_info=True)
            return None
    
    async def get_match_data(
        self,
        home_team: str,
        away_team: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get complete match data for analysis.
        
        Args:
            home_team: Home team name
            away_team: Away team name
            
        Returns:
            Complete match data dictionary
        """
        try:
            logger.info(f"Fetching match data: {home_team} vs {away_team}")
            
            # Get team info
            home_info = await self.get_team_info(home_team)
            away_info = await self.get_team_info(away_team)
            
            if not home_info or not away_info:
                logger.error("Could not find one or both teams")
                return None
            
            # Get team statistics (using Premier League as default - would be dynamic in production)
            league_id = 39  # Premier League
            season = 2024
            
            home_stats = await self.get_team_statistics(home_info["id"], league_id, season)
            away_stats = await self.get_team_statistics(away_info["id"], league_id, season)
            
            if not home_stats or not away_stats:
                logger.error("Could not fetch statistics for one or both teams")
                return None
            
            # Get head-to-head history
            h2h_data = await self.get_head_to_head(home_info["id"], away_info["id"])
            
            # Get injuries
            home_injuries = await self.get_injuries(home_info["id"])
            away_injuries = await self.get_injuries(away_info["id"])
            
            # Build complete match data
            match_data = {
                # Basic info
                "home_team": home_info["name"],
                "away_team": away_info["name"],
                "league_name": "Premier League",  # Would be dynamic
                "matchday": 15,  # Would be fetched from API
                "match_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "stadium": home_info.get("venue_name", "Estadio"),
                "referee": "Árbitro",  # Would be fetched
                "referee_style": "Equilibrado",
                "total_matchdays": 38,
                
                # Home team stats
                "home_formation": "4-3-3",  # Would be fetched
                "home_position": home_stats.get("position", 10),
                "home_points": home_stats.get("points", 0),
                "home_form": home_stats.get("form", "DDDLW"),
                "home_goals_for": home_stats.get("goals_for", 0),
                "home_goals_against": home_stats.get("goals_against", 0),
                "home_xg": home_stats.get("xg", 1.5),
                "home_xga": home_stats.get("xga", 1.2),
                "home_xg_last5": home_stats.get("xg_last5", 1.5),
                "home_ppda": home_stats.get("ppda", 10),
                "home_possession": home_stats.get("possession", 50),
                "home_territorial_presence": home_stats.get("territorial_presence", 45),
                "home_progressive_carries": home_stats.get("progressive_carries", 150),
                "home_shots_on_target": home_stats.get("shots_on_target", 5),
                "home_conversion_rate": home_stats.get("conversion_rate", 12),
                "home_big_chances_conversion": home_stats.get("big_chances_conversion", 35),
                "home_corners_goals": home_stats.get("corners_goals", 5),
                "home_freekicks_goals": home_stats.get("freekicks_goals", 3),
                "home_set_pieces_efficiency": home_stats.get("set_pieces_efficiency", "Alta"),
                "home_gk_saves": home_stats.get("gk_saves", 50),
                "home_shots_in_box_against": home_stats.get("shots_in_box_against", 3),
                "home_avg_distance_km": home_stats.get("avg_distance_km", 105),
                "home_sprints_last3": home_stats.get("sprints_last3", 450),
                "home_rotations": home_stats.get("rotations", 3),
                "home_rest_days": 7,  # Would be calculated
                "home_motivation": 7,  # Would be calculated
                "home_injuries": home_injuries,
                
                # Away team stats
                "away_formation": "4-2-3-1",  # Would be fetched
                "away_position": away_stats.get("position", 10),
                "away_points": away_stats.get("points", 0),
                "away_form": away_stats.get("form", "WWWDW"),
                "away_goals_for": away_stats.get("goals_for", 0),
                "away_goals_against": away_stats.get("goals_against", 0),
                "away_xg": away_stats.get("xg", 1.5),
                "away_xga": away_stats.get("xga", 1.2),
                "away_xg_last5": away_stats.get("xg_last5", 1.5),
                "away_ppda": away_stats.get("ppda", 10),
                "away_possession": away_stats.get("possession", 50),
                "away_territorial_presence": away_stats.get("territorial_presence", 45),
                "away_progressive_carries": away_stats.get("progressive_carries", 150),
                "away_shots_on_target": away_stats.get("shots_on_target", 5),
                "away_conversion_rate": away_stats.get("conversion_rate", 12),
                "away_big_chances_conversion": away_stats.get("big_chances_conversion", 35),
                "away_corners_goals": away_stats.get("corners_goals", 5),
                "away_freekicks_goals": away_stats.get("freekicks_goals", 3),
                "away_set_pieces_efficiency": away_stats.get("set_pieces_efficiency", "Alta"),
                "away_gk_saves": away_stats.get("gk_saves", 50),
                "away_shots_in_box_against": away_stats.get("shots_in_box_against", 3),
                "away_avg_distance_km": away_stats.get("avg_distance_km", 105),
                "away_sprints_last3": away_stats.get("sprints_last3", 450),
                "away_rotations": away_stats.get("rotations", 3),
                "away_rest_days": 7,  # Would be calculated
                "away_motivation": 7,  # Would be calculated
                "away_injuries": away_injuries,
                
                # Context
                "weather": "Despejado",
                "pitch_condition": "Bueno",
                "head_to_head": h2h_data,
                "home_win_conditions": "Local fuerte en casa",
                "away_win_conditions": "Visitante fuerte en contra",
                "recurring_pattern": "Partidos igualados",
            }
            
            logger.info(f"Match data fetched successfully for {home_team} vs {away_team}")
            return match_data
            
        except Exception as e:
            logger.error(f"Error fetching match data: {e}", exc_info=True)
            return None
    
    async def get_head_to_head(self, home_team_id: int, away_team_id: int) -> str:
        """
        Get head-to-head history between two teams.
        
        Args:
            home_team_id: Home team ID
            away_team_id: Away team ID
            
        Returns:
            Formatted head-to-head string
        """
        try:
            data = await self._make_request(
                "fixtures/headtohead",
                {"h2h": f"{home_team_id}-{away_team_id}"}
            )
            
            if not data:
                return "Sin historial reciente"
            
            # Get last 5 matches
            recent_matches = data[:5] if len(data) >= 5 else data
            
            results = []
            for match in recent_matches:
                home_goals = match.get("goals", {}).get("home", 0)
                away_goals = match.get("goals", {}).get("away", 0)
                home_team_name = match.get("teams", {}).get("home", {}).get("name", "Local")
                away_team_name = match.get("teams", {}).get("away", {}).get("name", "Visitante")
                
                results.append(f"{home_team_name} {home_goals}-{away_goals} {away_team_name}")
            
            return "\n".join(results)
            
        except Exception as e:
            logger.error(f"Error getting head-to-head: {e}", exc_info=True)
            return "Error al cargar historial"
    
    async def get_injuries(self, team_id: int) -> List[Dict[str, Any]]:
        """
        Get current injuries for a team.
        
        Args:
            team_id: Team ID
            
        Returns:
            List of injury dictionaries
        """
        try:
            # Get current season
            current_year = datetime.now().year
            current_month = datetime.now().month
            season = current_year if current_month >= 8 else current_year - 1
            
            data = await self._make_request(
                "injuries",
                {
                    "team": team_id,
                    "season": season
                }
            )
            
            if not data:
                return []
            
            # Filter current injuries (not recovered)
            injuries = []
            for injury_data in data[:5]:  # Top 5 injuries
                injury = injury_data.get("injury", {})
                player = injury_data.get("player", {})
                
                injuries.append({
                    "player": player.get("name", "Unknown"),
                    "position": player.get("position", ""),
                    "injury_type": injury.get("type", ""),
                    "reason": injury.get("reason", ""),
                    "date": injury_data.get("date", ""),
                    "is_key_player": self._is_key_player(player.get("name", "")),
                    "impact": self._assess_injury_impact(player.get("position", ""))
                })
            
            return injuries
            
        except Exception as e:
            logger.error(f"Error getting injuries for team {team_id}: {e}", exc_info=True)
            return []
    
    def _is_key_player(self, player_name: str) -> bool:
        """Determine if a player is a key player (simplified)."""
        # In production, this would use a database of key players
        key_players_keywords = ["messi", "ronaldo", "mbappé", "haaland", "de bruyne", "mbappe"]
        return any(keyword in player_name.lower() for keyword in key_players_keywords)
    
    def _assess_injury_impact(self, position: str) -> str:
        """Assess impact of injury based on position."""
        key_positions = ["Goalkeeper", "Center-Back", "Striker", "Attacking Midfielder"]
        
        if any(pos in position for pos in key_positions):
            return "Alto"
        else:
            return "Medio"
    
    def _calculate_conversion_rate(self, goals: int, shots: int) -> float:
        """Calculate conversion rate percentage."""
        if shots == 0:
            return 0.0
        return round((goals / shots) * 100, 1)
    
    def _calculate_big_chances_conversion(self, scored: int, missed: int) -> float:
        """Calculate big chances conversion percentage."""
        total = scored + missed
        if total == 0:
            return 0.0
        return round((scored / total) * 100, 1)
    
    def _assess_set_pieces_efficiency(self, set_pieces: Dict) -> str:
        """Assess set pieces efficiency."""
        corners_goals = set_pieces.get("corners", {}).get("goals", 0)
        freekicks_goals = set_pieces.get("freekicks", {}).get("goals", 0)
        
        total = corners_goals + freekicks_goals
        
        if total >= 10:
            return "Muy Alta"
        elif total >= 7:
            return "Alta"
        elif total >= 4:
            return "Media"
        else:
            return "Baja"
    
    async def get_live_matches(self, league_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get live matches (for real-time tracking).
        
        Args:
            league_id: Optional league ID filter
            
        Returns:
            List of live matches
        """
        try:
            params = {"live": "all"}
            if league_id:
                params["league"] = league_id
            
            data = await self._make_request("fixtures", params)
            
            if not data:
                return []
            
            matches = []
            for fixture in data:
                match = {
                    "fixture_id": fixture.get("fixture", {}).get("id"),
                    "home_team": fixture.get("teams", {}).get("home", {}).get("name"),
                    "away_team": fixture.get("teams", {}).get("away", {}).get("name"),
                    "score": fixture.get("goals", {}),
                    "minute": fixture.get("fixture", {}).get("status", {}).get("elapsed", 0),
                    "status": fixture.get("fixture", {}).get("status", {}).get("short"),
                }
                matches.append(match)
            
            return matches
            
        except Exception as e:
            logger.error(f"Error getting live matches: {e}", exc_info=True)
            return []
    
    async def get_league_table(self, league_id: int, season: int = 2024) -> List[Dict[str, Any]]:
        """
        Get league standings.
        
        Args:
            league_id: League ID
            season: Season year
            
        Returns:
            List of teams with standings
        """
        try:
            data = await self._make_request(
                "standings",
                {"league": league_id, "season": season}
            )
            
            if not data:
                return []
            
            # Extract standings
            standings = []
            for team_data in data[0].get("league", {}).get("standings", [{}])[0].get("all", []):
                team = team_data.get("team", {})
                standings.append({
                    "position": team_data.get("rank"),
                    "team_id": team.get("id"),
                    "team_name": team.get("name"),
                    "points": team_data.get("points"),
                    "played": team_data.get("all", {}).get("matchsPlayed", 0),
                    "won": team_data.get("all", {}).get("win", 0),
                    "drawn": team_data.get("all", {}).get("draw", 0),
                    "lost": team_data.get("all", {}).get("lose", 0),
                    "goals_for": team_data.get("all", {}).get("goals", {}).get("for", 0),
                    "goals_against": team_data.get("all", {}).get("goals", {}).get("against", 0),
                })
            
            return standings
            
        except Exception as e:
            logger.error(f"Error getting league table: {e}", exc_info=True)
            return []
    
    async def health_check(self) -> bool:
        """
        Check if API-Football is accessible.
        
        Returns:
            True if API is working, False otherwise
        """
        try:
            data = await self._make_request("status")
            return data is not None
        except Exception as e:
            logger.error(f"API-Football health check failed: {e}")
            return False