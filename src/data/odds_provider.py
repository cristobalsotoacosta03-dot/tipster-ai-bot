"""
The Odds API provider (https://the-odds-api.com/) - real bookmaker odds,
used to compare the model's confidence against the market's implied
probability. Free tier: 500 requests/month, no card required.

Not part of MatchDataProvider (results/fixtures) - this is a separate
concern (market odds) consumed by MatchAnalyzer as an optional enrichment
step, never required for /analisis to work.

The Odds API has no direct team-vs-team lookup: odds are fetched per league
(sport_key) and a single call returns every upcoming event for that league
at the cost of one credit, so the whole SOCCER_SPORT_KEYS list can be
queried cheaply and cached.
"""
from typing import Any, Dict, List, Optional
import logging

import aiohttp

from config.settings import settings

logger = logging.getLogger(__name__)

# A deliberately small set of major soccer leagues to keep the free
# 500 req/month quota sustainable. Each league covered by one cached call.
SOCCER_SPORT_KEYS = [
    "soccer_epl",
    "soccer_spain_la_liga",
    "soccer_italy_serie_a",
    "soccer_germany_bundesliga",
    "soccer_france_ligue_one",
    "soccer_uefa_champs_league",
]

ODDS_CACHE_TTL_SECONDS = 45 * 60  # 45 min - odds shift, but not per-second


class OddsProvider:
    """Fetches real bookmaker odds from The Odds API's free tier."""

    def __init__(self, cache_manager=None):
        self.api_key = settings.odds_api_key
        self.base_url = "https://api.the-odds-api.com/v4"
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache_manager = cache_manager

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self) -> None:
        if self.session and not self.session.closed:
            await self.session.close()

    async def _get_odds_for_league(self, sport_key: str) -> List[Dict[str, Any]]:
        cache_key = f"odds:{sport_key}"
        if self.cache_manager:
            cached = await self.cache_manager.get(cache_key)
            if cached is not None:
                return cached

        try:
            session = await self._get_session()
            url = f"{self.base_url}/sports/{sport_key}/odds/"
            params = {"apiKey": self.api_key, "regions": "eu", "markets": "h2h", "oddsFormat": "decimal"}
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    logger.warning(f"The Odds API error for {sport_key}: {response.status}")
                    return []
                events = await response.json()
        except Exception as e:
            logger.error(f"Error fetching odds for {sport_key}: {e}", exc_info=True)
            return []

        if self.cache_manager and events:
            await self.cache_manager.set(cache_key, events, ttl=ODDS_CACHE_TTL_SECONDS)

        return events

    def _matches_team(self, name: str, needle: str) -> bool:
        return needle.strip().lower() in name.strip().lower()

    async def find_match_odds(self, home_team: str, away_team: str) -> Optional[Dict[str, Any]]:
        """
        Search the major-league odds boards for this fixture and return
        real, averaged decimal odds + implied probabilities. Returns None
        if the match isn't found in any covered league (upcoming events
        only - The Odds API doesn't carry odds for matches too far out or
        already finished).
        """
        for sport_key in SOCCER_SPORT_KEYS:
            events = await self._get_odds_for_league(sport_key)
            for event in events:
                if self._matches_team(event.get("home_team", ""), home_team) and \
                   self._matches_team(event.get("away_team", ""), away_team):
                    return self._summarize_event(event)
        return None

    def _summarize_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Average the decimal price for each outcome across every
        bookmaker's h2h market, and derive the (unadjusted) implied
        probability - honest about not removing the bookmaker's margin."""
        prices: Dict[str, List[float]] = {}

        for bookmaker in event.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                if market.get("key") != "h2h":
                    continue
                for outcome in market.get("outcomes", []):
                    name = outcome.get("name")
                    price = outcome.get("price")
                    if name and isinstance(price, (int, float)):
                        prices.setdefault(name, []).append(price)

        avg_prices = {name: round(sum(p) / len(p), 2) for name, p in prices.items() if p}
        implied_probs = {name: round(100 / price, 1) for name, price in avg_prices.items() if price}

        return {
            "commence_time": event.get("commence_time"),
            "bookmakers_count": len(event.get("bookmakers", [])),
            "avg_decimal_odds": avg_prices,
            "implied_probability_pct": implied_probs,
        }
