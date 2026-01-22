"""
Test executor for the test runner.

Handles the actual execution of individual test.py files,
including dynamic import, function discovery, and error handling.
"""

import importlib.util
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Any, Optional, Tuple, Literal

from playwright.sync_api import Page

from .models import TestResult


class TestExecutor:
    """
    Executes individual test files.
    
    Dynamically imports test.py files and runs the test function,
    capturing results, errors, and screenshots.
    """
    
    def __init__(self, snapshots_dir: Optional[Path] = None):
        """
        Initialize the executor.
        
        Args:
            snapshots_dir: Directory to save screenshots on failure.
                          Defaults to .temp_screenshots/ (moved to run storage after)
        """
        self.snapshots_dir = snapshots_dir or Path(".temp_screenshots")
    
    def execute(
        self,
        test_path: Path,
        test_type: Literal["test", "setup", "teardown"],
        page: Page,
        context: Dict[str, Any],
    ) -> TestResult:
        """
        Execute a test file.
        
        Args:
            test_path: Path to the test folder (containing test.py)
            test_type: Type of test (test, setup, teardown)
            page: Playwright page object
            context: Shared context dictionary
            
        Returns:
            TestResult with pass/fail status and details
        """
        test_file = test_path / "test.py"
        test_name = test_path.name
        
        if not test_file.exists():
            return TestResult(
                test_name=test_name,
                test_path=test_path,
                test_type=test_type,
                status="skipped",
                duration_ms=0,
                error=f"Test file not found: {test_file}",
                error_type="FileNotFoundError",
            )
        
        # Find the test function
        func, error = self._load_test_function(test_file, test_type)
        if error:
            return TestResult(
                test_name=test_name,
                test_path=test_path,
                test_type=test_type,
                status="failed",
                duration_ms=0,
                error=error,
                error_type="ImportError",
            )
        
        # Execute the test
        start_time = time.time()
        screenshot_path = None
        
        try:
            func(page, context)
            
            duration_ms = int((time.time() - start_time) * 1000)
            return TestResult(
                test_name=test_name,
                test_path=test_path,
                test_type=test_type,
                status="passed",
                duration_ms=duration_ms,
            )
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Capture screenshot on failure
            screenshot_path = self._capture_screenshot(page, test_name)
            
            # Get full traceback
            error_msg = f"{type(e).__name__}: {str(e)}"
            full_traceback = traceback.format_exc()
            
            return TestResult(
                test_name=test_name,
                test_path=test_path,
                test_type=test_type,
                status="failed",
                duration_ms=duration_ms,
                error=error_msg,
                error_type=type(e).__name__,
                screenshot=screenshot_path,
                context_snapshot=context.copy() if context else None,
            )
    
    def _load_test_function(
        self,
        test_file: Path,
        test_type: Literal["test", "setup", "teardown"],
    ) -> Tuple[Optional[Callable], Optional[str]]:
        """
        Load the test function from a test.py file.
        
        Looks for functions matching these patterns:
        - test_*: For regular tests (e.g., test_create_matter)
        - setup_*: For setup functions (e.g., setup_clients_category)
        - teardown_*: For teardown functions
        - fn_*: For function tests (e.g., fn_login)
        
        Args:
            test_file: Path to test.py
            test_type: Type of test to look for
            
        Returns:
            Tuple of (function, error_message)
        """
        try:
            # Generate unique module name to avoid caching issues
            import time as time_module
            module_name = f"test_module_{test_file.parent.name}_{int(time_module.time() * 1000)}"
            
            # Load the module
            spec = importlib.util.spec_from_file_location(
                module_name,
                test_file
            )
            if spec is None or spec.loader is None:
                return None, f"Could not load module spec for {test_file}"
            
            module = importlib.util.module_from_spec(spec)
            
            # Add parent directories to path for imports
            parent_paths = [
                str(test_file.parent),
                str(test_file.parent.parent),
                str(test_file.parent.parent.parent),
            ]
            for p in parent_paths:
                if p not in sys.path:
                    sys.path.insert(0, p)
            
            # Add module to sys.modules before executing (for imports within the module)
            sys.modules[module_name] = module
            
            spec.loader.exec_module(module)
            
            # Find the appropriate function
            # Priority: exact match first, then fallback to fn_ for functions
            prefixes = {
                "test": ["test_"],
                "setup": ["setup_"],
                "teardown": ["teardown_"],
            }
            
            search_prefixes = prefixes.get(test_type, ["test_"])
            
            # First pass: look for exact prefix match
            for name in dir(module):
                for prefix in search_prefixes:
                    if name.startswith(prefix):
                        func = getattr(module, name)
                        if callable(func):
                            return func, None
            
            # Second pass: for functions folder, look for fn_ prefix
            # This is only used when running functions directly, not for setup/teardown
            if test_type == "test":
                for name in dir(module):
                    if name.startswith("fn_"):
                        func = getattr(module, name)
                        if callable(func):
                            return func, None
            
            # No function found
            available = [n for n in dir(module) if not n.startswith("_")]
            return None, f"No {test_type} function found in {test_file}. Available: {available[:10]}"
            
        except Exception as e:
            return None, f"Error loading {test_file}: {type(e).__name__}: {str(e)}"
    
    def _capture_screenshot(self, page: Page, test_name: str) -> Optional[Path]:
        """
        Capture a screenshot on test failure.
        
        Args:
            page: Playwright page
            test_name: Name of the test (for filename)
            
        Returns:
            Path to screenshot file, or None if capture failed
        """
        try:
            # Use absolute path to ensure correct location
            abs_snapshots_dir = Path.cwd() / self.snapshots_dir
            abs_snapshots_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = abs_snapshots_dir / f"{test_name}_{timestamp}.png"
            print(f"  [Screenshot] Capturing to: {screenshot_path}")
            page.screenshot(path=str(screenshot_path))
            # Verify the file was actually saved
            if screenshot_path.exists():
                print(f"  [Screenshot] Saved successfully ({screenshot_path.stat().st_size} bytes)")
                # Return relative path for heal request
                return self.snapshots_dir / f"{test_name}_{timestamp}.png"
            else:
                print(f"  [Screenshot] WARNING: File not found after save!")
                return None
        except Exception as e:
            print(f"  [Screenshot] FAILED to capture: {type(e).__name__}: {e}")
            return None
    
    def validate_test_file(self, test_path: Path) -> Tuple[bool, Optional[str]]:
        """
        Validate that a test file exists and has a runnable function.
        
        Args:
            test_path: Path to test folder
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        test_file = test_path / "test.py"
        
        if not test_file.exists():
            return False, f"test.py not found in {test_path}"
        
        # Check if file has content (not just placeholder)
        content = test_file.read_text()
        if content.strip() == "pass" or "Pending generation" in content:
            return False, f"test.py is a placeholder in {test_path}"
        
        return True, None
