"""
Smoke tests for TelegramBot handlers and the Stripe webhook endpoint.

These are not full-coverage tests — the bar here is the minimum needed for
an unattended, unsupervised change to this file to be safe: handlers must
not crash on the golden path or on obviously bad input, and the webhook
must not process (or crash on) an unverifiable Stripe event.

No real network calls: python-telegram-bot's Application.build() doesn't
hit the network at construction time, and everything that talks to
Telegram/Claude/Stripe/the DB is mocked.
"""
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from src.bot.telegram_bot import TelegramBot


def make_update(user_id=111, username="tester", first_name="Test", args_text=""):
    update = MagicMock()
    update.effective_user.id = user_id
    update.effective_user.username = username
    update.effective_user.first_name = first_name
    update.effective_user.last_name = "User"
    update.message = MagicMock()
    update.message.reply_text = AsyncMock(return_value=MagicMock(
        edit_text=AsyncMock(), delete=AsyncMock()
    ))
    update.message.text = args_text
    return update


def make_context(args=None):
    context = MagicMock()
    context.args = args or []
    return context


@pytest.fixture
def bot():
    with patch("src.bot.telegram_bot.MatchAnalyzer") as MockAnalyzer:
        instance = MockAnalyzer.return_value
        instance.claude_client.enabled = True
        instance.analyze_match = AsyncMock(return_value={
            "match_id": "real_madrid_vs_barcelona",
            "home_team": "Real Madrid",
            "away_team": "Barcelona",
            "analysis_type": "express",
            "analysis": "Análisis de prueba.",
            "match_data": {},
            "prompt_used": "prompt",
            "from_cache": False,
        })
        database = MagicMock()
        access_control = MagicMock()
        access_control.is_vip_user.return_value = False
        access_control.check_analysis_limit.return_value = {"can_analyze": True, "analyses_limit": 2}
        payment_handler = MagicMock()

        tb = TelegramBot(database=database, access_control=access_control, payment_handler=payment_handler)
        tb.analysis_formatter.format_analysis_for_telegram = MagicMock(return_value="formatted analysis")
        return tb


class TestStartCommand:
    @pytest.mark.asyncio
    async def test_start_registers_user_and_replies(self, bot):
        update = make_update()
        await bot.start_command(update, make_context())

        bot.database.create_or_update_user.assert_called_once()
        update.message.reply_text.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_start_does_not_crash_without_database(self, bot):
        bot.database = None
        update = make_update()
        await bot.start_command(update, make_context())
        update.message.reply_text.assert_awaited_once()


class TestStatusCommand:
    @pytest.mark.asyncio
    async def test_status_replies_without_crashing(self, bot):
        update = make_update()
        await bot.status_command(update, make_context())
        update.message.reply_text.assert_awaited_once()


class TestAnalisisCommand:
    @pytest.mark.asyncio
    async def test_analisis_happy_path(self, bot):
        update = make_update()
        context = make_context(args=["Real", "Madrid", "vs", "Barcelona"])

        await bot.analisis_command(update, context)

        bot.match_analyzer.analyze_match.assert_awaited_once()
        bot.database.save_analysis.assert_called_once()
        bot.access_control.increment_analysis_count.assert_called_once()

    @pytest.mark.asyncio
    async def test_analisis_shows_coming_soon_when_claude_disabled(self, bot):
        bot.match_analyzer.claude_client.enabled = False
        update = make_update()
        context = make_context(args=["Real", "Madrid", "vs", "Barcelona"])

        await bot.analisis_command(update, context)

        bot.match_analyzer.analyze_match.assert_not_awaited()
        update.message.reply_text.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_analisis_rejects_missing_args(self, bot):
        update = make_update()
        context = make_context(args=["Real"])

        await bot.analisis_command(update, context)

        bot.match_analyzer.analyze_match.assert_not_awaited()
        update.message.reply_text.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_analisis_blocked_at_free_tier_limit(self, bot):
        bot.access_control.check_analysis_limit.return_value = {"can_analyze": False, "analyses_limit": 2}
        update = make_update()
        context = make_context(args=["Real", "Madrid", "vs", "Barcelona"])

        await bot.analisis_command(update, context)

        bot.match_analyzer.analyze_match.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_analisis_handles_analyzer_returning_none(self, bot):
        bot.match_analyzer.analyze_match = AsyncMock(return_value=None)
        update = make_update()
        context = make_context(args=["Unknown", "FC", "vs", "Barcelona"])

        # Must not raise even though analyze_match found nothing.
        await bot.analisis_command(update, context)

        bot.database.save_analysis.assert_not_called()

    @pytest.mark.asyncio
    async def test_analisis_handles_unexpected_exception(self, bot):
        bot.match_analyzer.analyze_match = AsyncMock(side_effect=RuntimeError("boom"))
        update = make_update()
        context = make_context(args=["Real", "Madrid", "vs", "Barcelona"])

        # The handler's own try/except must catch this and reply, not propagate.
        await bot.analisis_command(update, context)

        assert update.message.reply_text.await_count >= 1


class TestStripeWebhook:
    def make_request(self, body: bytes, signature: str = "sig"):
        request = MagicMock()
        request.read = AsyncMock(return_value=body)
        request.headers = {"Stripe-Signature": signature}
        return request

    @pytest.mark.asyncio
    async def test_invalid_signature_returns_200_without_crashing(self, bot):
        bot.payment_handler.handle_webhook = MagicMock(return_value=None)
        request = self.make_request(b"{}", signature="bad-signature")

        response = await bot._handle_stripe_webhook(request)

        assert response.status == 200
        bot.access_control.grant_vip_access.assert_not_called()

    @pytest.mark.asyncio
    async def test_checkout_completed_grants_vip(self, bot):
        bot.payment_handler.handle_webhook = MagicMock(return_value={
            "event": "checkout_completed",
            "user_id": 111,
            "username": "tester",
            "price_type": "monthly",
            "subscription_id": "sub_123",
            "customer_id": "cus_123",
            "amount_total": 29.99,
        })
        # python-telegram-bot's Bot object is frozen (raises on setattr), so
        # mock at the TelegramBot method boundary instead of on bot.application.bot.
        bot._create_vip_invite_link = AsyncMock(return_value="https://t.me/joinchat/abc")
        bot.send_message = AsyncMock(return_value=True)
        request = self.make_request(b"{}", signature="good-signature")

        response = await bot._handle_stripe_webhook(request)

        assert response.status == 200
        bot.access_control.grant_vip_access.assert_called_once()
        bot.database.save_payment.assert_called_once()

    @pytest.mark.asyncio
    async def test_subscription_deleted_revokes_vip(self, bot):
        bot.payment_handler.handle_webhook = MagicMock(return_value={
            "event": "subscription_deleted",
            "customer_id": "cus_123",
        })
        bot.database.get_user_by_stripe_customer_id.return_value = {"user_id": 111}
        bot.send_message = AsyncMock(return_value=True)
        request = self.make_request(b"{}", signature="good-signature")

        response = await bot._handle_stripe_webhook(request)

        assert response.status == 200
        bot.access_control.revoke_vip_access.assert_called_once_with(111)
