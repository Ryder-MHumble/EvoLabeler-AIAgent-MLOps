#!/usr/bin/env python
"""
Development server runner.

This script provides a convenient way to run the development server
with proper configuration.
"""

import sys
import uvicorn

from app.core.config import settings


def main() -> None:
    """Run the development server."""
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Debug mode: {settings.debug}")
    print(f"Log level: {settings.log_level}")
    print("-" * 50)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True,
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        sys.exit(0)

