"""
Tests for Access Control System.
"""
import pytest
from datetime import datetime, timedelta
from src.monetization.access_control import AccessControl


class TestAccessControl:
    """Test suite for AccessControl."""
    
    @pytest.fixture
    def access_control(self):
        """Create AccessControl instance."""
        return AccessControl()
    
    def test_access_control_initialization(self, access_control):
        """Test AccessControl initialization."""
        assert access_control is not None
        assert len(access_control.vip_users) == 0
        assert len(access_control.user_analyses) == 0
    
    def test_grant_vip_access(self, access_control):
        """Test granting VIP access."""
        user_id = 123456
        username = "testuser"
        
        result = access_control.grant_vip_access(
            user_id=user_id,
            username=username,
            subscription_type="monthly",
            duration_days=30
        )
        
        assert result is True
        assert access_control.is_vip_user(user_id) is True
        
        vip_status = access_control.get_vip_status(user_id)
        assert vip_status is not None
        assert vip_status["is_vip"] is True
        assert vip_status["subscription_type"] == "monthly"
        assert vip_status["username"] == username
    
    def test_revoke_vip_access(self, access_control):
        """Test revoking VIP access."""
        user_id = 123456
        
        # Grant access first
        access_control.grant_vip_access(user_id, "testuser")
        assert access_control.is_vip_user(user_id) is True
        
        # Revoke access
        result = access_control.revoke_vip_access(user_id)
        assert result is True
        assert access_control.is_vip_user(user_id) is False
    
    def test_vip_expiration(self, access_control):
        """Test VIP subscription expiration."""
        user_id = 123456
        
        # Grant access with 1 day duration
        access_control.grant_vip_access(
            user_id=user_id,
            username="testuser",
            duration_days=1
        )
        
        assert access_control.is_vip_user(user_id) is True
        
        # Simulate expiration by modifying the expiry date
        user_data = access_control.vip_users[user_id]
        user_data["expires_at"] = (datetime.now() - timedelta(days=1)).isoformat()
        
        # Check if expired
        assert access_control.is_vip_user(user_id) is False
        assert user_id not in access_control.vip_users
    
    def test_check_analysis_limit_vip(self, access_control):
        """Test analysis limit check for VIP users."""
        user_id = 123456
        
        # Grant VIP access
        access_control.grant_vip_access(user_id, "testuser")
        
        # VIP users should have unlimited access
        limit_status = access_control.check_analysis_limit(user_id)
        assert limit_status["can_analyze"] is True
        assert limit_status["analyses_limit"] == "Ilimitado"
        assert limit_status["is_vip"] is True
    
    def test_check_analysis_limit_free(self, access_control):
        """Test analysis limit check for free users."""
        user_id = 123456
        
        # Free user should have limited access
        limit_status = access_control.check_analysis_limit(user_id)
        assert limit_status["can_analyze"] is True
        assert limit_status["analyses_limit"] == 2  # Default free limit
        assert limit_status["is_vip"] is False
        assert limit_status["analyses_used"] == 0
    
    def test_increment_analysis_count(self, access_control):
        """Test incrementing analysis count."""
        user_id = 123456
        
        # Increment for free user
        result = access_control.increment_analysis_count(user_id)
        assert result is True
        
        limit_status = access_control.check_analysis_limit(user_id)
        assert limit_status["analyses_used"] == 1
        
        # Increment again
        result = access_control.increment_analysis_count(user_id)
        assert result is True
        
        limit_status = access_control.check_analysis_limit(user_id)
        assert limit_status["analyses_used"] == 2
        
        # Third increment should fail (limit reached)
        result = access_control.increment_analysis_count(user_id)
        assert result is False
    
    def test_get_user_stats(self, access_control):
        """Test getting user statistics."""
        user_id = 123456
        
        # Free user stats
        stats = access_control.get_user_stats(user_id)
        assert stats["user_id"] == user_id
        assert stats["is_vip"] is False
        assert stats["analyses_today"] == 0
        
        # Grant VIP and check again
        access_control.grant_vip_access(user_id, "testuser")
        stats = access_control.get_user_stats(user_id)
        assert stats["is_vip"] is True
        assert stats["vip_status"] is not None
    
    def test_get_all_vip_users(self, access_control):
        """Test getting all VIP users."""
        # Grant VIP to multiple users
        access_control.grant_vip_access(123, "user1")
        access_control.grant_vip_access(456, "user2")
        
        vip_users = access_control.get_all_vip_users()
        assert len(vip_users) == 2
        assert any(u["user_id"] == 123 for u in vip_users)
        assert any(u["user_id"] == 456 for u in vip_users)
    
    def test_cleanup_expired_subscriptions(self, access_control):
        """Test cleaning up expired subscriptions."""
        # Grant VIP with 1 day duration
        access_control.grant_vip_access(123, "user1", duration_days=1)
        access_control.grant_vip_access(456, "user2", duration_days=30)
        
        # Simulate expiration for user1
        user_data = access_control.vip_users[123]
        user_data["expires_at"] = (datetime.now() - timedelta(days=1)).isoformat()
        
        # Cleanup
        removed = access_control.cleanup_expired_subscriptions()
        assert removed == 1
        assert 123 not in access_control.vip_users
        assert 456 in access_control.vip_users
    
    def test_get_stats(self, access_control):
        """Test getting access control statistics."""
        # Add some users
        access_control.grant_vip_access(123, "user1")
        access_control.grant_vip_access(456, "user2")
        access_control.increment_analysis_count(789)
        
        stats = access_control.get_stats()
        assert stats["active_vips"] == 2
        assert stats["total_users"] == 3
        assert stats["free_users"] == 1
        assert stats["analyses_today"] == 1