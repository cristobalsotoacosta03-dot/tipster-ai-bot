"""
Data module for fetching and managing football statistics.
"""
from .stats_fetcher import StatsFetcher
from .cache_manager import CacheManager

__all__ = ["StatsFetcher", "CacheManager"]