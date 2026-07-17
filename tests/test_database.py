"""
Tests for Database Manager.
"""
from unittest.mock import MagicMock, patch
import pytest
import os
from src.data.database import DatabaseManager


class TestDatabaseManager:
    """Test suite for DatabaseManager."""
    
    @pytest.fixture
    def db_manager(self, tmp_path):
        """Create DatabaseManager with temporary database."""
        db_path = str(tmp_path / "test.db")
        return DatabaseManager(db_path)
    
    def test_database_initialization(self, db_manager):
        """Test database initialization."""
        assert db_manager is not None
        assert os.path.exists(db_manager.db_path)
    
    def test_create_or_update_user(self, db_manager):
        """Test user creation/update."""
        user_id = 123456
        username = "testuser"
        first_name = "Test"
        last_name = "User"
        
        result = db_manager.create_or_update_user(user_id, username, first_name, last_name)
        assert result is True
        
        # Update same user
        result = db_manager.create_or_update_user(user_id, "newusername", first_name, last_name)
        assert result is True
    
    def test_get_user(self, db_manager):
        """Test getting user from database."""
        user_id = 123456
        db_manager.create_or_update_user(user_id, "testuser", "Test", "User")
        
        user = db_manager.get_user(user_id)
        assert user is not None
        assert user["user_id"] == user_id
        assert user["username"] == "testuser"
        assert user["first_name"] == "Test"
    
    def test_get_nonexistent_user(self, db_manager):
        """Test getting non-existent user."""
        user = db_manager.get_user(999999)
        assert user is None
    
    def test_update_vip_status(self, db_manager):
        """Test updating VIP status."""
        user_id = 123456
        db_manager.create_or_update_user(user_id, "testuser", "Test", "User")
        
        # Update to VIP
        result = db_manager.update_vip_status(
            user_id=user_id,
            is_vip=True,
            subscription_type="monthly",
            expires_at="2024-12-31T23:59:59"
        )
        assert result is True
        
        user = db_manager.get_user(user_id)
        assert user["is_vip"] == 1
        assert user["subscription_type"] == "monthly"
    
    def test_save_analysis(self, db_manager):
        """Test saving analysis."""
        analysis_data = {
            "user_id": 123456,
            "match_id": "real_madrid_vs_barcelona",
            "home_team": "Real Madrid",
            "away_team": "Barcelona",
            "analysis_type": "full",
            "analysis": "Análisis de prueba...",
            "match_data": {},
            "from_cache": False,
            "tokens_used": 1000,
            "cost_eur": 0.05
        }
        
        analysis_id = db_manager.save_analysis(analysis_data)
        assert analysis_id is not None
        assert analysis_id > 0
    
    def test_get_user_analyses(self, db_manager):
        """Test getting user analyses."""
        user_id = 123456
        
        # Save multiple analyses
        for i in range(5):
            analysis_data = {
                "user_id": user_id,
                "match_id": f"match_{i}",
                "home_team": "Team A",
                "away_team": "Team B",
                "analysis_type": "full",
                "analysis": f"Analysis {i}",
                "from_cache": False
            }
            db_manager.save_analysis(analysis_data)
        
        # Get analyses
        analyses = db_manager.get_user_analyses(user_id, limit=10)
        assert len(analyses) == 5
        assert analyses[0]["analysis_text"] == "Analysis 4"  # Most recent first
    
    def test_save_payment(self, db_manager):
        """Test saving payment."""
        payment_data = {
            "user_id": 123456,
            "stripe_payment_id": "pi_123456",
            "stripe_customer_id": "cus_123456",
            "amount_eur": 29.99,
            "status": "succeeded",
            "subscription_type": "monthly"
        }
        
        payment_id = db_manager.save_payment(payment_data)
        assert payment_id is not None
        assert payment_id > 0
    
    def test_save_subscription(self, db_manager):
        """Test saving subscription."""
        subscription_data = {
            "user_id": 123456,
            "stripe_subscription_id": "sub_123456",
            "status": "active",
            "price_type": "monthly",
            "current_period_start": "2024-12-01T00:00:00",
            "current_period_end": "2024-12-31T23:59:59",
            "cancel_at_period_end": False
        }
        
        subscription_id = db_manager.save_subscription(subscription_data)
        assert subscription_id is not None
        assert subscription_id > 0
    
    def test_get_stats(self, db_manager):
        """Test getting database statistics."""
        # Add some data
        db_manager.create_or_update_user(123, "user1", "User", "One")
        db_manager.create_or_update_user(456, "user2", "User", "Two")
        
        stats = db_manager.get_stats()
        assert stats["total_users"] == 2
        assert stats["vip_users"] == 0
        assert stats["free_users"] == 2
        assert stats["total_analyses"] == 0
    
    def test_health_check(self, db_manager):
        """Test database health check."""
        result = db_manager.health_check()
        assert result is True
    
    def test_daily_stats_update(self, db_manager):
        """Test daily stats update."""
        result = db_manager.update_daily_stats()
        assert result is True


class TestDatabaseManagerPostgresSelection:
    """
    DATABASE_URL is meant to switch the driver from SQLite to Postgres
    without touching production (nobody has set it yet, and there's no free
    Postgres instance available to test against here). These tests only
    verify the driver-selection wiring — the '?' -> '%s' query translation,
    which class attribute gets used, and the RETURNING-id insert path — with
    psycopg2 mocked out. They do not, and cannot, prove the SQL is valid
    against a real Postgres server.
    """

    @pytest.fixture
    def pg_manager(self, tmp_path):
        with patch("src.data.database.settings") as mock_settings, \
             patch("src.data.database.psycopg2") as mock_psycopg2:
            mock_settings.database_url = "postgresql://user:pass@host/db"

            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = {"id": 42, "count": 0, "total": 0.0}
            mock_cursor.fetchall.return_value = []
            mock_psycopg2.connect.return_value = mock_conn
            mock_psycopg2.extras.RealDictCursor = MagicMock()

            manager = DatabaseManager(str(tmp_path / "unused.db"))
            manager._mock_conn = mock_conn
            manager._mock_cursor = mock_cursor
            yield manager

    def test_uses_postgres_when_database_url_is_set(self, pg_manager):
        assert pg_manager.use_postgres is True

    def test_query_placeholders_are_translated_for_postgres(self, pg_manager):
        assert pg_manager._q("SELECT * FROM users WHERE user_id = ?") == \
            "SELECT * FROM users WHERE user_id = %s"

    def test_sqlite_queries_are_left_untouched(self, tmp_path):
        sqlite_manager = DatabaseManager(str(tmp_path / "sqlite.db"))
        assert sqlite_manager.use_postgres is False
        assert sqlite_manager._q("SELECT * FROM users WHERE user_id = ?") == \
            "SELECT * FROM users WHERE user_id = ?"

    def test_save_analysis_uses_returning_id_on_postgres(self, pg_manager):
        analysis_id = pg_manager.save_analysis({
            "user_id": 1, "match_id": "a_vs_b", "home_team": "A", "away_team": "B",
            "analysis_type": "full", "analysis": "text",
        })

        assert analysis_id == 42
        executed_sql = pg_manager._mock_cursor.execute.call_args[0][0]
        assert "RETURNING id" in executed_sql
        assert "%s" in executed_sql