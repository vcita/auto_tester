"""
Main test runner orchestrator.

Coordinates test execution across categories, managing browser lifecycle,
context, and emitting events for real-time updates.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from playwright.sync_api import sync_playwright, Browser, Page

from src.discovery import TestDiscovery
from src.models import Category, Test

from .models import TestResult, CategoryResult, RunResult
from .events import EventEmitter, RunnerEvent
from .context import ContextManager
from .executor import TestExecutor
from .heal import HealRequestGenerator
from .storage import RunStorage


class TestRunner:
    """
    Main test runner that orchestrates test execution.
    
    Features:
    - Runs tests sequentially within categories
    - Manages browser lifecycle (new browser per category)
    - Passes shared context between tests
    - Emits events for real-time updates (GUI-ready)
    - Generates heal requests on failure
    
    Usage:
        runner = TestRunner(tests_root)
        
        # Subscribe to events (optional)
        runner.events.on(RunnerEvent.TEST_COMPLETED, my_callback)
        
        # Run all categories
        result = runner.run_all()
        
        # Or run specific category
        result = runner.run_category("clients")
    """
    
    def __init__(
        self,
        tests_root: Path,
        headless: bool = False,
        snapshots_dir: Optional[Path] = None,
        record_video: bool = True,
        keep_open: bool = False,
        until_test: Optional[str] = None,
    ):
        """
        Initialize the test runner.
        
        Args:
            tests_root: Path to the tests/ directory
            headless: Whether to run browser in headless mode
            snapshots_dir: Directory for screenshots (default: snapshots/)
            record_video: Whether to record video of test execution (default: True)
            keep_open: Whether to keep browser open on failure for debugging (default: False)
            until_test: Stop before executing this test and keep browser open (for MCP debugging)
        """
        self.tests_root = Path(tests_root)
        self.headless = headless
        self.snapshots_dir = snapshots_dir or Path("snapshots")
        self.record_video = record_video
        self.keep_open = keep_open
        self.until_test = until_test
        
        # Components
        self.events = EventEmitter()
        self.discovery = TestDiscovery(tests_root)
        self.executor = TestExecutor(Path(".temp_screenshots"))  # Temp location, moved to run storage
        self.context_manager = ContextManager()
        self.heal_generator = HealRequestGenerator()
        self.storage = RunStorage(self.tests_root)
    
    def get_categories(self) -> List[Category]:
        """
        Get all available categories.
        
        Returns:
            List of Category objects
        """
        return self.discovery.scan()
    
    def get_category(self, category_name: str) -> Optional[Category]:
        """
        Get a specific category by name.
        
        Args:
            category_name: Name of the category
            
        Returns:
            Category object or None if not found
        """
        return self.discovery.find_category(category_name)
    
    def run_all(self) -> RunResult:
        """
        Run all categories.
        
        Returns:
            RunResult with results from all categories
        """
        categories = self.get_categories()
        
        result = RunResult(started_at=datetime.now())
        
        # Start a new run in storage
        run_id = self.storage.start_run()
        
        # Count total tests
        total_tests = sum(len(c.tests) for c in categories)
        
        # Emit run started
        self.events.emit(RunnerEvent.RUN_STARTED, {
            "categories": [c.name for c in categories],
            "total_categories": len(categories),
            "total_tests": total_tests,
            "run_id": run_id,
        })
        
        # Run each category
        for index, category in enumerate(categories):
            category_result = self._run_category_internal(
                category,
                index + 1,
                len(categories),
            )
            result.category_results.append(category_result)
        
        result.completed_at = datetime.now()
        
        # Finalize run in storage
        self.storage.finalize_run(result)
        
        # Emit run completed
        self.events.emit(RunnerEvent.RUN_COMPLETED, {
            "result": result.to_dict(),
            "run_id": run_id,
        })
        
        return result
    
    def run_category(self, category_name: str, until_test: Optional[str] = None) -> CategoryResult:
        """
        Run a specific category.
        
        Args:
            category_name: Name of the category to run
            until_test: Stop before executing this test and keep browser open (for MCP debugging)
                       If None, uses self.until_test from initialization
            
        Returns:
            CategoryResult with results from the category
        """
        category = self.get_category(category_name)
        
        if not category:
            return CategoryResult(
                category_name=category_name,
                category_path=Path(category_name),
                stopped_early=True,
            )
        
        # Use until_test parameter if provided, otherwise use instance variable
        until_test_name = until_test or self.until_test
        
        # Start a new run in storage
        run_id = self.storage.start_run()
        
        # Emit run started (single category)
        self.events.emit(RunnerEvent.RUN_STARTED, {
            "categories": [category.name],
            "total_categories": 1,
            "total_tests": len(category.tests),
            "run_id": run_id,
        })
        
        result = self._run_category_internal(category, 1, 1, until_test=until_test_name)
        
        # Finalize run in storage
        run_result = RunResult(
            started_at=datetime.now(),
            completed_at=datetime.now(),
            category_results=[result],
        )
        self.storage.finalize_run(run_result)
        
        # Emit run completed
        self.events.emit(RunnerEvent.RUN_COMPLETED, {
            "result": run_result.to_dict(),
            "run_id": run_id,
        })
        
        return result
    
    def _run_category_internal(
        self,
        category: Category,
        category_index: int,
        total_categories: int,
        until_test: Optional[str] = None,
    ) -> CategoryResult:
        """
        Internal method to run a single category.
        
        Args:
            category: Category to run
            category_index: Index of this category (1-based)
            total_categories: Total number of categories
            
        Returns:
            CategoryResult
        """
        result = CategoryResult(
            category_name=category.name,
            category_path=category.path,
        )
        
        # Emit category started
        self.events.emit(RunnerEvent.CATEGORY_STARTED, {
            "category": category.name,
            "tests": [t.name for t in category.tests],
            "index": category_index,
            "total": total_categories,
            "has_setup": category.setup is not None,
            "has_teardown": category.teardown is not None,
        })
        
        # Create fresh context for this category
        context = self.context_manager.create_fresh()
        
        # Start browser for this category
        self.events.emit(RunnerEvent.BROWSER_STARTING, {"category": category.name})
        
        with sync_playwright() as playwright:
            # Use channel='chrome' to use the real installed Chrome browser
            # This bypasses most Cloudflare detection since it's a real browser
            browser = playwright.chromium.launch(
                headless=self.headless,
                channel='chrome',  # Use real Chrome instead of Chromium
                args=[
                    '--disable-blink-features=AutomationControlled',
                ]
            )
            
            # Create context with realistic settings
            # Video recording is enabled by default for debugging
            # Videos are recorded to a temp location and moved to run storage after completion
            video_dir = None
            if self.record_video:
                video_dir = Path.cwd() / ".temp_videos"
                video_dir.mkdir(parents=True, exist_ok=True)
            
            # Custom user agent with bypass string to avoid captcha
            # The bypass string is specific to vcita's captcha allowlist
            bypass_string = "#vUC5wTG98Hq5=BW+D_1c29744b-38df-4f40-8830-a7558ccbfa6b"
            custom_user_agent = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 {bypass_string}"
            
            browser_context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York',
                user_agent=custom_user_agent,
                record_video_dir=str(video_dir) if video_dir else None,
                record_video_size={'width': 1920, 'height': 1080},
            )
            
            # Minimal stealth - just hide webdriver flag
            browser_context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            page = browser_context.new_page()
            
            # Track video start time for timestamp logging
            import time as time_module
            video_start_time = time_module.time()
            video_timestamps = []  # List of (test_name, start_offset, end_offset, status)
            
            self.events.emit(RunnerEvent.BROWSER_STARTED, {"category": category.name})
            
            try:
                # Run setup if exists
                if category.setup and category.setup.is_valid:
                    test_start_offset = time_module.time() - video_start_time
                    setup_result = self._run_single_test(
                        test_path=self.tests_root / category.path / "_setup",
                        test_name="_setup",
                        test_type="setup",
                        page=page,
                        context=context,
                        index=0,
                        total=len(category.tests),
                        category_name=category.name,
                    )
                    test_end_offset = time_module.time() - video_start_time
                    video_timestamps.append(("_setup", test_start_offset, test_end_offset, setup_result.status))
                    result.setup_result = setup_result
                    
                    # If setup fails, skip all tests
                    if setup_result.status == "failed":
                        result.stopped_early = True
                        # Skip all tests
                        for test in category.tests:
                            result.test_results.append(TestResult(
                                test_name=test.name,
                                test_path=test.path,
                                test_type="test",
                                status="skipped",
                                duration_ms=0,
                                error="Skipped due to setup failure",
                            ))
                        # Still run teardown
                        self._run_teardown_if_exists(
                            category, page, context, result
                        )
                        return result
                
                # Build execution plan: interleave tests and subcategories based on run_after
                execution_plan = self._build_execution_plan(category)
                total_items = len(execution_plan)
                
                # Run tests and subcategories in order
                for index, item in enumerate(execution_plan):
                    if isinstance(item, Test):
                        # Run a test
                        test = item
                        
                        # Check if we should stop before this test (for MCP debugging)
                        if until_test:
                            # Match test name (can be "Services/Edit Group Event" or "Edit Group Event")
                            test_full_name = f"{category.name}/{test.name}" if hasattr(category, 'name') else test.name
                            # Also check subcategory format like "Services/Edit Group Event"
                            subcategory_prefix = ""
                            if hasattr(category, 'subcategories') and category.subcategories:
                                # Try to find if test is in a subcategory
                                for subcat in category.subcategories:
                                    if test in subcat.tests:
                                        subcategory_prefix = f"{subcat.name}/"
                                        break
                            test_with_subcat = f"{subcategory_prefix}{test.name}"
                            
                            if (test.name == until_test or 
                                test_full_name == until_test or 
                                test_with_subcat == until_test or
                                until_test in test.name or
                                until_test in test_full_name):
                                result.stopped_early = True
                                result.until_test_reached = True
                                print(f"\n  [>] Stopped before test: {test.name}")
                                print(f"  [>] Browser kept open for MCP debugging")
                                print(f"  [>] Current URL: {page.url}")
                                print(f"  [>] Current Title: {page.title()}")
                                print(f"  [>] Use Playwright MCP to run the test step-by-step")
                                
                                # Note: Video recording continues until browser context closes
                                # The video will include the MCP debugging wait time until you press Enter
                                if self.record_video:
                                    print(f"  [>] Note: Video recording will stop when you close the browser")
                                
                                # Skip remaining items
                                self._skip_remaining_items(execution_plan[index:], result, test.name)
                                # Keep browser open - don't run teardown yet
                                input("  [>] Press Enter when done with MCP debugging to close browser...")
                                break
                        
                        test_start_offset = time_module.time() - video_start_time
                        test_result = self._run_single_test(
                            test_path=test.path,
                            test_name=test.name,
                            test_type="test",
                            page=page,
                            context=context,
                            index=index + 1,
                            total=total_items,
                            category_name=category.name,
                        )
                        test_end_offset = time_module.time() - video_start_time
                        video_timestamps.append((test.name, test_start_offset, test_end_offset, test_result.status))
                        result.test_results.append(test_result)
                        
                        # If test fails, stop category and skip remaining items
                        if test_result.status == "failed":
                            result.stopped_early = True
                            self._skip_remaining_items(execution_plan[index + 1:], result, test.name)
                            break
                    
                    elif isinstance(item, Category):
                        # Run a subcategory inline
                        subcategory = item
                        subcat_start_offset = time_module.time() - video_start_time
                        
                        subcat_failed, failed_test_name = self._run_subcategory_inline(
                            subcategory=subcategory,
                            page=page,
                            context=context,
                            result=result,
                            video_timestamps=video_timestamps,
                            video_start_time=video_start_time,
                            time_module=time_module,
                            until_test=until_test,
                        )
                        
                        # If subcategory failed, stop and skip remaining items
                        if subcat_failed:
                            result.stopped_early = True
                            self._skip_remaining_items(execution_plan[index + 1:], result, failed_test_name)
                            break
                
                # Run teardown if exists (always, even on failure, unless until_test was reached)
                if not getattr(result, 'until_test_reached', False):
                    self._run_teardown_if_exists(category, page, context, result)
                
            finally:
                # Get video path before closing (if recording enabled)
                video_path = None
                if self.record_video and page.video:
                    video_path = page.video.path()
                
                # If keep_open is enabled and there was a failure, wait for user
                # Or if until_test was reached, browser is already open (handled above)
                if self.keep_open and result.stopped_early and not getattr(result, 'until_test_reached', False):
                    print("\n  [!] Browser kept open for debugging (--keep-open flag)")
                    print(f"  [>] Current URL: {page.url}")
                    print(f"  [>] Current Title: {page.title()}")
                    input("  [>] Press Enter to close browser and continue...")
                
                # Close browser
                # Note: Video recording stops when browser_context.close() is called
                # If until_test was reached, the video will include the MCP debugging wait time
                self.events.emit(RunnerEvent.BROWSER_CLOSING, {"category": category.name})
                browser_context.close()  # Close context first to finalize video
                browser.close()
                
                # Process video and save to storage
                final_video_path = None
                if video_path and Path(video_path).exists():
                    # Temporarily rename video with category name for identification
                    temp_video_path = Path(video_path).parent / f"{category.name}_{self.storage.current_run_id}.webm"
                    Path(video_path).rename(temp_video_path)
                    final_video_path = temp_video_path
                    
                    # Print video timestamps for easy navigation
                    if video_timestamps:
                        print(f"  [Video] Timeline:")
                        for test_name, start, end, status in video_timestamps:
                            start_str = f"{int(start//60):02d}:{int(start%60):02d}"
                            end_str = f"{int(end//60):02d}:{int(end%60):02d}"
                            status_icon = ">" if status == "passed" else "X" if status == "failed" else "-"
                            print(f"    [{status_icon}] {start_str} - {end_str} : {test_name}")
        
        # Save category result to storage (will move video to _runs folder)
        self.storage.save_category_result(
            category=category.name,
            result=result,
            video_path=final_video_path,
        )
        
        # Save context for debugging
        self.context_manager.save_to_file(f"{category.name}_context.json")
        
        # Emit category completed
        self.events.emit(RunnerEvent.CATEGORY_COMPLETED, {
            "category": category.name,
            "result": result.to_dict(),
        })
        
        return result
    
    def _run_teardown_if_exists(
        self,
        category: Category,
        page: Page,
        context: dict,
        result: CategoryResult,
    ) -> None:
        """Run teardown if it exists."""
        if category.teardown and category.teardown.is_valid:
            teardown_result = self._run_single_test(
                test_path=self.tests_root / category.path / "_teardown",
                test_name="_teardown",
                test_type="teardown",
                page=page,
                context=context,
                index=0,
                total=0,
                category_name=category.name,
            )
            result.teardown_result = teardown_result
    
    def _run_single_test(
        self,
        test_path: Path,
        test_name: str,
        test_type: str,
        page: Page,
        context: dict,
        index: int,
        total: int,
        category_name: str,
    ) -> TestResult:
        """
        Run a single test and handle events/healing.
        
        Args:
            test_path: Path to the test folder
            test_name: Name of the test
            test_type: Type (test, setup, teardown)
            page: Playwright page
            context: Shared context
            index: Test index (1-based)
            total: Total tests in category
            category_name: Name of the category
            
        Returns:
            TestResult
        """
        # Emit test started
        self.events.emit(RunnerEvent.TEST_STARTED, {
            "test": test_name,
            "test_type": test_type,
            "index": index,
            "total": total,
            "category": category_name,
        })
        
        # Execute the test
        result = self.executor.execute(
            test_path=test_path,
            test_type=test_type,
            page=page,
            context=context,
        )
        
        # Emit test completed
        self.events.emit(RunnerEvent.TEST_COMPLETED, {
            "test": test_name,
            "test_type": test_type,
            "result": result.to_dict(),
        })
        
        # Save test result to storage
        # Extract simple test name (handle subcategory paths like "services/create_service")
        simple_test_name = test_name.split("/")[-1] if "/" in test_name else test_name
        self.storage.save_test_result(
            category=category_name,
            test_name=simple_test_name,
            result=result,
            screenshot_path=result.screenshot,
        )
        
        # If failed, generate heal request and emit event
        if result.status == "failed":
            self.events.emit(RunnerEvent.TEST_FAILED, {
                "test": test_name,
                "error": result.error,
                "error_type": result.error_type,
            })
            
            # Generate heal request
            heal_path = self.heal_generator.generate(
                result=result,
                category_name=category_name,
                context=context,
            )
            
            # Copy heal request to storage
            if heal_path:
                self.storage.save_heal_request(
                    category=category_name,
                    test_name=simple_test_name,
                    heal_request_path=heal_path,
                )
            
            self.events.emit(RunnerEvent.HEAL_REQUEST_CREATED, {
                "test": test_name,
                "path": str(heal_path),
            })
        
        return result
    
    def _build_execution_plan(self, category: Category) -> List:
        """
        Build an execution plan that interleaves tests and subcategories.
        
        Subcategories with run_after specified will be inserted after the named test.
        Subcategories without run_after will be added at the end.
        
        Args:
            category: The category to build plan for
            
        Returns:
            List of Test and Category objects in execution order
        """
        from typing import Union
        
        plan: List[Union[Test, Category]] = []
        
        # Create a map of test_id -> list of subcategories to run after it
        subcats_after: dict[str, List[Category]] = {}
        subcats_at_end: List[Category] = []
        
        for subcat in category.subcategories:
            if subcat.run_after:
                if subcat.run_after not in subcats_after:
                    subcats_after[subcat.run_after] = []
                subcats_after[subcat.run_after].append(subcat)
            else:
                subcats_at_end.append(subcat)
        
        # Build plan: tests with subcategories inserted at appropriate points
        for test in category.tests:
            plan.append(test)
            
            # Insert any subcategories that should run after this test
            if test.id in subcats_after:
                for subcat in subcats_after[test.id]:
                    plan.append(subcat)
        
        # Add subcategories without run_after at the end
        plan.extend(subcats_at_end)
        
        return plan
    
    def _skip_remaining_items(
        self,
        remaining_items: List,
        result: CategoryResult,
        failed_test_name: str,
    ) -> None:
        """
        Skip all remaining items (tests and subcategories) after a failure.
        
        Args:
            remaining_items: List of remaining Test and Category objects
            result: CategoryResult to update
            failed_test_name: Name of the test that failed
        """
        for item in remaining_items:
            if isinstance(item, Test):
                result.test_results.append(TestResult(
                    test_name=item.name,
                    test_path=item.path,
                    test_type="test",
                    status="skipped",
                    duration_ms=0,
                    error=f"Skipped due to {failed_test_name} failure",
                ))
            elif isinstance(item, Category):
                # Skip all tests in the subcategory
                for test in item.tests:
                    result.test_results.append(TestResult(
                        test_name=f"{item.name}/{test.name}",
                        test_path=test.path,
                        test_type="test",
                        status="skipped",
                        duration_ms=0,
                        error=f"Skipped due to {failed_test_name} failure",
                    ))
    
    def _run_subcategory_inline(
        self,
        subcategory: Category,
        page,
        context: dict,
        result: CategoryResult,
        video_timestamps: list,
        video_start_time: float,
        time_module,
        until_test: Optional[str] = None,
    ) -> tuple[bool, str]:
        """
        Run a subcategory inline within the parent category's browser session.
        
        Args:
            subcategory: The subcategory to run
            page: Playwright page (shared with parent)
            context: Shared context dict
            result: Parent's CategoryResult to append to
            video_timestamps: List to append timestamps to
            video_start_time: When video recording started
            time_module: time module reference
            
        Returns:
            Tuple of (failed: bool, failed_test_name: str or None)
        """
        print(f"\n    >>> Subcategory: {subcategory.name}")
        
        # Run subcategory setup if exists
        if subcategory.setup and subcategory.setup.is_valid:
            test_start_offset = time_module.time() - video_start_time
            setup_result = self._run_single_test(
                test_path=self.tests_root / subcategory.path / "_setup",
                test_name=f"{subcategory.name}/_setup",
                test_type="setup",
                page=page,
                context=context,
                index=0,
                total=len(subcategory.tests),
                category_name=subcategory.name,
            )
            test_end_offset = time_module.time() - video_start_time
            video_timestamps.append((f"{subcategory.name}/_setup", test_start_offset, test_end_offset, setup_result.status))
            
            # Store as a test result in parent
            result.test_results.append(setup_result)
            
            if setup_result.status == "failed":
                # Skip all tests in subcategory
                for test in subcategory.tests:
                    result.test_results.append(TestResult(
                        test_name=f"{subcategory.name}/{test.name}",
                        test_path=test.path,
                        test_type="test",
                        status="skipped",
                        duration_ms=0,
                        error=f"Skipped due to {subcategory.name}/_setup failure",
                    ))
                return True, f"{subcategory.name}/_setup"
        
        # Run subcategory tests
        for index, test in enumerate(subcategory.tests):
            # Check if we should stop before this test (for MCP debugging)
            if until_test:
                test_full_name = f"{subcategory.name}/{test.name}"
                if (test.name == until_test or 
                    test_full_name == until_test or 
                    until_test in test.name or
                    until_test in test_full_name):
                    result.stopped_early = True
                    result.until_test_reached = True
                    print(f"\n  [>] Stopped before test: {test_full_name}")
                    print(f"  [>] Browser kept open for MCP debugging")
                    print(f"  [>] Current URL: {page.url}")
                    print(f"  [>] Current Title: {page.title()}")
                    print(f"  [>] Use Playwright MCP to run the test step-by-step")
                    
                    # Note: Video recording continues until browser context closes
                    # The video will include the MCP debugging wait time until you press Enter
                    if getattr(self, 'record_video', False):
                        print(f"  [>] Note: Video recording will stop when you close the browser")
                    
                    # Skip remaining items
                    for remaining_test in subcategory.tests[index:]:
                        result.test_results.append(TestResult(
                            test_name=f"{subcategory.name}/{remaining_test.name}",
                            test_path=remaining_test.path,
                            test_type="test",
                            status="skipped",
                            duration_ms=0,
                            error=f"Skipped - stopped before test for MCP debugging",
                        ))
                    # Keep browser open - don't run teardown yet
                    input("  [>] Press Enter when done with MCP debugging to close browser...")
                    return True, test_full_name
            
            test_start_offset = time_module.time() - video_start_time
            test_result = self._run_single_test(
                test_path=test.path,
                test_name=f"{subcategory.name}/{test.name}",
                test_type="test",
                page=page,
                context=context,
                index=index + 1,
                total=len(subcategory.tests),
                category_name=subcategory.name,
            )
            test_end_offset = time_module.time() - video_start_time
            video_timestamps.append((f"{subcategory.name}/{test.name}", test_start_offset, test_end_offset, test_result.status))
            result.test_results.append(test_result)
            
            if test_result.status == "failed":
                # Skip remaining tests in subcategory
                for remaining_test in subcategory.tests[index + 1:]:
                    result.test_results.append(TestResult(
                        test_name=f"{subcategory.name}/{remaining_test.name}",
                        test_path=remaining_test.path,
                        test_type="test",
                        status="skipped",
                        duration_ms=0,
                        error=f"Skipped due to {subcategory.name}/{test.name} failure",
                    ))
                
                # Run teardown even on failure
                self._run_subcategory_teardown(subcategory, page, context, result, video_timestamps, video_start_time, time_module)
                return True, f"{subcategory.name}/{test.name}"
        
        # Run subcategory teardown if exists
        self._run_subcategory_teardown(subcategory, page, context, result, video_timestamps, video_start_time, time_module)
        
        print(f"    <<< Subcategory: {subcategory.name} completed")
        return False, None
    
    def _run_subcategory_teardown(
        self,
        subcategory: Category,
        page,
        context: dict,
        result: CategoryResult,
        video_timestamps: list,
        video_start_time: float,
        time_module,
    ) -> None:
        """Run subcategory teardown if it exists."""
        if subcategory.teardown and subcategory.teardown.is_valid:
            test_start_offset = time_module.time() - video_start_time
            teardown_result = self._run_single_test(
                test_path=self.tests_root / subcategory.path / "_teardown",
                test_name=f"{subcategory.name}/_teardown",
                test_type="teardown",
                page=page,
                context=context,
                index=0,
                total=0,
                category_name=subcategory.name,
            )
            test_end_offset = time_module.time() - video_start_time
            video_timestamps.append((f"{subcategory.name}/_teardown", test_start_offset, test_end_offset, teardown_result.status))
            result.test_results.append(teardown_result)
