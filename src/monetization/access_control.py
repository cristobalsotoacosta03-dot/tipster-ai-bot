"""
Access Control System for VIP management.
Controls access to VIP features and group based on subscription status.
"""
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, timedelta

from config.settings import settings

logger = logging.getLogger(__name__)


class AccessControl:
    """
    Manages VIP access control and permissions.
    Checks subscription status and manages group access.
    """
    
    def __init__(self):
        """Initialize access control."""
        # In production, this would use a database
        # For now, we'll use in-memory storage
        self.vip_users: Dict[int, Dict[str, Any]] = {}
        self.user_analyses: Dict[int, Dict[str, Any]] = {}
        
        logger.info("Access Control initialized")
    
    def is_vip_user(self, user_id: int) -> bool:
        """
        Check if user has active VIP subscription.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if user is VIP, False otherwise
        """
        if user_id not in self.vip_users:
            return False
        
        user_data = self.vip_users[user_id]
        
        # Check if subscription is still active
        if user_data.get("expires_at"):
            expires_at = datetime.fromisoformat(user_data["expires_at"])
            if datetime.now() < expires_at:
                return True
            else:
                # Subscription expired, remove from VIP
                logger.info(f"VIP subscription expired for user {user_id}")
                del self.vip_users[user_id]
                return False
        
        return False
    
    def grant_vip_access(
        self,
        user_id: int,
        username: str,
        subscription_type: str = "monthly",
        duration_days: int = 30
    ) -> bool:
        """
        Grant VIP access to user.
        
        Args:
            user_id: Telegram user ID
            username: Telegram username
            subscription_type: "monthly" or "yearly"
            duration_days: Duration of subscription in days
            
        Returns:
            True if successful, False otherwise
        """
        try:
            expires_at = datetime.now() + timedelta(days=duration_days)
            
            self.vip_users[user_id] = {
                "user_id": user_id,
                "username": username,
                "subscription_type": subscription_type,
                "granted_at": datetime.now().isoformat(),
                "expires_at": expires_at.isoformat(),
                "is_active": True
            }
            
            logger.info(f"VIP access granted to user {user_id} ({username}) - {subscription_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error granting VIP access: {e}", exc_info=True)
            return False
    
    def revoke_vip_access(self, user_id: int) -> bool:
        """
        Revoke VIP access from user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if user_id in self.vip_users:
                del self.vip_users[user_id]
                logger.info(f"VIP access revoked for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error revoking VIP access: {e}", exc_info=True)
            return False
    
    def get_vip_status(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get VIP status for user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            VIP status dictionary or None
        """
        if user_id not in self.vip_users:
            return None
        
        user_data = self.vip_users[user_id]
        expires_at = datetime.fromisoformat(user_data["expires_at"])
        
        return {
            "is_vip": True,
            "subscription_type": user_data.get("subscription_type"),
            "expires_at": user_data.get("expires_at"),
            "days_remaining": (expires_at - datetime.now()).days,
            "username": user_data.get("username")
        }
    
    def send_vip_invite(self, user_id: int) -> Optional[str]:
        """
        Generate VIP group invite link.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Invite link or None
        """
        try:
            # In production, this would use Telegram API to create invite link
            # For now, return a placeholder
            invite_link = f"https://t.me/+{settings.telegram_vip_group_id}"
            
            logger.info(f"VIP invite generated for user {user_id}")
            return invite_link
            
        except Exception as e:
            logger.error(f"Error generating VIP invite: {e}", exc_info=True)
            return None
    
    def check_analysis_limit(self, user_id: int) -> Dict[str, Any]:
        """
        Check if user has reached analysis limit.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Dictionary with limit status
        """
        # VIP users have unlimited access
        if self.is_vip_user(user_id):
            return {
                "can_analyze": True,
                "analyses_used": 0,
                "analyses_limit": "Ilimitado",
                "is_vip": True
            }
        
        # Free users have daily limits
        today = datetime.now().date()
        
        if user_id not in self.user_analyses:
            self.user_analyses[user_id] = {
                "date": today.isoformat(),
                "count": 0
            }
        
        user_data = self.user_analyses[user_id]
        
        # Reset counter if it's a new day
        if user_data["date"] != today.isoformat():
            user_data["date"] = today.isoformat()
            user_data["count"] = 0
        
        analyses_used = user_data["count"]
        analyses_limit = settings.free_tips_per_day
        can_analyze = analyses_used < analyses_limit
        
        return {
            "can_analyze": can_analyze,
            "analyses_used": analyses_used,
            "analyses_limit": analyses_limit,
            "is_vip": False
        }
    
    def increment_analysis_count(self, user_id: int) -> bool:
        """
        Increment analysis count for free user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if successful, False if limit reached
        """
        # VIP users don't have limits
        if self.is_vip_user(user_id):
            return True
        
        # Check limit first
        limit_status = self.check_analysis_limit(user_id)
        
        if not limit_status["can_analyze"]:
            logger.warning(f"User {user_id} reached analysis limit")
            return False
        
        # Increment count
        if user_id not in self.user_analyses:
            today = datetime.now().date()
            self.user_analyses[user_id] = {
                "date": today.isoformat(),
                "count": 0
            }
        
        self.user_analyses[user_id]["count"] += 1
        logger.info(f"Analysis count incremented for user {user_id}: {self.user_analyses[user_id]['count']}")
        
        return True
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get statistics for user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            User statistics dictionary
        """
        is_vip = self.is_vip_user(user_id)
        vip_status = self.get_vip_status(user_id) if is_vip else None
        limit_status = self.check_analysis_limit(user_id)
        
        return {
            "user_id": user_id,
            "is_vip": is_vip,
            "vip_status": vip_status,
            "analyses_today": limit_status["analyses_used"],
            "analyses_limit": limit_status["analyses_limit"],
            "can_analyze": limit_status["can_analyze"]
        }
    
    def get_all_vip_users(self) -> List[Dict[str, Any]]:
        """
        Get all active VIP users.
        
        Returns:
            List of VIP user dictionaries
        """
        active_vips = []
        
        for user_id, user_data in self.vip_users.items():
            if self.is_vip_user(user_id):
                active_vips.append({
                    "user_id": user_id,
                    "username": user_data.get("username"),
                    "subscription_type": user_data.get("subscription_type"),
                    "expires_at": user_data.get("expires_at")
                })
        
        return active_vips
    
    def cleanup_expired_subscriptions(self) -> int:
        """
        Remove expired subscriptions.
        
        Returns:
            Number of expired subscriptions removed
        """
        removed = 0
        current_time = datetime.now()
        
        expired_users = []
        for user_id, user_data in self.vip_users.items():
            expires_at = datetime.fromisoformat(user_data["expires_at"])
            if current_time >= expires_at:
                expired_users.append(user_id)
        
        for user_id in expired_users:
            del self.vip_users[user_id]
            removed += 1
            logger.info(f"Removed expired subscription for user {user_id}")
        
        if removed > 0:
            logger.info(f"Cleaned up {removed} expired subscriptions")
        
        return removed
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get access control statistics.
        
        Returns:
            Statistics dictionary
        """
        active_vips = len([uid for uid in self.vip_users.keys() if self.is_vip_user(uid)])
        total_users = len(set(list(self.vip_users.keys()) + list(self.user_analyses.keys())))
        
        return {
            "total_users": total_users,
            "active_vips": active_vips,
            "free_users": total_users - active_vips,
            "analyses_today": sum(
                data["count"] for data in self.user_analyses.values()
                if data["date"] == datetime.now().date().isoformat()
            )
        }