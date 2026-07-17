"""
Tests for OddsProvider (The Odds API).
All HTTP calls are mocked - no real network requests, no API key required.
"""
from unittest.mock import AsyncMock
import pytest

from src.data.odds_provider import OddsProvider, SOCCER_SPORT_KEYS


class TestOddsProvider:

    @pytest.fixture
    def provider(self):
        return OddsProvider()

    @pytest.mark.asyncio
    async def test_find_match_odds_found_in_first_league(self, provider):
        provider._get_odds_for_league = AsyncMock(return_value=[
            {
                "commence_time": "2025-01-01T20:00:00Z",
                "home_team": "Real Madrid",
                "away_team": "Barcelona",
                "bookmakers": [
                    {
                        "key": "bet365",
                        "markets": [{
                            "key": "h2h",
                            "outcomes": [
                                {"name": "Real Madrid", "price": 2.0},
                                {"name": "Draw", "price": 3.5},
                                {"name": "Barcelona", "price": 3.8},
                            ],
                        }],
                    },
                    {
                        "key": "williamhill",
                        "markets": [{
                            "key": "h2h",
                            "outcomes": [
                                {"name": "Real Madrid", "price": 2.2},
                                {"name": "Draw", "price": 3.3},
                                {"name": "Barcelona", "price": 3.6},
                            ],
                        }],
                    },
                ],
            }
        ])

        result = await provider.find_match_odds("Real Madrid", "Barcelona")

        assert result is not None
        assert result["bookmakers_count"] == 2
        assert result["avg_decimal_odds"]["Real Madrid"] == 2.1  # (2.0 + 2.2) / 2
        assert result["implied_probability_pct"]["Real Madrid"] == round(100 / 2.1, 1)

    @pytest.mark.asyncio
    async def test_find_match_odds_not_found_in_any_league(self, provider):
        provider._get_odds_for_league = AsyncMock(return_value=[])

        result = await provider.find_match_odds("Unknown FC", "Another FC")

        assert result is None
        assert provider._get_odds_for_league.await_count == len(SOCCER_SPORT_KEYS)

    @pytest.mark.asyncio
    async def test_find_match_odds_stops_at_first_matching_league(self, provider):
        async def fake_get_odds(sport_key):
            if sport_key == SOCCER_SPORT_KEYS[1]:
                return [{
                    "commence_time": "2025-01-01T20:00:00Z",
                    "home_team": "Real Madrid",
                    "away_team": "Barcelona",
                    "bookmakers": [],
                }]
            return []

        provider._get_odds_for_league = AsyncMock(side_effect=fake_get_odds)

        result = await provider.find_match_odds("Real Madrid", "Barcelona")

        assert result is not None
        # Stopped as soon as it found a match - didn't scan every league.
        assert provider._get_odds_for_league.await_count == 2

    def test_summarize_event_with_no_bookmakers(self, provider):
        summary = provider._summarize_event({
            "commence_time": "2025-01-01T20:00:00Z",
            "home_team": "A", "away_team": "B",
            "bookmakers": [],
        })
        assert summary["avg_decimal_odds"] == {}
        assert summary["implied_probability_pct"] == {}
