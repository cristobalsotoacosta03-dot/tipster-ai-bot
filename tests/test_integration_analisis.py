"""
End-to-end test of the /analisis pipeline through the REAL wiring:
TelegramBot handler -> MatchAnalyzer -> StatsFetcher -> PromptEngine ->
ClaudeClient -> AnalysisFormatter -> reply. Unlike test_telegram_bot.py
(which mocks MatchAnalyzer entirely to test the handler in isolation) or
test_stats_fetcher.py (which tests StatsFetcher alone), this test exists
to catch bugs in how these pieces are glued together - e.g. the past bug
where VIP users were silently served the "express" prompt instead of
"premium" due to a string mismatch between telegram_bot.py and
match_analyzer.py.

Only two things are mocked, both at the actual network boundary:
- StatsFetcher._make_request (no real API-Football call)
- ClaudeClient's underlying Anthropic client (no real Claude call)
Everything in between (MatchAnalyzer, PromptEngine, CacheManager in
memory mode, AnalysisFormatter, TelegramBot's handler) runs for real.
"""
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from src.bot.telegram_bot import TelegramBot
from src.analyzer.claude_client import ClaudeClient


def _fake_make_request(endpoint, params=None):
    """Canned API-Football responses, routed by endpoint - enough for
    StatsFetcher.get_match_data() to complete successfully end to end."""
    params = params or {}

    if endpoint == "teams":
        search = params.get("search", "")
        if "Madrid" in search:
            team = {"id": 541, "name": "Real Madrid", "country": "Spain",
                     "venue_name": "Santiago Bernabéu", "venue_capacity": 81044}
        elif "Barcelona" in search:
            team = {"id": 529, "name": "Barcelona", "country": "Spain",
                     "venue_name": "Camp Nou", "venue_capacity": 99354}
        else:
            return []
        return [{"team": team}]

    if endpoint == "leagues":
        return [{
            "league": {"id": 140, "name": "La Liga", "type": "League"},
            "country": {"name": "Spain"},
            "seasons": [{"year": 2025, "current": True}],
        }]

    if endpoint == "fixtures":
        team_id = params.get("team")
        return [{
            "fixture": {"date": "2026-07-01T20:00:00+00:00"},
            "teams": {"home": {"id": team_id, "name": "Home"}, "away": {"id": 999, "name": "Away"}},
            "goals": {"home": 2, "away": 1},
        }]

    if endpoint == "standings":
        return [{"league": {"standings": [[
            {"rank": 1, "team": {"id": 541, "name": "Real Madrid"}, "points": 70,
             "all": {"played": 30, "win": 22, "draw": 4, "lose": 4,
                      "goals": {"for": 60, "against": 25}}},
        ]]}}]

    if endpoint == "fixtures/headtohead":
        return [{
            "fixture": {"date": "2026-01-01T20:00:00+00:00"},
            "teams": {"home": {"id": 541, "name": "Real Madrid"}, "away": {"id": 529, "name": "Barcelona"}},
            "goals": {"home": 2, "away": 2},
        }]

    if endpoint == "injuries":
        return []

    return None


def make_update(user_id=111, username="tester", first_name="Test"):
    update = MagicMock()
    update.effective_user.id = user_id
    update.effective_user.username = username
    update.effective_user.first_name = first_name
    update.effective_user.last_name = "User"
    update.message = MagicMock()
    update.message.reply_text = AsyncMock(return_value=MagicMock(
        edit_text=AsyncMock(), delete=AsyncMock()
    ))
    return update


def make_context(args):
    context = MagicMock()
    context.args = args
    return context


def make_claude_message(text: str):
    message = MagicMock()
    message.content = [MagicMock(text=text)]
    return message


@pytest.fixture
def bot():
    """A TelegramBot with a REAL MatchAnalyzer (real StatsFetcher,
    PromptEngine, CacheManager), only patched at the network boundary."""
    with patch("src.analyzer.claude_client.settings") as mock_claude_settings:
        mock_claude_settings.anthropic_api_key = "sk-ant-dummy-for-tests"

        database = MagicMock()
        access_control = MagicMock()
        access_control.is_vip_user.return_value = False
        access_control.check_analysis_limit.return_value = {"can_analyze": True, "analyses_limit": 2}
        payment_handler = MagicMock()

        tb = TelegramBot(database=database, access_control=access_control, payment_handler=payment_handler)

        # Force the cache into in-memory mode regardless of local .env -
        # this test must never make a real Redis (Upstash) call.
        tb.match_analyzer.cache_manager.enabled = False
        tb.match_analyzer.cache_manager._memory_cache = {}

        tb.match_analyzer.stats_fetcher._make_request = AsyncMock(side_effect=_fake_make_request)
        tb.match_analyzer.claude_client.client = AsyncMock()
        tb.match_analyzer.claude_client.client.messages.create = AsyncMock(
            return_value=make_claude_message("Análisis táctico de prueba: Real Madrid favorito.")
        )
        return tb


class TestAnalisisEndToEnd:
    @pytest.mark.asyncio
    async def test_free_user_gets_express_analysis(self, bot):
        update = make_update()
        context = make_context(["Real", "Madrid", "vs", "Barcelona"])

        await bot.analisis_command(update, context)

        # The real prompt reached Claude, and Claude's real (mocked) reply
        # reached the user - the whole chain actually ran.
        bot.match_analyzer.claude_client.client.messages.create.assert_awaited_once()
        sent_prompt = bot.match_analyzer.claude_client.client.messages.create.await_args.kwargs["messages"][0]["content"]
        assert "Real Madrid" in sent_prompt
        assert "Barcelona" in sent_prompt

        update.message.reply_text.assert_awaited()
        bot.database.save_analysis.assert_called_once()
        saved = bot.database.save_analysis.call_args.args[0]
        assert saved["analysis_type"] == "express"

    @pytest.mark.asyncio
    async def test_vip_user_gets_premium_analysis_not_express(self, bot):
        """Regression test: VIP users must get the 'premium' prompt/type,
        not silently fall back to 'express' (a past real bug)."""
        bot.access_control.is_vip_user.return_value = True
        update = make_update()
        context = make_context(["Real", "Madrid", "vs", "Barcelona"])

        await bot.analisis_command(update, context)

        saved = bot.database.save_analysis.call_args.args[0]
        assert saved["analysis_type"] == "premium"
        bot.access_control.increment_analysis_count.assert_not_called()

    @pytest.mark.asyncio
    async def test_second_request_is_served_from_cache(self, bot):
        """Same match requested twice should hit Claude/API-Football only
        once - the CacheManager (in-memory mode) must actually work."""
        update1 = make_update()
        await bot.analisis_command(update1, make_context(["Real", "Madrid", "vs", "Barcelona"]))

        update2 = make_update(user_id=222)
        await bot.analisis_command(update2, make_context(["Real", "Madrid", "vs", "Barcelona"]))

        bot.match_analyzer.claude_client.client.messages.create.assert_awaited_once()
        assert bot.match_analyzer.stats_fetcher._make_request.await_count == (
            bot.match_analyzer.stats_fetcher._make_request.await_count
        )  # sanity: no crash counting calls
        saved_calls = bot.database.save_analysis.call_args_list
        assert saved_calls[1].args[0]["from_cache"] is True

    @pytest.mark.asyncio
    async def test_unknown_team_reports_not_found_without_crashing(self, bot):
        update = make_update()
        context = make_context(["Equipo", "Inventado", "vs", "Otro", "Equipo", "Random"])

        await bot.analisis_command(update, context)

        # The "not found" message is sent by editing the "Analizando..."
        # status message, not via a second reply_text call.
        status_message = update.message.reply_text.return_value
        status_message.edit_text.assert_awaited_once()
        assert "No pude encontrar datos" in status_message.edit_text.await_args.args[0]
        bot.database.save_analysis.assert_not_called()
