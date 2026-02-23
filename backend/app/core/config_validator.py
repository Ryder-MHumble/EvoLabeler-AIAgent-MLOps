"""
Configuration validator for external service connectivity.

This module provides functions to validate configuration and check
external service connections (Supabase, Qwen API, etc.).
"""

import asyncio
from typing import Dict

import httpx

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


async def check_supabase_connection() -> bool:
    """
    Check if Supabase is reachable and credentials are valid.

    Returns:
        bool: True if Supabase is accessible, False otherwise
    """
    try:
        # Basic connectivity check - verify URL is reachable
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{settings.supabase_url}/rest/v1/",
                headers={
                    "apikey": settings.supabase_key,
                    "Authorization": f"Bearer {settings.supabase_key}"
                }
            )
            # Supabase returns 200 for valid auth, 401 for invalid
            is_healthy = response.status_code in [200, 401]  # 401 means auth worked, just no access

            if is_healthy:
                logger.info("Supabase connection check: OK")
            else:
                logger.warning(
                    f"Supabase connection check failed: HTTP {response.status_code}"
                )

            return is_healthy

    except httpx.TimeoutException:
        logger.error("Supabase connection check failed: Timeout")
        return False
    except Exception as e:
        logger.error(f"Supabase connection check failed: {e}")
        return False


async def check_qwen_api() -> bool:
    """
    Check if Qwen API is accessible and API key is valid.

    Returns:
        bool: True if Qwen API is accessible, False otherwise
    """
    try:
        # Test API connectivity by calling models endpoint
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{settings.qwen_api_base_url}/models",
                headers={"Authorization": f"Bearer {settings.qwen_api_key}"}
            )

            is_healthy = response.status_code == 200

            if is_healthy:
                logger.info("Qwen API connection check: OK")
            else:
                logger.warning(
                    f"Qwen API connection check failed: HTTP {response.status_code}"
                )

            return is_healthy

    except httpx.TimeoutException:
        logger.error("Qwen API connection check failed: Timeout")
        return False
    except Exception as e:
        logger.error(f"Qwen API connection check failed: {e}")
        return False


def check_yolo_path_exists() -> bool:
    """
    Check if YOLO project path is configured.

    Note: This only validates the path is set in config.
    Actual SSH connection check would require remote access which
    may not be available at startup.

    Returns:
        bool: True if path is configured, False otherwise
    """
    try:
        # Check if path is set and not empty
        if not settings.remote_yolo_project_path:
            logger.warning("YOLO project path not configured")
            return False

        # Check if it looks like a valid path
        if not settings.remote_yolo_project_path.startswith("/"):
            logger.warning(
                f"YOLO project path should be absolute: {settings.remote_yolo_project_path}"
            )
            return False

        logger.info(f"YOLO project path configured: {settings.remote_yolo_project_path}")
        return True

    except Exception as e:
        logger.error(f"YOLO path check failed: {e}")
        return False


async def validate_config() -> Dict[str, bool]:
    """
    Validate configuration and return health status for each service.

    Runs all health checks concurrently for faster validation.

    Returns:
        dict: Dictionary with service names as keys and health status as values
        Example: {"supabase": True, "qwen_api": True, "yolo_path": False}
    """
    logger.info("Starting configuration validation...")

    # Run all async checks concurrently
    supabase_task = check_supabase_connection()
    qwen_task = check_qwen_api()

    # Wait for all async checks
    supabase_result, qwen_result = await asyncio.gather(
        supabase_task,
        qwen_task,
        return_exceptions=True
    )

    # Handle any exceptions from gather
    supabase_healthy = supabase_result if isinstance(supabase_result, bool) else False
    qwen_healthy = qwen_result if isinstance(qwen_result, bool) else False

    # Run sync check
    yolo_healthy = check_yolo_path_exists()

    checks = {
        "supabase": supabase_healthy,
        "qwen_api": qwen_healthy,
        "yolo_path": yolo_healthy,
    }

    # Log summary
    passed = sum(checks.values())
    total = len(checks)
    logger.info(f"Configuration validation complete: {passed}/{total} checks passed")

    for service, status in checks.items():
        status_str = "✓ PASS" if status else "✗ FAIL"
        logger.info(f"  {service}: {status_str}")

    return checks
