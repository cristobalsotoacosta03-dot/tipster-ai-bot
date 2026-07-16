"""
Database Manager - SQLite Integration.
Manages persistent storage for users, analyses, and subscriptions.
"""
from typing import Optional, Dict, Any, List
import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path

from config.settings import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    SQLite database manager for persistent storage.
    Handles users, analyses, subscriptions, and analytics.
    """
    
    def __init__(self, db_path: str = "data/tipster_bot.db"):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        
        # Create data directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        logger.info(f"Database Manager initialized at {db_path}")
    
    def _get_connection(self) -> sqlite3.Connection:
        """
        Get database connection.
        
        Returns:
            SQLite connection object
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    def _init_database(self) -> None:
        """Initialize database tables."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    is_vip BOOLEAN DEFAULT 0,
                    vip_started_at TEXT,
                    vip_expires_at TEXT,
                    subscription_type TEXT,
                    stripe_customer_id TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Analyses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    match_id TEXT NOT NULL,
                    home_team TEXT NOT NULL,
                    away_team TEXT NOT NULL,
                    analysis_type TEXT NOT NULL,
                    analysis_text TEXT NOT NULL,
                    match_data TEXT,
                    prompt_used TEXT,
                    from_cache BOOLEAN DEFAULT 0,
                    tokens_used INTEGER,
                    cost_eur REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Payments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    stripe_payment_id TEXT UNIQUE,
                    stripe_customer_id TEXT,
                    amount_eur REAL NOT NULL,
                    currency TEXT DEFAULT 'EUR',
                    status TEXT NOT NULL,
                    subscription_type TEXT,
                    payment_method TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Subscriptions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    stripe_subscription_id TEXT UNIQUE,
                    status TEXT NOT NULL,
                    price_type TEXT,
                    current_period_start TEXT,
                    current_period_end TEXT,
                    cancel_at_period_end BOOLEAN DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Daily stats table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    total_users INTEGER DEFAULT 0,
                    active_users INTEGER DEFAULT 0,
                    new_users INTEGER DEFAULT 0,
                    vip_subscriptions INTEGER DEFAULT 0,
                    analyses_generated INTEGER DEFAULT 0,
                    revenue_eur REAL DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date)
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON analyses(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analyses_match_id ON analyses(match_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id)")
            
            conn.commit()
            conn.close()
            
            logger.info("Database tables initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}", exc_info=True)
            raise
    
    # ==================== USER MANAGEMENT ====================
    
    def create_or_update_user(
        self,
        user_id: int,
        username: str,
        first_name: str,
        last_name: str
    ) -> bool:
        """
        Create or update user in database.
        
        Args:
            user_id: Telegram user ID
            username: Telegram username
            first_name: User's first name
            last_name: User's last name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Upsert user
            cursor.execute("""
                INSERT INTO users (user_id, username, first_name, last_name, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username = excluded.username,
                    first_name = excluded.first_name,
                    last_name = excluded.last_name,
                    updated_at = excluded.updated_at
            """, (user_id, username, first_name, last_name, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"User {user_id} created/updated in database")
            return True
            
        except Exception as e:
            logger.error(f"Error creating/updating user {user_id}: {e}", exc_info=True)
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user from database.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            User dictionary or None
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            
            conn.close()
            
            if row:
                return dict(row)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}", exc_info=True)
            return None

    def get_user_by_stripe_customer_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by their Stripe customer ID.

        Args:
            customer_id: Stripe customer ID

        Returns:
            User dictionary or None
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM users WHERE stripe_customer_id = ?", (customer_id,))
            row = cursor.fetchone()

            conn.close()

            return dict(row) if row else None

        except Exception as e:
            logger.error(f"Error getting user by Stripe customer {customer_id}: {e}", exc_info=True)
            return None

    def set_stripe_customer_id(self, user_id: int, stripe_customer_id: str) -> bool:
        """
        Link a Telegram user to their Stripe customer ID.

        Args:
            user_id: Telegram user ID
            stripe_customer_id: Stripe customer ID

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE users
                SET stripe_customer_id = ?, updated_at = ?
                WHERE user_id = ?
            """, (stripe_customer_id, datetime.now().isoformat(), user_id))

            conn.commit()
            conn.close()

            return True

        except Exception as e:
            logger.error(f"Error linking Stripe customer for user {user_id}: {e}", exc_info=True)
            return False

    def update_vip_status(
        self,
        user_id: int,
        is_vip: bool,
        subscription_type: str = None,
        expires_at: str = None
    ) -> bool:
        """
        Update user's VIP status.
        
        Args:
            user_id: Telegram user ID
            is_vip: Whether user is VIP
            subscription_type: "monthly" or "yearly"
            expires_at: Expiration date ISO string
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users
                SET is_vip = ?, subscription_type = ?, vip_expires_at = ?, updated_at = ?
                WHERE user_id = ?
            """, (is_vip, subscription_type, expires_at, datetime.now().isoformat(), user_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"VIP status updated for user {user_id}: is_vip={is_vip}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating VIP status for user {user_id}: {e}", exc_info=True)
            return False
    
    # ==================== ANALYSIS MANAGEMENT ====================
    
    def save_analysis(self, analysis_data: Dict[str, Any]) -> Optional[int]:
        """
        Save analysis to database.
        
        Args:
            analysis_data: Analysis data dictionary
            
        Returns:
            Analysis ID or None
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO analyses (
                    user_id, match_id, home_team, away_team, analysis_type,
                    analysis_text, match_data, prompt_used, from_cache,
                    tokens_used, cost_eur
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis_data.get("user_id"),
                analysis_data.get("match_id"),
                analysis_data.get("home_team"),
                analysis_data.get("away_team"),
                analysis_data.get("analysis_type"),
                analysis_data.get("analysis"),
                json.dumps(analysis_data.get("match_data", {})),
                analysis_data.get("prompt_used", "")[:1000],  # Limit prompt length
                analysis_data.get("from_cache", False),
                analysis_data.get("tokens_used", 0),
                analysis_data.get("cost_eur", 0.0)
            ))
            
            analysis_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Analysis saved with ID {analysis_id}")
            return analysis_id
            
        except Exception as e:
            logger.error(f"Error saving analysis: {e}", exc_info=True)
            return None
    
    def get_user_analyses(
        self,
        user_id: int,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get user's analysis history.
        
        Args:
            user_id: Telegram user ID
            limit: Maximum number of analyses to retrieve
            offset: Offset for pagination
            
        Returns:
            List of analysis dictionaries
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM analyses
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (user_id, limit, offset))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting analyses for user {user_id}: {e}", exc_info=True)
            return []
    
    # ==================== PAYMENT MANAGEMENT ====================
    
    def save_payment(self, payment_data: Dict[str, Any]) -> Optional[int]:
        """
        Save payment record.
        
        Args:
            payment_data: Payment data dictionary
            
        Returns:
            Payment ID or None
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO payments (
                    user_id, stripe_payment_id, stripe_customer_id,
                    amount_eur, currency, status, subscription_type, payment_method
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                payment_data.get("user_id"),
                payment_data.get("stripe_payment_id"),
                payment_data.get("stripe_customer_id"),
                payment_data.get("amount_eur"),
                payment_data.get("currency", "EUR"),
                payment_data.get("status"),
                payment_data.get("subscription_type"),
                payment_data.get("payment_method", "card")
            ))
            
            payment_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            logger.info(f"Payment saved with ID {payment_id}")
            return payment_id
            
        except Exception as e:
            logger.error(f"Error saving payment: {e}", exc_info=True)
            return None
    
    def save_subscription(self, subscription_data: Dict[str, Any]) -> Optional[int]:
        """
        Save subscription record.
        
        Args:
            subscription_data: Subscription data dictionary
            
        Returns:
            Subscription ID or None
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO subscriptions (
                    user_id, stripe_subscription_id, status, price_type,
                    current_period_start, current_period_end, cancel_at_period_end
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(stripe_subscription_id) DO UPDATE SET
                    status = excluded.status,
                    current_period_end = excluded.current_period_end,
                    cancel_at_period_end = excluded.cancel_at_period_end,
                    updated_at = excluded.updated_at
            """, (
                subscription_data.get("user_id"),
                subscription_data.get("stripe_subscription_id"),
                subscription_data.get("status"),
                subscription_data.get("price_type"),
                subscription_data.get("current_period_start"),
                subscription_data.get("current_period_end"),
                subscription_data.get("cancel_at_period_end", False)
            ))
            
            subscription_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            logger.info(f"Subscription saved with ID {subscription_id}")
            return subscription_id
            
        except Exception as e:
            logger.error(f"Error saving subscription: {e}", exc_info=True)
            return None
    
    # ==================== STATISTICS ====================
    
    def update_daily_stats(self, date: str = None) -> bool:
        """
        Update daily statistics.
        
        Args:
            date: Date string (YYYY-MM-DD), defaults to today
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not date:
                date = datetime.now().date().isoformat()
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Calculate stats
            cursor.execute("""
                INSERT INTO daily_stats (date, total_users, active_users, new_users, vip_subscriptions, analyses_generated)
                SELECT
                    ? as date,
                    COUNT(DISTINCT u.user_id) as total_users,
                    COUNT(DISTINCT a.user_id) as active_users,
                    COUNT(DISTINCT CASE WHEN DATE(u.created_at) = ? THEN u.user_id END) as new_users,
                    COUNT(DISTINCT CASE WHEN u.is_vip = 1 THEN u.user_id END) as vip_subscriptions,
                    COUNT(a.id) as analyses_generated
                FROM users u
                LEFT JOIN analyses a ON DATE(a.created_at) = ?
                WHERE DATE(u.created_at) <= ?
            """, (date, date, date, date))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Daily stats updated for {date}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating daily stats: {e}", exc_info=True)
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get overall statistics.
        
        Returns:
            Statistics dictionary
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Total users
            cursor.execute("SELECT COUNT(*) as count FROM users")
            total_users = cursor.fetchone()["count"]
            
            # VIP users
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE is_vip = 1")
            vip_users = cursor.fetchone()["count"]
            
            # Total analyses
            cursor.execute("SELECT COUNT(*) as count FROM analyses")
            total_analyses = cursor.fetchone()["count"]
            
            # Today's analyses
            today = datetime.now().date().isoformat()
            cursor.execute("SELECT COUNT(*) as count FROM analyses WHERE DATE(created_at) = ?", (today,))
            today_analyses = cursor.fetchone()["count"]
            
            # Revenue
            cursor.execute("SELECT SUM(amount_eur) as total FROM payments WHERE status = 'succeeded'")
            total_revenue = cursor.fetchone()["total"] or 0.0
            
            conn.close()
            
            return {
                "total_users": total_users,
                "vip_users": vip_users,
                "free_users": total_users - vip_users,
                "total_analyses": total_analyses,
                "today_analyses": today_analyses,
                "total_revenue": total_revenue
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}", exc_info=True)
            return {}
    
    def health_check(self) -> bool:
        """
        Check if database is accessible.
        
        Returns:
            True if database is working, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            conn.close()
            
            return result is not None
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False