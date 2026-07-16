"""
Payment Handler - Stripe Integration.
Manages subscriptions, payments, and webhooks for VIP access.
"""
from typing import Optional, Dict, Any
import stripe
import logging
from datetime import datetime

from config.settings import settings

logger = logging.getLogger(__name__)


class PaymentHandler:
    """
    Handles Stripe payments and subscriptions.
    Manages checkout sessions, webhooks, and subscription lifecycle.
    """
    
    def __init__(self):
        """Initialize Stripe with API key."""
        stripe.api_key = settings.stripe_api_key
        self.webhook_secret = settings.stripe_webhook_secret
        self.monthly_price_id = settings.stripe_price_id_monthly
        self.yearly_price_id = settings.stripe_price_id_yearly
        
        logger.info("Payment Handler initialized with Stripe")
    
    def create_checkout_session(
        self,
        user_id: int,
        username: str,
        price_type: str = "monthly",
        bot_username: str = "TuBot"
    ) -> Optional[Dict[str, Any]]:
        """
        Create Stripe checkout session for subscription.

        Args:
            user_id: Telegram user ID
            username: Telegram username
            price_type: "monthly" or "yearly"
            bot_username: Telegram bot username (without @), used to build
                the redirect links back into the chat after checkout

        Returns:
            Checkout session dictionary with URL
        """
        try:
            # Select price ID
            price_id = self.monthly_price_id if price_type == "monthly" else self.yearly_price_id

            # Create checkout session
            session = stripe.checkout.Session.create(
                customer_email=None,  # Will be collected by Stripe
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                mode="subscription",
                success_url=f"https://t.me/{bot_username}?start=success",
                cancel_url=f"https://t.me/{bot_username}?start=cancel",
                metadata={
                    "user_id": str(user_id),
                    "username": username or "unknown",
                    "price_type": price_type
                }
            )
            
            logger.info(f"Checkout session created for user {user_id}: {session.id}")
            
            return {
                "session_id": session.id,
                "url": session.url,
                "price_type": price_type
            }
            
        except Exception as e:
            logger.error(f"Error creating checkout session: {e}", exc_info=True)
            return None
    
    def handle_webhook(self, payload: bytes, signature: str) -> Optional[Dict[str, Any]]:
        """
        Handle Stripe webhook events.
        
        Args:
            payload: Webhook payload bytes
            signature: Stripe signature header
            
        Returns:
            Event data dictionary or None
        """
        try:
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            
            event_type = event["type"]
            event_data = event["data"]["object"]
            
            logger.info(f"Received webhook event: {event_type}")
            
            # Handle different event types
            if event_type == "checkout.session.completed":
                return self._handle_checkout_completed(event_data)
            elif event_type == "customer.subscription.created":
                return self._handle_subscription_created(event_data)
            elif event_type == "customer.subscription.updated":
                return self._handle_subscription_updated(event_data)
            elif event_type == "customer.subscription.deleted":
                return self._handle_subscription_deleted(event_data)
            elif event_type == "invoice.payment_succeeded":
                return self._handle_payment_succeeded(event_data)
            elif event_type == "invoice.payment_failed":
                return self._handle_payment_failed(event_data)
            else:
                logger.info(f"Unhandled event type: {event_type}")
                return None
                
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Webhook signature verification failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error handling webhook: {e}", exc_info=True)
            return None
    
    def _handle_checkout_completed(self, session: Dict) -> Dict[str, Any]:
        """Handle checkout.session.completed event."""
        metadata = session.get("metadata", {})
        user_id = metadata.get("user_id")
        subscription_id = session.get("subscription")

        logger.info(f"Checkout completed for user {user_id}, subscription: {subscription_id}")

        return {
            "event": "checkout_completed",
            "user_id": int(user_id) if user_id else None,
            "username": metadata.get("username"),
            "price_type": metadata.get("price_type", "monthly"),
            "subscription_id": subscription_id,
            "customer_id": session.get("customer"),
            "amount_total": (session.get("amount_total") or 0) / 100,
        }
    
    def _handle_subscription_created(self, subscription: Dict) -> Dict[str, Any]:
        """Handle customer.subscription.created event."""
        customer_id = subscription.get("customer")
        status = subscription.get("status")
        
        logger.info(f"Subscription created for customer {customer_id}, status: {status}")
        
        return {
            "event": "subscription_created",
            "customer_id": customer_id,
            "status": status,
            "current_period_end": subscription.get("current_period_end"),
        }
    
    def _handle_subscription_updated(self, subscription: Dict) -> Dict[str, Any]:
        """Handle customer.subscription.updated event."""
        customer_id = subscription.get("customer")
        status = subscription.get("status")
        
        logger.info(f"Subscription updated for customer {customer_id}, status: {status}")
        
        return {
            "event": "subscription_updated",
            "customer_id": customer_id,
            "status": status,
            "current_period_end": subscription.get("current_period_end"),
        }
    
    def _handle_subscription_deleted(self, subscription: Dict) -> Dict[str, Any]:
        """Handle customer.subscription.deleted event."""
        customer_id = subscription.get("customer")
        
        logger.info(f"Subscription deleted for customer {customer_id}")
        
        return {
            "event": "subscription_deleted",
            "customer_id": customer_id,
        }
    
    def _handle_payment_succeeded(self, invoice: Dict) -> Dict[str, Any]:
        """Handle invoice.payment_succeeded event."""
        customer_id = invoice.get("customer")
        amount_paid = invoice.get("amount_paid", 0) / 100  # Convert from cents
        
        logger.info(f"Payment succeeded for customer {customer_id}: €{amount_paid:.2f}")
        
        return {
            "event": "payment_succeeded",
            "customer_id": customer_id,
            "amount": amount_paid,
        }
    
    def _handle_payment_failed(self, invoice: Dict) -> Dict[str, Any]:
        """Handle invoice.payment_failed event."""
        customer_id = invoice.get("customer")
        
        logger.warning(f"Payment failed for customer {customer_id}")
        
        return {
            "event": "payment_failed",
            "customer_id": customer_id,
        }
    
    def get_subscription_status(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Get subscription status for a customer.
        
        Args:
            customer_id: Stripe customer ID
            
        Returns:
            Subscription status dictionary
        """
        try:
            subscriptions = stripe.Subscription.list(
                customer=customer_id,
                limit=1
            )
            
            if not subscriptions.data:
                return None
            
            subscription = subscriptions.data[0]
            
            return {
                "status": subscription.status,
                "current_period_end": subscription.current_period_end,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "price_type": "monthly" if subscription.items.data[0].price.id == self.monthly_price_id else "yearly"
            }
            
        except Exception as e:
            logger.error(f"Error getting subscription status: {e}", exc_info=True)
            return None
    
    def cancel_subscription(self, subscription_id: str) -> bool:
        """
        Cancel subscription at period end.
        
        Args:
            subscription_id: Stripe subscription ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            
            logger.info(f"Subscription {subscription_id} canceled at period end")
            return True
            
        except Exception as e:
            logger.error(f"Error canceling subscription: {e}", exc_info=True)
            return False
    
    def create_customer_portal_session(self, customer_id: str, bot_username: str = "TuBot") -> Optional[str]:
        """
        Create customer portal session for managing subscription.

        Args:
            customer_id: Stripe customer ID
            bot_username: Telegram bot username (without @), used to build
                the return link back into the chat

        Returns:
            Portal session URL
        """
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=f"https://t.me/{bot_username}"
            )
            
            return session.url
            
        except Exception as e:
            logger.error(f"Error creating portal session: {e}", exc_info=True)
            return None
    
    def get_payment_history(self, customer_id: str, limit: int = 10) -> list[Dict]:
        """
        Get payment history for a customer.
        
        Args:
            customer_id: Stripe customer ID
            limit: Maximum number of payments to retrieve
            
        Returns:
            List of payment dictionaries
        """
        try:
            invoices = stripe.Invoice.list(
                customer=customer_id,
                limit=limit
            )
            
            payments = []
            for invoice in invoices.data:
                payments.append({
                    "date": datetime.fromtimestamp(invoice.created).isoformat(),
                    "amount": invoice.amount_paid / 100,
                    "status": invoice.status,
                    "invoice_url": invoice.hosted_invoice_url
                })
            
            return payments
            
        except Exception as e:
            logger.error(f"Error getting payment history: {e}", exc_info=True)
            return []
    
    def health_check(self) -> bool:
        """
        Check if Stripe API is accessible.
        
        Returns:
            True if API is working, False otherwise
        """
        try:
            # Try to retrieve account info
            stripe.Account.retrieve()
            return True
        except Exception as e:
            logger.error(f"Stripe health check failed: {e}")
            return False