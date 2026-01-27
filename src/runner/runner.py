"""
Main test runner orchestrator.

Coordinates test execution across categories, managing browser lifecycle,
context, and emitting events for real-time updates.
"""

import shutil
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
        config: Optional[dict] = None,
    ):
        """
        Initialize the test runner.
        
        Args:
            tests_root: Path to the tests/ directory
            headless: Whether to run browser in headless mode
            snapshots_dir: Directory for screenshots (default: snapshots/)
            record_video: Whether to record video of test execution (default: True)
            keep_open: Whether to keep browser open on failure for debugging (default: False)
            until_test: Stop before this test; dump context to until_test_context.json and leave browser open (for manual or MCP debugging; MCP uses a new session)
            config: Full config dict (e.g. from config.yaml); target subtree is stored in run logs and heal requests
        """
        self.tests_root = Path(tests_root)
        self.headless = headless
        self.snapshots_dir = snapshots_dir or Path("snapshots")
        self.record_video = record_video
        self.keep_open = keep_open
        self.until_test = until_test
        self.run_config = (config or {}).get("target") if config else None
        
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

    def _get_subcategory_by_segment(self, parent: Category, segment: str) -> Optional[Category]:
        """Find a direct subcategory of parent by segment name (case-insensitive, name or path tail)."""
        want = segment.strip().lower()
        for subcat in parent.subcategories or []:
            if subcat.name and subcat.name.strip().lower() == want:
                return subcat
            if subcat.path and subcat.path.name.strip().lower() == want:
                return subcat
            if subcat.path:
                path_str = subcat.path.as_posix().lower()
                if path_str.endswith("/" + want) or path_str == want:
                    return subcat
        return None

    def _resolve_category_path(self, path_str: str) -> Optional[List[Category]]:
        """
        Resolve a category path like "scheduling/appointments" or "a/b/c" to a chain of categories.
        Returns [root, child, ..., leaf] or None if any segment is not found.
        """
        parts = [p.strip() for p in path_str.split("/") if p.strip()]
        if not parts:
            return None
        root = self.get_category(parts[0])
        if not root:
            return None
        chain: List[Category] = [root]
        current = root
        for i in range(1, len(parts)):
            sub = self._get_subcategory_by_segment(current, parts[i])
            if not sub:
                return None
            chain.append(sub)
            current = sub
        return chain

    def run_all(self) -> RunResult:
        """
        Run all categories.
        
        Returns:
            RunResult with results from all categories
        """
        categories = self.get_categories()
        
        result = RunResult(started_at=datetime.now())
        
        # Start a new run in storage (pass config for run.json and runs_index)
        run_id = self.storage.start_run(config={"target": self.run_config} if self.run_config else None)
        
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
    
    def run_category(
        self,
        category_name: str,
        until_test: Optional[str] = None,
        subcategory_name: Optional[str] = None,
    ) -> CategoryResult:
        """
        Run a specific category.
        
        Args:
            category_name: Name of the category to run
            until_test: Stop before this test; dump context and leave browser open. If None, uses self.until_test.
            subcategory_name: If set, run only this subcategory (e.g. 'services'). Parent setup runs first.
            
        Returns:
            CategoryResult with results from the category
        """
        # Support path: xxx/yyy/zzz -> run setup of xxx, then setup of yyy, then setup and tests of zzz
        category_chain: Optional[List[Category]] = None
        if "/" in category_name:
            category_chain = self._resolve_category_path(category_name)
            if not category_chain:
                return CategoryResult(
                    category_name=category_name,
                    category_path=Path(category_name),
                    stopped_early=True,
                    test_results=[TestResult(
                        test_name="_path_resolve",
                        test_path=Path(category_name),
                        test_type="test",
                        status="failed",
                        duration_ms=0,
                        error=f"Category path not found: {category_name}",
                    )],
                )
            category = category_chain[0]
            total_tests = len(category_chain[-1].tests)
            path_for_display = "/".join((c.path.name for c in category_chain if c.path))
            subcategory_name = None  # path overrides --subcategory
        else:
            category = self.get_category(category_name)
            path_for_display = None
            total_tests = len(category.tests) if category else 0

        if not category:
            return CategoryResult(
                category_name=category_name,
                category_path=Path(category_name),
                stopped_early=True,
            )

        until_test_name = until_test or self.until_test

        # Total test count for events (if only one subcategory, count its tests)
        if not category_chain and subcategory_name and category.subcategories:
            for subcat in category.subcategories:
                if (
                    subcat.name.lower() == subcategory_name.lower()
                    or (subcat.path and subcat.path.name.lower() == subcategory_name.lower())
                ):
                    total_tests = len(subcat.tests)
                    break
        
        # Start a new run in storage (pass config for run.json and runs_index)
        run_id = self.storage.start_run(config={"target": self.run_config} if self.run_config else None)
        
        # Emit run started (single category)
        self.events.emit(RunnerEvent.RUN_STARTED, {
            "categories": [path_for_display or category.name],
            "total_categories": 1,
            "total_tests": total_tests,
            "run_id": run_id,
        })

        result = self._run_category_internal(
            category, 1, 1,
            until_test=until_test_name,
            subcategory_name=subcategory_name,
            category_chain=category_chain,
        )
        if path_for_display and result:
            result.category_name = path_for_display

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
        subcategory_name: Optional[str] = None,
        category_chain: Optional[List[Category]] = None,
    ) -> CategoryResult:
        """
        Internal method to run a single category.
        
        Args:
            category: Category to run (root when category_chain is set)
            category_index: Index of this category (1-based)
            total_categories: Total number of categories
            subcategory_name: If set, run only this subcategory (parent setup still runs).
            category_chain: If set (e.g. [root, yyy, zzz]), run root setup, then each intermediate's
                           setup, then leaf setup + tests. Takes precedence over subcategory_name.
            
        Returns:
            CategoryResult
        """
        result = CategoryResult(
            category_name=category.name,
            category_path=category.path,
        )
        # Track subcategory run dirs we save to (so we can copy parent video there)
        self._saved_subcategory_paths = []

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
        if self.run_config:
            if self.run_config.get("base_url"):
                context["base_url"] = self.run_config["base_url"]
            auth = self.run_config.get("auth")
            if isinstance(auth, dict):
                if auth.get("username"):
                    context["username"] = auth["username"]
                if auth.get("password"):
                    context["password"] = auth["password"]
        
        # Start browser for this category
        self.events.emit(RunnerEvent.BROWSER_STARTING, {"category": category.name})
        
        with sync_playwright() as playwright:
            # Launch new browser
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

                # Path mode: xxx/yyy/zzz -> root setup done; run each intermediate setup, then leaf setup + tests
                if category_chain and len(category_chain) >= 2:
                    for i in range(1, len(category_chain)):
                        parent_cat = category_chain[i - 1]
                        subcat = category_chain[i]
                        path_str = "/".join((c.path.name for c in category_chain[: i + 1] if c.path))
                        if subcat.setup and subcat.setup.is_valid:
                            test_start_offset = time_module.time() - video_start_time
                            setup_result = self._run_single_test(
                                test_path=self.tests_root / subcat.path / "_setup",
                                test_name=f"{subcat.name}/_setup",
                                test_type="setup",
                                page=page,
                                context=context,
                                index=0,
                                total=len(subcat.tests),
                                category_name=path_str,
                            )
                            test_end_offset = time_module.time() - video_start_time
                            video_timestamps.append((f"{subcat.name}/_setup", test_start_offset, test_end_offset, setup_result.status))
                            result.test_results.append(setup_result)
                            if setup_result.status == "failed":
                                result.stopped_early = True
                                for test in category_chain[-1].tests:
                                    result.test_results.append(TestResult(
                                        test_name=f"{category_chain[-1].name}/{test.name}",
                                        test_path=test.path,
                                        test_type="test",
                                        status="skipped",
                                        duration_ms=0,
                                        error=f"Skipped due to {subcat.name}/_setup failure",
                                    ))
                                # Teardown in reverse order: categories that were set up (0..i-1)
                                self._run_teardown_chain_reverse(
                                    category_chain[:i], page, context, result,
                                    video_timestamps, video_start_time, time_module,
                                )
                                return result
                    # Run leaf subcategory (setup already ran above for leaf, so skip setup)
                    leaf = category_chain[-1]
                    parent_of_leaf = category_chain[-2]
                    subcat_failed, _ = self._run_subcategory_inline(
                        subcategory=leaf,
                        page=page,
                        context=context,
                        result=result,
                        video_timestamps=video_timestamps,
                        video_start_time=video_start_time,
                        time_module=time_module,
                        parent_category=parent_of_leaf,
                        until_test=until_test,
                        skip_setup=True,
                    )
                    if subcat_failed:
                        result.stopped_early = True
                    if not getattr(result, "until_test_reached", False):
                        # Teardown in reverse order: zzz -> yyy -> xxx
                        self._run_teardown_chain_reverse(
                            category_chain, page, context, result,
                            video_timestamps, video_start_time, time_module,
                        )
                else:
                    # Build execution plan: interleave tests and subcategories based on run_after
                    execution_plan = self._build_execution_plan(category)
                    # If only one subcategory requested, use only that subcategory (don't filter the
                    # full plan: run_after can leave the requested subcategory out of the plan).
                    if subcategory_name:
                        want = subcategory_name.strip().lower()
                        chosen = None
                        for subcat in category.subcategories or []:
                            if subcat.name and subcat.name.strip().lower() == want:
                                chosen = subcat
                                break
                            if subcat.path:
                                path_str = subcat.path.as_posix().lower()
                                if path_str.endswith("/" + want) or path_str == want or subcat.path.name.strip().lower() == want:
                                    chosen = subcat
                                    break
                        if chosen is not None:
                            execution_plan = [chosen]
                        else:
                            result.stopped_early = True
                            available = [s.name for s in (category.subcategories or [])]
                            result.test_results.append(TestResult(
                                test_name=f"_subcategory_{subcategory_name}",
                                test_path=category.path,
                                test_type="test",
                                status="failed",
                                duration_ms=0,
                                error=f"Subcategory '{subcategory_name}' not found. Available: {available}",
                            ))
                            execution_plan = []
                    total_items = len(execution_plan)

                    # Run tests and subcategories in order
                    for index, item in enumerate(execution_plan):
                        if isinstance(item, Test):
                            # Run a test
                            test = item

                            # Check if we should stop before this test (for MCP debugging)
                            if until_test:
                                # Match test name (can be "Services/Edit Group Event" or "Edit Group Event")
                                # Also match by test ID (folder name like "remove_attendee")
                                test_full_name = f"{category.name}/{test.name}" if hasattr(category, 'name') else test.name
                                test_full_id = f"{category.name}/{test.id}" if hasattr(category, 'name') else test.id
                                # Also check subcategory format like "Services/Edit Group Event"
                                subcategory_prefix = ""
                                if hasattr(category, 'subcategories') and category.subcategories:
                                    # Try to find if test is in a subcategory
                                    for subcat in category.subcategories:
                                        if test in subcat.tests:
                                            subcategory_prefix = f"{subcat.name}/"
                                            break
                                test_with_subcat = f"{subcategory_prefix}{test.name}"
                                test_id_with_subcat = f"{subcategory_prefix}{test.id}"
                                if (test.name == until_test or
                                    test.id == until_test or
                                    test_full_name == until_test or
                                    test_full_id == until_test or
                                    test_with_subcat == until_test or
                                    test_id_with_subcat == until_test or
                                    until_test in test.name or
                                    until_test in test.id or
                                    until_test in test_full_name or
                                    until_test in test_full_id):
                                    result.stopped_early = True
                                    result.until_test_reached = True
                                    result.until_test_next_test = test_with_subcat or test_full_name or test.name
                                    self._skip_remaining_items(execution_plan[index:], result, test.name)
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

                            if test_result.status == "failed":
                                result.stopped_early = True
                                self._skip_remaining_items(execution_plan[index + 1:], result, test.name)
                                break

                        elif isinstance(item, Category):
                            subcategory = item
                            subcat_failed, failed_test_name = self._run_subcategory_inline(
                                subcategory=subcategory,
                                page=page,
                                context=context,
                                result=result,
                                video_timestamps=video_timestamps,
                                video_start_time=video_start_time,
                                time_module=time_module,
                                parent_category=category,
                                until_test=until_test,
                            )
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
                
                # If until_test was reached: dump context for MCP (new session), then keep browser open for manual debug.
                if getattr(result, 'until_test_reached', False):
                    import json as _json
                    next_test = getattr(result, 'until_test_next_test', '')
                    dump = {
                        "next_test": next_test,
                        "url": page.url,
                        "title": page.title(),
                        "context": {k: ("***" if k == "password" else v) for k, v in context.items()},
                    }
                    run_dir = self.storage.get_current_run_dir(category.name)
                    run_dir.mkdir(parents=True, exist_ok=True)
                    context_path = run_dir / "until_test_context.json"
                    with open(context_path, "w", encoding="utf-8") as f:
                        _json.dump(dump, f, indent=2)
                    print("\n  [--until-test] Stopped before test:", next_test)
                    print(f"  [--until-test] Context saved to: {context_path}")
                    print(f"  [--until-test] Next test would start at URL: {dump['url']}")
                    print(f"  [--until-test] Browser left open for manual debugging. (To debug with MCP, start a new MCP session and use this context/URL.)")
                    try:
                        import sys
                        if sys.stdin.isatty():
                            input("  [>] Press Enter to close browser and continue...")
                        else:
                            raise EOFError("Non-interactive")
                    except (EOFError, KeyboardInterrupt):
                        pass
                    self.events.emit(RunnerEvent.BROWSER_CLOSING, {"category": category.name})
                    browser_context.close()
                    browser.close()
                # If keep_open is enabled and there was a failure (but not until_test), wait for user
                elif self.keep_open and result.stopped_early:
                    print("\n  [!] Browser kept open for debugging (--keep-open flag)")
                    print(f"  [>] Current URL: {page.url}")
                    print(f"  [>] Current Title: {page.title()}")
                    try:
                        input("  [>] Press Enter to close browser and continue...")
                    except (EOFError, KeyboardInterrupt):
                        print("\n  [>] Closing browser...")
                    # Close browser after waiting
                    self.events.emit(RunnerEvent.BROWSER_CLOSING, {"category": category.name})
                    browser_context.close()  # Close context first to finalize video
                    browser.close()
                
                else:
                    # Close browser normally
                    self.events.emit(RunnerEvent.BROWSER_CLOSING, {"category": category.name})
                    browser_context.close()  # Close context first to finalize video
                    browser.close()
                
                # Process video and save to storage
                # Wait briefly for video file to appear (Playwright may finalize async on some systems)
                final_video_path = None
                if video_path:
                    import time as _time
                    for _ in range(30):  # up to ~3 seconds
                        if Path(video_path).exists():
                            break
                        _time.sleep(0.1)
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

        # Copy parent video into each subcategory run dir so video is visible there too
        if final_video_path is not None and getattr(self, "_saved_subcategory_paths", None):
            parent_video = self.storage.get_current_run_dir(category.name) / "video.webm"
            if parent_video.exists():
                for subcat_path in self._saved_subcategory_paths:
                    subcat_run_dir = self.storage.get_current_run_dir(subcat_path)
                    subcat_run_dir.mkdir(parents=True, exist_ok=True)
                    dest_video = subcat_run_dir / "video.webm"
                    if dest_video != parent_video:
                        shutil.copy2(str(parent_video), str(dest_video))

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

    def _run_teardown_chain_reverse(
        self,
        category_chain: List[Category],
        page: Page,
        context: dict,
        result: CategoryResult,
        video_timestamps: list,
        video_start_time: float,
        time_module,
    ) -> None:
        """Run teardowns for each category in reverse order (leaf -> ... -> root)."""
        root_teardown_result = None
        for cat in reversed(category_chain):
            if not (cat.teardown and cat.teardown.is_valid):
                continue
            path_str = cat.path.name if cat.path else cat.name
            test_name = f"{cat.name}/_teardown" if cat != category_chain[0] else "_teardown"
            test_start_offset = time_module.time() - video_start_time
            teardown_result = self._run_single_test(
                test_path=self.tests_root / cat.path / "_teardown",
                test_name=test_name,
                test_type="teardown",
                page=page,
                context=context,
                index=0,
                total=0,
                category_name=path_str,
            )
            test_end_offset = time_module.time() - video_start_time
            video_timestamps.append((test_name, test_start_offset, test_end_offset, teardown_result.status))
            result.test_results.append(teardown_result)
            if cat == category_chain[0]:
                root_teardown_result = teardown_result
        if root_teardown_result is not None:
            result.teardown_result = root_teardown_result
    
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
        
        # Update test_name to match the passed parameter (important for subcategory tests)
        # The executor uses test_path.name, but we want the full name with subcategory prefix
        result.test_name = test_name
        
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
                config=self.run_config,
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
        parent_category: Category,
        until_test: Optional[str] = None,
        skip_setup: bool = False,
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
            skip_setup: If True, do not run subcategory setup (e.g. already run in path mode).
            
        Returns:
            Tuple of (failed: bool, failed_test_name: str or None)
        """
        print(f"\n    >>> Subcategory: {subcategory.name}")
        
        # Build category path: parent/subcategory (e.g., "scheduling/appointments")
        category_path = f"{parent_category.path.name}/{subcategory.path.name}" if parent_category.path and subcategory.path else f"{parent_category.name}/{subcategory.name}"
        
        # Run subcategory setup if exists (unless skip_setup, e.g. path mode already ran it)
        if not skip_setup and subcategory.setup and subcategory.setup.is_valid:
            test_start_offset = time_module.time() - video_start_time
            setup_result = self._run_single_test(
                test_path=self.tests_root / subcategory.path / "_setup",
                test_name=f"{subcategory.name}/_setup",
                test_type="setup",
                page=page,
                context=context,
                index=0,
                total=len(subcategory.tests),
                category_name=category_path,
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
                # Save subcategory result before returning
                self._save_subcategory_result(subcategory, parent_category, result, category_path)
                return True, f"{subcategory.name}/_setup"
        
        # Run subcategory tests
        for index, test in enumerate(subcategory.tests):
            # Check if we should stop before this test (for MCP debugging)
            if until_test:
                # Match by both test name and test ID (folder name)
                test_full_name = f"{subcategory.name}/{test.name}"
                test_full_id = f"{subcategory.name}/{test.id}"
                if (test.name == until_test or 
                    test.id == until_test or
                    test_full_name == until_test or 
                    test_full_id == until_test or
                    until_test in test.name or
                    until_test in test.id or
                    until_test in test_full_name or
                    until_test in test_full_id):
                    result.stopped_early = True
                    result.until_test_reached = True
                    result.until_test_next_test = test_full_name
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
                    # Save subcategory result (without teardown) before returning
                    self._save_subcategory_result(subcategory, parent_category, result, category_path)
                    # Return early - browser will be kept open in finally block
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
                category_name=category_path,
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
                self._run_subcategory_teardown(subcategory, page, context, result, video_timestamps, video_start_time, time_module, parent_category)
                # Save subcategory result before returning
                self._save_subcategory_result(subcategory, parent_category, result, category_path)
                return True, f"{subcategory.name}/{test.name}"
        
        # Run subcategory teardown if exists
        self._run_subcategory_teardown(subcategory, page, context, result, video_timestamps, video_start_time, time_module, parent_category)
        
        # Extract subcategory results and save them separately
        self._save_subcategory_result(subcategory, parent_category, result, category_path)
        
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
        parent_category: Category,
    ) -> None:
        """Run subcategory teardown if it exists."""
        if subcategory.teardown and subcategory.teardown.is_valid:
            # Build category path: parent/subcategory (e.g., "scheduling/appointments")
            category_path = f"{parent_category.path.name}/{subcategory.path.name}" if parent_category.path and subcategory.path else f"{parent_category.name}/{subcategory.name}"
            
            test_start_offset = time_module.time() - video_start_time
            teardown_result = self._run_single_test(
                test_path=self.tests_root / subcategory.path / "_teardown",
                test_name=f"{subcategory.name}/_teardown",
                test_type="teardown",
                page=page,
                context=context,
                index=0,
                total=0,
                category_name=category_path,
            )
            test_end_offset = time_module.time() - video_start_time
            video_timestamps.append((f"{subcategory.name}/_teardown", test_start_offset, test_end_offset, teardown_result.status))
            result.test_results.append(teardown_result)
    
    def _save_subcategory_result(
        self,
        subcategory: Category,
        parent_category: Category,
        parent_result: CategoryResult,
        category_path: str,
    ) -> None:
        """
        Extract subcategory results from parent CategoryResult and save them separately.
        
        This creates a run.json file in the subcategory's _runs directory so that
        list_test_runs can find the runs.
        
        Args:
            subcategory: The subcategory that was run
            parent_category: The parent category
            parent_result: The parent's CategoryResult containing all results
            category_path: The category path (e.g., "clients/notes")
        """
        # Extract all results that belong to this subcategory
        # Subcategory results have test_name starting with "{subcategory.name}/"
        subcategory_prefix = f"{subcategory.name}/"
        
        subcategory_setup = None
        subcategory_teardown = None
        subcategory_tests = []
        
        # Filter results from parent_result.test_results
        for test_result in parent_result.test_results:
            if not test_result.test_name.startswith(subcategory_prefix):
                continue
            
            # Identify setup, teardown, and regular tests
            if test_result.test_name == f"{subcategory.name}/_setup" and test_result.test_type == "setup":
                subcategory_setup = test_result
            elif test_result.test_name == f"{subcategory.name}/_teardown" and test_result.test_type == "teardown":
                subcategory_teardown = test_result
            elif test_result.test_type == "test":
                # Regular test - remove the subcategory prefix from test_name for cleaner display
                # But keep the original test_name in the result for consistency
                subcategory_tests.append(test_result)
        
        # Create CategoryResult for subcategory
        subcategory_result = CategoryResult(
            category_name=subcategory.name,
            category_path=subcategory.path,
            setup_result=subcategory_setup,
            test_results=subcategory_tests,
            teardown_result=subcategory_teardown,
            stopped_early=parent_result.stopped_early,
        )
        
        # Save subcategory result (this creates run.json in subcategory's _runs directory)
        # Don't pass video_path - subcategory shares parent's video (copied after parent save)
        self.storage.save_category_result(
            category=category_path,
            result=subcategory_result,
            video_path=None,
        )
        self._saved_subcategory_paths.append(category_path)
