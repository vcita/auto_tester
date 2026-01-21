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
    ):
        """
        Initialize the test runner.
        
        Args:
            tests_root: Path to the tests/ directory
            headless: Whether to run browser in headless mode
            snapshots_dir: Directory for screenshots (default: snapshots/)
            record_video: Whether to record video of test execution (default: True)
        """
        self.tests_root = Path(tests_root)
        self.headless = headless
        self.snapshots_dir = snapshots_dir or Path("snapshots")
        self.record_video = record_video
        
        # Components
        self.events = EventEmitter()
        self.discovery = TestDiscovery(tests_root)
        self.executor = TestExecutor(self.snapshots_dir / "screenshots")
        self.context_manager = ContextManager()
        self.heal_generator = HealRequestGenerator()
    
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
        
        # Count total tests
        total_tests = sum(len(c.tests) for c in categories)
        
        # Emit run started
        self.events.emit(RunnerEvent.RUN_STARTED, {
            "categories": [c.name for c in categories],
            "total_categories": len(categories),
            "total_tests": total_tests,
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
        
        # Emit run completed
        self.events.emit(RunnerEvent.RUN_COMPLETED, {
            "result": result.to_dict(),
        })
        
        return result
    
    def run_category(self, category_name: str) -> CategoryResult:
        """
        Run a specific category.
        
        Args:
            category_name: Name of the category to run
            
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
        
        # Emit run started (single category)
        self.events.emit(RunnerEvent.RUN_STARTED, {
            "categories": [category.name],
            "total_categories": 1,
            "total_tests": len(category.tests),
        })
        
        result = self._run_category_internal(category, 1, 1)
        
        # Emit run completed
        run_result = RunResult(
            started_at=datetime.now(),
            completed_at=datetime.now(),
            category_results=[result],
        )
        self.events.emit(RunnerEvent.RUN_COMPLETED, {
            "result": run_result.to_dict(),
        })
        
        return result
    
    def _run_category_internal(
        self,
        category: Category,
        category_index: int,
        total_categories: int,
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
            video_dir = None
            if self.record_video:
                video_dir = Path.cwd() / self.snapshots_dir / "videos"
                video_dir.mkdir(parents=True, exist_ok=True)
            
            browser_context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York',
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
                                test_path=self.tests_root / test.path,
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
                
                # Run tests in order
                for index, test in enumerate(category.tests):
                    test_start_offset = time_module.time() - video_start_time
                    test_result = self._run_single_test(
                        test_path=self.tests_root / test.path,
                        test_name=test.name,
                        test_type="test",
                        page=page,
                        context=context,
                        index=index + 1,
                        total=len(category.tests),
                        category_name=category.name,
                    )
                    test_end_offset = time_module.time() - video_start_time
                    video_timestamps.append((test.name, test_start_offset, test_end_offset, test_result.status))
                    result.test_results.append(test_result)
                    
                    # If test fails, stop category and skip remaining tests
                    if test_result.status == "failed":
                        result.stopped_early = True
                        
                        # Skip remaining tests
                        for remaining_test in category.tests[index + 1:]:
                            result.test_results.append(TestResult(
                                test_name=remaining_test.name,
                                test_path=self.tests_root / remaining_test.path,
                                test_type="test",
                                status="skipped",
                                duration_ms=0,
                                error=f"Skipped due to {test.name} failure",
                            ))
                        break
                
                # Run teardown if exists (always, even on failure)
                self._run_teardown_if_exists(category, page, context, result)
                
            finally:
                # Get video path before closing (if recording enabled)
                video_path = None
                if self.record_video and page.video:
                    video_path = page.video.path()
                
                # Close browser
                self.events.emit(RunnerEvent.BROWSER_CLOSING, {"category": category.name})
                browser_context.close()  # Close context first to finalize video
                browser.close()
                
                # Rename video file to include category name and timestamp
                if video_path and Path(video_path).exists():
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    new_video_path = Path(video_path).parent / f"{category.name}_{timestamp}.webm"
                    Path(video_path).rename(new_video_path)
                    print(f"  [Video] Saved: {new_video_path}")
                    
                    # Print video timestamps for easy navigation
                    if video_timestamps:
                        print(f"  [Video] Timeline:")
                        for test_name, start, end, status in video_timestamps:
                            start_str = f"{int(start//60):02d}:{int(start%60):02d}"
                            end_str = f"{int(end//60):02d}:{int(end%60):02d}"
                            status_icon = ">" if status == "passed" else "X" if status == "failed" else "-"
                            print(f"    [{status_icon}] {start_str} - {end_str} : {test_name}")
        
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
            
            self.events.emit(RunnerEvent.HEAL_REQUEST_CREATED, {
                "test": test_name,
                "path": str(heal_path),
            })
        
        return result
