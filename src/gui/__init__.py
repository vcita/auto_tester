"""
Web GUI for the vcita Test Runner.

Provides a web-based interface for:
- Browsing the test suite
- Running tests with real-time updates
- Viewing test artifacts (screenshots, videos, logs)
- Managing heal requests
"""

from .app import create_app, run_server

__all__ = ["create_app", "run_server"]
