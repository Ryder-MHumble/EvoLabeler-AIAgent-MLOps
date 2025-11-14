"""
Supabase client initialization using singleton pattern.

This module provides a global Supabase client instance that is initialized
once and reused throughout the application.
"""

from typing import Optional
from supabase import create_client, Client

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class SupabaseClientSingleton:
    """Singleton class for Supabase client."""

    _instance: Optional["SupabaseClientSingleton"] = None
    _client: Optional[Client] = None

    def __new__(cls) -> "SupabaseClientSingleton":
        """Create or return the singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_client(self) -> Client:
        """
        Get the Supabase client instance.

        Returns:
            Initialized Supabase client
        """
        if self._client is None:
            logger.info("Initializing Supabase client")
            # Use service key if available, otherwise use regular key
            supabase_key = settings.supabase_service_key or settings.supabase_key
            key_type = "service" if settings.supabase_service_key else "regular"

            logger.info(f"Using {key_type} Supabase key")
            self._client = create_client(
                supabase_url=settings.supabase_url,
                supabase_key=supabase_key,
            )
            logger.info("Supabase client initialized successfully")
        return self._client


# Global function to get the Supabase client
def get_supabase_client() -> Client:
    """
    Get the global Supabase client instance.
    
    Returns:
        Supabase client instance
    """
    return SupabaseClientSingleton().get_client()


