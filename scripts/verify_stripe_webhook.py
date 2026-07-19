"""
One-off local verification that PaymentHandler.handle_webhook() actually
works with the REAL STRIPE_WEBHOOK_SECRET from .env (test mode) — signature
verification is pure local HMAC, no network call and no real charge
involved. Not a pytest test on purpose: it depends on a real secret being
present in .env, which CI and other machines won't have.

Run: .venv\\Scripts\\python.exe scripts\\verify_stripe_webhook.py
"""
import hashlib
import hmac
import json
import time

from config.settings import settings
from src.monetization.payment_handler import PaymentHandler


def sign_payload(payload: bytes, secret: str) -> str:
    """Build a Stripe-Signature header value the same way Stripe itself
    does: t=<timestamp>,v1=<hmac_sha256(f"{t}.{payload}", secret)>."""
    timestamp = int(time.time())
    signed_payload = f"{timestamp}.{payload.decode()}".encode()
    signature = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={signature}"


def main():
    handler = PaymentHandler()

    fake_event = {
        "id": "evt_test_verification",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_verification",
                "customer": "cus_test_verification",
                "subscription": "sub_test_verification",
                "amount_total": 2999,
                "metadata": {
                    "user_id": "999999999",
                    "username": "verification_test",
                    "price_type": "monthly",
                },
            }
        },
    }
    payload = json.dumps(fake_event).encode()
    signature = sign_payload(payload, settings.stripe_webhook_secret)

    result = handler.handle_webhook(payload, signature)

    print("=== Resultado ===")
    print(result)

    if result is None:
        print("\nFALLO: la firma no se verificó o el evento no se procesó. "
              "Revisa STRIPE_WEBHOOK_SECRET en .env.")
    elif result.get("event") == "checkout_completed" and result.get("user_id") == 999999999:
        print("\nOK: el webhook real de Stripe (modo test) verifica la firma "
              "y procesa checkout.session.completed correctamente.")
    else:
        print("\nAVISO: se procesó el evento pero con datos inesperados, revisar arriba.")


if __name__ == "__main__":
    main()
