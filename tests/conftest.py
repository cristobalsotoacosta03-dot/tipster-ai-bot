"""
Shared pytest fixtures/setup.

Settings() requires several env vars with no defaults (telegram/Stripe
credentials). Locally, developers get these from their own .env file; in CI
(and here, before any test module imports config.settings) there is no
.env, so we set harmless dummy values for the required fields only. Real
secrets are never needed to run the test suite — nothing here talks to a
real Telegram/Stripe/Claude API.
"""
import os

os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test-telegram-bot-token")
os.environ.setdefault("TELEGRAM_ADMIN_ID", "123456789")
os.environ.setdefault("TELEGRAM_VIP_GROUP_ID", "-100123456789")
os.environ.setdefault("STRIPE_API_KEY", "sk_test_dummy")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "whsec_dummy")
os.environ.setdefault("STRIPE_PRICE_ID_MONTHLY", "price_dummy_monthly")
os.environ.setdefault("STRIPE_PRICE_ID_YEARLY", "price_dummy_yearly")
