# Auto-generated from script.md
# Last updated: 2024-01-20
# Source: tests/clients/_setup/script.md
# DO NOT EDIT MANUALLY - This file is regenerated from script.md

import os
import sys

from playwright.sync_api import Page

# Import the login function
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from tests._functions.login.test import fn_login


def setup_clients(page: Page, context: dict) -> None:
    """
    Setup for Clients category.
    
    Logs in the user before running client-related tests.
    
    Credentials: from context (injected by runner from config.yaml target.auth). No fallbacks.
    
    Saves to context:
    - logged_in_user: The email that was logged in (from login function)
    """
    username = context.get("username")
    password = context.get("password")
    if not username or not password:
        raise ValueError(
            "username and password not in context. Set target.auth.username and target.auth.password in config.yaml."
        )
    
    # Call the login function
    fn_login(page, context, username=username, password=password)
    
    print(f"  Clients setup complete - logged in as {context.get('logged_in_user')}")
