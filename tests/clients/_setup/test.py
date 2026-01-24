# Auto-generated from script.md
# Last updated: 2024-01-20
# Source: tests/clients/_setup/script.md
# DO NOT EDIT MANUALLY - This file is regenerated from script.md

import os
from playwright.sync_api import Page

# Import the login function
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from tests._functions.login.test import fn_login


def setup_clients(page: Page, context: dict) -> None:
    """
    Setup for Clients category.
    
    Logs in the user before running client-related tests.
    
    Credentials are read from environment variables or use defaults.
    
    Saves to context:
    - logged_in_user: The email that was logged in (from login function)
    """
    # Get credentials from environment or use defaults
    username = os.environ.get("VCITA_TEST_USERNAME", "itzik+autotest@vcita.com")
    password = os.environ.get("VCITA_TEST_PASSWORD", "vcita123")
    
    # Call the login function
    fn_login(page, context, username=username, password=password)
    
    print(f"  Clients setup complete - logged in as {context.get('logged_in_user')}")
