"""
Run storage for persisting test run history.

Stores run data per-category in tests/{category}/_runs/ with:
- run.json: Category run result + metadata
- video.webm: Video recording
- tests/{test_name}/result.json: Individual test results
- tests/{test_name}/screenshot.png: Failure screenshots
- tests/{test_name}/heal_request.md: Heal request copies

Also maintains a root index at runs_index/ for correlating multi-category runs.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .models import CategoryResult, RunResult, TestResult


class RunStorage:
    """Manages persistent storage of test run history."""
    
    RUNS_DIR_NAME = "_runs"
    INDEX_DIR_NAME = "runs_index"
    
    def __init__(self, tests_root: Path, max_runs_per_category: int = 100):
        """
        Initialize run storage.
        
        Args:
            tests_root: Path to the tests/ directory
            max_runs_per_category: Maximum runs to keep per category (oldest deleted)
        """
        self.tests_root = tests_root
        self.max_runs = max_runs_per_category
        self.index_dir = tests_root.parent / self.INDEX_DIR_NAME
        self.current_run_id: Optional[str] = None
        self._current_categories: List[str] = []
        self._run_config: Optional[Dict] = None

    @staticmethod
    def _sanitize_config(config: Optional[Dict]) -> Optional[Dict]:
        """Return target config safe for logs (no plaintext password)."""
        if not config:
            return None
        target = config.get("target") if isinstance(config.get("target"), dict) else config
        if not target:
            return None
        auth = target.get("auth") if isinstance(target.get("auth"), dict) else {}
        return {
            "target": {
                "base_url": target.get("base_url"),
                "auth": {"username": auth.get("username")} if auth else None,
            }
        }
    
    def start_run(self, config: Optional[Dict] = None) -> str:
        """
        Generate and set the current run_id (timestamp-based).
        Optionally store config for inclusion in run.json and runs_index (password omitted).

        Returns:
            The generated run_id (format: YYYYMMDD_HHMMSS)
        """
        self.current_run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._current_categories = []
        self._run_config = self._sanitize_config(config)
        return self.current_run_id
    
    def get_category_runs_dir(self, category: str) -> Path:
        """
        Get the _runs directory for a category.
        
        Args:
            category: Category name or path (e.g., 'scheduling' or 'scheduling/appointments')
            
        Returns:
            Path to tests/{category}/_runs/ or tests/{parent}/{subcategory}/_runs/
        """
        # Handle nested category paths (e.g., "scheduling/appointments")
        if "/" in category:
            # Split into parent and subcategory
            parts = category.split("/")
            return self.tests_root / "/".join(parts) / self.RUNS_DIR_NAME
        return self.tests_root / category / self.RUNS_DIR_NAME
    
    def get_current_run_dir(self, category: str) -> Path:
        """
        Get the current run directory for a category.
        
        Args:
            category: Category name
            
        Returns:
            Path to tests/{category}/_runs/{run_id}/
        """
        if not self.current_run_id:
            raise ValueError("No active run. Call start_run() first.")
        return self.get_category_runs_dir(category) / self.current_run_id
    
    def save_test_result(
        self,
        category: str,
        test_name: str,
        result: TestResult,
        screenshot_path: Optional[Path] = None
    ) -> Path:
        """
        Save an individual test result.
        
        Args:
            category: Category name
            test_name: Test name (e.g., 'create_matter')
            result: TestResult to save
            screenshot_path: Optional path to failure screenshot to copy
            
        Returns:
            Path to the saved result.json
        """
        run_dir = self.get_current_run_dir(category)
        test_dir = run_dir / "tests" / test_name
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # Save result.json
        result_path = test_dir / "result.json"
        result_data = result.to_dict()
        result_data["saved_at"] = datetime.now().isoformat()
        result_path.write_text(json.dumps(result_data, indent=2), encoding="utf-8")
        
        # Copy screenshot if provided
        if screenshot_path and screenshot_path.exists():
            dest_screenshot = test_dir / "screenshot.png"
            shutil.copy2(screenshot_path, dest_screenshot)
            # Update result to point to new location
            result_data["screenshot"] = str(dest_screenshot)
            result_path.write_text(json.dumps(result_data, indent=2), encoding="utf-8")
        
        return result_path
    
    def save_heal_request(
        self,
        category: str,
        test_name: str,
        heal_request_path: Path
    ) -> Optional[Path]:
        """
        Copy a heal request to the run storage.
        
        Args:
            category: Category name
            test_name: Test name
            heal_request_path: Path to the heal request markdown file
            
        Returns:
            Path to the copied heal request, or None if source doesn't exist
        """
        if not heal_request_path.exists():
            return None
            
        run_dir = self.get_current_run_dir(category)
        test_dir = run_dir / "tests" / test_name
        test_dir.mkdir(parents=True, exist_ok=True)
        
        dest_path = test_dir / "heal_request.md"
        shutil.copy2(heal_request_path, dest_path)
        return dest_path
    
    def save_category_result(
        self,
        category: str,
        result: CategoryResult,
        video_path: Optional[Path] = None
    ) -> Path:
        """
        Save category run result and optionally move video.
        
        Args:
            category: Category name
            result: CategoryResult to save
            video_path: Optional path to video file to move
            
        Returns:
            Path to the saved run.json
        """
        run_dir = self.get_current_run_dir(category)
        run_dir.mkdir(parents=True, exist_ok=True)
        
        # Track this category for the index
        if category not in self._current_categories:
            self._current_categories.append(category)
        
        # Save run.json (include config snapshot for this run; no password)
        run_json_path = run_dir / "run.json"
        run_data = result.to_dict()
        run_data["run_id"] = self.current_run_id
        run_data["saved_at"] = datetime.now().isoformat()
        if self._run_config is not None:
            run_data["config"] = self._run_config
        run_json_path.write_text(json.dumps(run_data, indent=2), encoding="utf-8")
        
        # Move video if provided
        if video_path and video_path.exists():
            dest_video = run_dir / "video.webm"
            shutil.move(str(video_path), str(dest_video))
            run_data["video"] = str(dest_video)
            run_json_path.write_text(json.dumps(run_data, indent=2), encoding="utf-8")
        
        # Cleanup old runs
        self.cleanup_old_runs(category)
        
        return run_json_path
    
    def finalize_run(self, run_result: RunResult) -> Path:
        """
        Create/update the runs_index file for multi-category correlation.
        
        Args:
            run_result: The complete RunResult
            
        Returns:
            Path to the index file
        """
        if not self.current_run_id:
            raise ValueError("No active run to finalize.")
        
        self.index_dir.mkdir(parents=True, exist_ok=True)
        index_path = self.index_dir / f"{self.current_run_id}.json"
        
        # Collect failed tests with their category paths
        failed_tests = []
        for category_result in run_result.category_results:
            # Get base category path for this category
            base_category_path = None
            if category_result.category_path:
                try:
                    # Get relative path from tests_root
                    rel_path = category_result.category_path.relative_to(self.tests_root)
                    base_category_path = str(rel_path).replace("\\", "/")
                except ValueError:
                    base_category_path = category_result.category_name
            
            if not base_category_path:
                base_category_path = category_result.category_name
            
            def get_category_path_for_test(test_result):
                """Extract the actual category path where the test was saved."""
                # For subcategory tests, test_name includes subcategory prefix (e.g., "Appointments/Cancel Appointment")
                # and test_path shows the full path (e.g., "tests/scheduling/appointments/cancel_appointment")
                if test_result.test_path:
                    try:
                        # Extract category path from test_path
                        rel_test_path = test_result.test_path.relative_to(self.tests_root)
                        # Get parent directory (removes test folder name)
                        category_path_from_test = str(rel_test_path.parent).replace("\\", "/")
                        return category_path_from_test
                    except (ValueError, AttributeError):
                        pass
                
                # Fallback: check if test_name has subcategory prefix
                if "/" in test_result.test_name:
                    # Test name like "Appointments/Cancel Appointment" or "Services/Create Service"
                    subcategory_name = test_result.test_name.split("/")[0]
                    # Build nested path: parent/subcategory
                    return f"{base_category_path}/{subcategory_name}"
                
                # Default to base category path
                return base_category_path
            
            # Check setup failures
            if category_result.setup_result and category_result.setup_result.status == "failed":
                category_path = get_category_path_for_test(category_result.setup_result)
                failed_tests.append({
                    "test_name": category_result.setup_result.test_name,
                    "category": category_result.category_name,
                    "category_path": category_path,
                    "test_type": category_result.setup_result.test_type,
                    "error": category_result.setup_result.error,
                    "error_type": category_result.setup_result.error_type,
                })
            
            # Check test failures
            for test_result in category_result.test_results:
                if test_result.status == "failed":
                    category_path = get_category_path_for_test(test_result)
                    failed_tests.append({
                        "test_name": test_result.test_name,
                        "category": category_result.category_name,
                        "category_path": category_path,
                        "test_type": test_result.test_type,
                        "error": test_result.error,
                        "error_type": test_result.error_type,
                    })
            
            # Check teardown failures
            if category_result.teardown_result and category_result.teardown_result.status == "failed":
                category_path = get_category_path_for_test(category_result.teardown_result)
                failed_tests.append({
                    "test_name": category_result.teardown_result.test_name,
                    "category": category_result.category_name,
                    "category_path": category_path,
                    "test_type": category_result.teardown_result.test_type,
                    "error": category_result.teardown_result.error,
                    "error_type": category_result.teardown_result.error_type,
                })
        
        index_data = {
            "run_id": self.current_run_id,
            "started_at": run_result.started_at.isoformat(),
            "completed_at": run_result.completed_at.isoformat() if run_result.completed_at else None,
            "categories": self._current_categories,
            "status": run_result.status,
            "summary": {
                "passed": run_result.total_passed,
                "failed": run_result.total_failed,
                "skipped": run_result.total_skipped,
                "total": run_result.total_tests,
            },
            "duration_ms": run_result.duration_ms,
            "failed_tests": failed_tests,
        }
        if self._run_config is not None:
            index_data["config"] = self._run_config
        
        index_path.write_text(json.dumps(index_data, indent=2), encoding="utf-8")
        
        # Cleanup old index files
        self._cleanup_old_index_files()
        
        return index_path
    
    def cleanup_old_runs(self, category: str) -> int:
        """
        Delete oldest runs if count exceeds max_runs.
        
        Args:
            category: Category name
            
        Returns:
            Number of runs deleted
        """
        runs_dir = self.get_category_runs_dir(category)
        if not runs_dir.exists():
            return 0
        
        # Get all run directories sorted by name (timestamp = chronological)
        run_dirs = sorted(
            [d for d in runs_dir.iterdir() if d.is_dir()],
            key=lambda d: d.name
        )
        
        deleted = 0
        while len(run_dirs) > self.max_runs:
            oldest = run_dirs.pop(0)
            shutil.rmtree(oldest)
            deleted += 1
        
        return deleted
    
    def _cleanup_old_index_files(self) -> int:
        """
        Delete oldest index files if count exceeds max_runs.
        
        Returns:
            Number of index files deleted
        """
        if not self.index_dir.exists():
            return 0
        
        index_files = sorted(
            [f for f in self.index_dir.iterdir() if f.suffix == ".json"],
            key=lambda f: f.name
        )
        
        deleted = 0
        while len(index_files) > self.max_runs:
            oldest = index_files.pop(0)
            oldest.unlink()
            deleted += 1
        
        return deleted
    
    def list_category_runs(self, category: str) -> List[Dict]:
        """
        List all runs for a specific category.
        
        Args:
            category: Category name
            
        Returns:
            List of run metadata dicts, newest first
        """
        runs_dir = self.get_category_runs_dir(category)
        if not runs_dir.exists():
            return []
        
        runs = []
        for run_dir in sorted(runs_dir.iterdir(), key=lambda d: d.name, reverse=True):
            if not run_dir.is_dir():
                continue
            run_json = run_dir / "run.json"
            if run_json.exists():
                try:
                    data = json.loads(run_json.read_text(encoding="utf-8"))
                    # Ensure run_id is set (from directory name, which is the source of truth)
                    data["run_id"] = run_dir.name
                    # Set category field (normalize to lowercase for consistency)
                    data["category"] = category.lower()
                    runs.append(data)
                except (json.JSONDecodeError, IOError):
                    # Skip corrupted files
                    pass
        
        return runs
    
    def list_all_runs(self) -> List[Dict]:
        """
        List all runs from all categories and the index directory.
        
        Returns:
            List of run data, newest first. For "All Categories" view:
            - Multi-category runs from index (shown once)
            - Individual category runs that aren't in index
            This avoids showing the same run multiple times in the all-runs view.
        """
        runs = []
        index_runs_by_id = {}  # Track index runs by run_id
        category_runs_by_id = {}  # Track category runs by (run_id, category) to avoid duplicates
        
        # First, get runs from index (these are multi-category runs)
        if self.index_dir.exists():
            for index_file in sorted(self.index_dir.iterdir(), key=lambda f: f.name, reverse=True):
                if index_file.suffix != ".json":
                    continue
                try:
                    data = json.loads(index_file.read_text(encoding="utf-8"))
                    run_id = data.get("run_id")
                    if run_id:
                        index_runs_by_id[run_id] = data
                        runs.append(data)
                except (json.JSONDecodeError, IOError):
                    pass
        
        # Then, scan all category _runs directories (including subcategories) to find individual category runs
        def scan_runs_directory(category_path: Path, category_name: str):
            """Recursively scan a category directory for _runs folders."""
            runs_dir = category_path / self.RUNS_DIR_NAME
            if runs_dir.exists():
                for run_dir in sorted(runs_dir.iterdir(), key=lambda d: d.name, reverse=True):
                    if not run_dir.is_dir():
                        continue
                    
                    run_id = run_dir.name
                    run_json = run_dir / "run.json"
                    
                    if run_json.exists():
                        try:
                            data = json.loads(run_json.read_text(encoding="utf-8"))
                            # Ensure run_id is set (from directory name, which is the source of truth)
                            data["run_id"] = run_id
                            # Normalize category name to lowercase
                            category_from_path = category_name.lower()
                            data["category"] = category_from_path
                            
                            # Only add category runs that aren't already in index
                            # (Index runs are more complete for multi-category runs)
                            if run_id not in index_runs_by_id:
                                # Also check for duplicates within category runs
                                key = (run_id, category_from_path)
                                if key not in category_runs_by_id:
                                    category_runs_by_id[key] = True
                                    runs.append(data)
                        except (json.JSONDecodeError, IOError):
                            pass
            
            # Recursively scan subdirectories
            for subdir in category_path.iterdir():
                if subdir.is_dir() and not subdir.name.startswith("_") and subdir.name != self.RUNS_DIR_NAME:
                    # Check if it's a subcategory (has _category.yaml or contains _runs)
                    subcategory_name = f"{category_name}/{subdir.name}" if category_name != subdir.name else subdir.name
                    scan_runs_directory(subdir, subcategory_name)
        
        # Start scanning from top-level categories
        for category_dir in self.tests_root.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith("_"):
                continue
            scan_runs_directory(category_dir, category_dir.name)
        
        # Sort by run_id (timestamp) descending
        runs.sort(key=lambda r: r.get("run_id", ""), reverse=True)
        
        return runs
    
    def get_all_last_results(self) -> List[Dict]:
        """
        Get the latest result (passed/failed/skipped) for every test that has been run.
        Scans all category _runs directories and returns the most recent result per test.
        
        Returns:
            List of dicts with keys: category_path (str), test_name (str, as stored in run dir), status (str)
        """
        results: List[Dict] = []
        
        def scan_category_runs(category_path: Path, category_name: str):
            runs_dir = category_path / self.RUNS_DIR_NAME
            if not runs_dir.exists():
                return
            run_dirs = sorted(
                [d for d in runs_dir.iterdir() if d.is_dir()],
                key=lambda d: d.name,
                reverse=True
            )
            if not run_dirs:
                return
            latest_run = run_dirs[0]
            tests_dir = latest_run / "tests"
            if not tests_dir.exists():
                return
            category_path_str = str(category_path.relative_to(self.tests_root)).replace("\\", "/")
            for test_dir in tests_dir.iterdir():
                if not test_dir.is_dir():
                    continue
                result_json = test_dir / "result.json"
                if not result_json.exists():
                    continue
                try:
                    data = json.loads(result_json.read_text(encoding="utf-8"))
                    status = data.get("status")
                    if status in ("passed", "failed", "skipped"):
                        results.append({
                            "category_path": category_path_str,
                            "test_name": test_dir.name,
                            "status": status,
                        })
                except (json.JSONDecodeError, IOError):
                    pass
            
            for subdir in category_path.iterdir():
                if subdir.is_dir() and not subdir.name.startswith("_") and subdir.name != self.RUNS_DIR_NAME:
                    subcat_name = f"{category_name}/{subdir.name}" if category_name != subdir.name else subdir.name
                    scan_category_runs(subdir, subcat_name)
        
        for category_dir in self.tests_root.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith("_"):
                continue
            try:
                scan_category_runs(category_dir, category_dir.name)
            except ValueError:
                continue
        
        return results
    
    def list_test_runs(self, category: str, test_name: str) -> List[Dict]:
        """
        List all runs that contain a specific test.
        
        Args:
            category: Category name (parent category, e.g., 'scheduling')
            test_name: Test name (e.g., 'Create Service' or 'create_service')
            
        Returns:
            List of run metadata dicts that contain this test, newest first
        """
        # First, try the parent category's runs directory
        runs_dir = self.get_category_runs_dir(category)
        runs = []
        run_ids_found = set()
        
        if runs_dir.exists():
            for run_dir in sorted(runs_dir.iterdir(), key=lambda d: d.name, reverse=True):
                if not run_dir.is_dir():
                    continue
                
                run_id = run_dir.name
                
                # Check if this run contains the test (try different name formats)
                test_dir = run_dir / "tests" / test_name
                if not test_dir.exists():
                    # Try lowercase version
                    test_dir = run_dir / "tests" / test_name.lower().replace(" ", "_")
                if not test_dir.exists():
                    # Try with subcategory prefix (e.g., "Services/Create Service")
                    # Check all subdirectories in tests/ for matching test names
                    tests_dir = run_dir / "tests"
                    if tests_dir.exists():
                        for subdir in tests_dir.iterdir():
                            if subdir.is_dir():
                                # Check if subdir name matches test (case-insensitive)
                                if subdir.name.lower() == test_name.lower() or \
                                   subdir.name.lower() == test_name.lower().replace(" ", "_"):
                                    test_dir = subdir
                                    break
                                # Also check subcategory/test format
                                for subcat_dir in subdir.iterdir():
                                    if subcat_dir.is_dir() and \
                                       (subcat_dir.name.lower() == test_name.lower() or \
                                        subcat_dir.name.lower() == test_name.lower().replace(" ", "_")):
                                        test_dir = subcat_dir
                                        break
                
                if not test_dir.exists():
                    continue
                
                # Check if test has a result
                result_json = test_dir / "result.json"
                if not result_json.exists():
                    continue
                
                # Load run.json for metadata
                run_json = run_dir / "run.json"
                if run_json.exists():
                    try:
                        data = json.loads(run_json.read_text(encoding="utf-8"))
                        # Add test-specific result
                        test_result = json.loads(result_json.read_text(encoding="utf-8"))
                        data["test_result"] = test_result
                        data["test_name"] = test_name
                        data["run_id"] = run_id
                        runs.append(data)
                        run_ids_found.add(run_id)
                    except (json.JSONDecodeError, IOError):
                        pass
        
        # Also check subcategory runs directories
        # Subcategories might have their own _runs directories either:
        # 1. As nested paths: tests/scheduling/appointments/_runs/ (new behavior)
        # 2. As subdirectories: tests/scheduling/services/_runs/ (legacy)
        # 3. As top-level categories: tests/appointments/_runs/ (legacy, if subcategory name matches a top-level category)
        category_path = self.tests_root / category
        if category_path.exists():
            # First, check nested subcategory paths (e.g., scheduling/appointments/_runs/)
            # This is the new behavior where subcategory runs are saved under parent/subcategory
            for subdir in category_path.iterdir():
                if subdir.is_dir() and not subdir.name.startswith("_"):
                    # Check nested path: tests/scheduling/appointments/_runs/
                    nested_runs_dir = subdir / self.RUNS_DIR_NAME
                    if nested_runs_dir.exists():
                        for run_dir in sorted(nested_runs_dir.iterdir(), key=lambda d: d.name, reverse=True):
                            if not run_dir.is_dir():
                                continue
                            
                            run_id = run_dir.name
                            # Skip if we already found this run in the parent category
                            if run_id in run_ids_found:
                                continue
                            
                            # First, check if run.json exists and contains the test in test_results
                            run_json = run_dir / "run.json"
                            test_found_in_json = False
                            matching_test_result = None
                            
                            if run_json.exists():
                                try:
                                    data = json.loads(run_json.read_text(encoding="utf-8"))
                                    # Check test_results array for matching test name
                                    # Handle variations: "Edit Note", "edit_note", "Notes/Edit Note", etc.
                                    test_name_lower = test_name.lower()
                                    test_name_underscore = test_name.replace(" ", "_").lower()
                                    test_name_space = test_name.replace("_", " ").lower()
                                    
                                    for tr in data.get("test_results", []):
                                        tr_name = tr.get("test_name", "").lower()
                                        tr_simple = tr_name.split("/")[-1]  # Get simple name without subcategory prefix
                                        # Check if test name matches (exact, or with subcategory prefix, or simple name)
                                        # Also handle space/underscore variations
                                        if (tr_name == test_name_lower or
                                            tr_name == test_name_underscore or
                                            tr_name == test_name_space or
                                            tr_simple == test_name_lower or
                                            tr_simple == test_name_underscore or
                                            tr_simple == test_name_space or
                                            tr_name.endswith(f"/{test_name_lower}") or
                                            tr_name.endswith(f"/{test_name_underscore}") or
                                            tr_name.endswith(f"/{test_name_space}")):
                                            test_found_in_json = True
                                            matching_test_result = tr
                                            break
                                except (json.JSONDecodeError, IOError):
                                    pass
                            
                            # Also check test directory (for backward compatibility)
                            test_dir = None
                            test_name_variants = [
                                test_name,
                                test_name.lower().replace(" ", "_"),
                                test_name.replace(" ", "_"),
                                test_name.title().replace(" ", "_"),
                            ]
                            
                            for variant in test_name_variants:
                                test_dir = run_dir / "tests" / variant
                                if test_dir.exists():
                                    break
                            
                            # If found in run.json, use that; otherwise check directory
                            if test_found_in_json and matching_test_result:
                                try:
                                    data = json.loads(run_json.read_text(encoding="utf-8"))
                                    data["test_result"] = matching_test_result
                                    data["test_name"] = test_name
                                    data["run_id"] = run_id
                                    data["category"] = category.lower()
                                    runs.append(data)
                                    run_ids_found.add(run_id)
                                except (json.JSONDecodeError, IOError):
                                    pass
                            elif test_dir and test_dir.exists():
                                # Check if test has a result
                                result_json = test_dir / "result.json"
                                if result_json.exists():
                                    if run_json.exists():
                                        try:
                                            data = json.loads(run_json.read_text(encoding="utf-8"))
                                            test_result = json.loads(result_json.read_text(encoding="utf-8"))
                                            data["test_result"] = test_result
                                            data["test_name"] = test_name
                                            data["run_id"] = run_id
                                            data["category"] = category.lower()
                                            runs.append(data)
                                            run_ids_found.add(run_id)
                                        except (json.JSONDecodeError, IOError):
                                            pass
                                    else:
                                        # If run.json doesn't exist but test directory does, still try to load the result
                                        try:
                                            test_result = json.loads(result_json.read_text(encoding="utf-8"))
                                            data = {
                                                "test_result": test_result,
                                                "test_name": test_name,
                                                "run_id": run_id,
                                                "category": category.lower(),
                                                "status": test_result.get("status", "unknown"),
                                            }
                                            runs.append(data)
                                            run_ids_found.add(run_id)
                                        except (json.JSONDecodeError, IOError):
                                            pass
        
        # Also check if subcategory names exist as top-level category directories
        # (e.g., "appointments" subcategory might have runs in tests/appointments/_runs/)
        # Get subcategory names from the category structure
        from src.discovery import TestDiscovery
        discovery = TestDiscovery(self.tests_root)
        categories = discovery.scan()
        parent_category = next((c for c in categories if c.name.lower() == category.lower() or (c.path and c.path.name.lower() == category.lower())), None)
        
        if parent_category and parent_category.subcategories:
            for subcat in parent_category.subcategories:
                # Check if subcategory name matches a top-level category directory
                subcat_runs_dir = self.tests_root / subcat.path.name / self.RUNS_DIR_NAME if subcat.path else None
                if not subcat_runs_dir or not subcat_runs_dir.exists():
                    # Also try by subcategory name directly
                    subcat_runs_dir = self.tests_root / subcat.name.lower() / self.RUNS_DIR_NAME
                
                if subcat_runs_dir and subcat_runs_dir.exists():
                    for run_dir in sorted(subcat_runs_dir.iterdir(), key=lambda d: d.name, reverse=True):
                        if not run_dir.is_dir():
                            continue
                        
                        run_id = run_dir.name
                        # Skip if we already found this run
                        if run_id in run_ids_found:
                            continue
                        
                # First, check if run.json exists and contains the test in test_results
                run_json = run_dir / "run.json"
                test_found_in_json = False
                matching_test_result = None
                
                if run_json.exists():
                    try:
                        data = json.loads(run_json.read_text(encoding="utf-8"))
                        # Check test_results array for matching test name
                        # Handle variations: "Edit Note", "edit_note", "Notes/Edit Note", etc.
                        test_name_lower = test_name.lower()
                        test_name_underscore = test_name.replace(" ", "_").lower()
                        test_name_space = test_name.replace("_", " ").lower()
                        
                        # Normalize test name for comparison (remove spaces/underscores)
                        def normalize_name(name):
                            return name.replace(" ", "").replace("_", "").lower()
                        
                        test_name_normalized = normalize_name(test_name)
                        
                        for tr in data.get("test_results", []):
                            tr_name = tr.get("test_name", "").lower()
                            tr_simple = tr_name.split("/")[-1]  # Get simple name without subcategory prefix
                            tr_normalized = normalize_name(tr_name)
                            tr_simple_normalized = normalize_name(tr_simple)
                            
                            # Check if test name matches (exact, or with subcategory prefix, or simple name)
                            # Also handle space/underscore variations by normalizing
                            if (tr_name == test_name_lower or
                                tr_name == test_name_underscore or
                                tr_name == test_name_space or
                                tr_simple == test_name_lower or
                                tr_simple == test_name_underscore or
                                tr_simple == test_name_space or
                                tr_normalized == test_name_normalized or
                                tr_simple_normalized == test_name_normalized or
                                tr_name.endswith(f"/{test_name_lower}") or
                                tr_name.endswith(f"/{test_name_underscore}") or
                                tr_name.endswith(f"/{test_name_space}")):
                                test_found_in_json = True
                                matching_test_result = tr
                                break
                    except (json.JSONDecodeError, IOError):
                        pass
                
                # Also check test directory (for backward compatibility)
                test_dir = None
                test_name_variants = [
                    test_name,
                    test_name.lower().replace(" ", "_"),
                    test_name.replace(" ", "_"),
                    test_name.title().replace(" ", "_"),
                ]
                
                for variant in test_name_variants:
                    test_dir = run_dir / "tests" / variant
                    if test_dir.exists():
                        break
                
                # If found in run.json, use that; otherwise check directory
                if test_found_in_json and matching_test_result:
                    try:
                        data = json.loads(run_json.read_text(encoding="utf-8"))
                        data["test_result"] = matching_test_result
                        data["test_name"] = test_name
                        data["run_id"] = run_id
                        data["category"] = category.lower()
                        runs.append(data)
                        run_ids_found.add(run_id)
                    except (json.JSONDecodeError, IOError):
                        pass
                elif test_dir and test_dir.exists():
                    # Check if test has a result
                    result_json = test_dir / "result.json"
                    if result_json.exists():
                        if run_json.exists():
                            try:
                                data = json.loads(run_json.read_text(encoding="utf-8"))
                                test_result = json.loads(result_json.read_text(encoding="utf-8"))
                                data["test_result"] = test_result
                                data["test_name"] = test_name
                                data["run_id"] = run_id
                                data["category"] = category.lower()
                                runs.append(data)
                                run_ids_found.add(run_id)
                            except (json.JSONDecodeError, IOError):
                                pass
        
        return runs
    
    def get_run_details(self, category: str, run_id: str) -> Optional[Dict]:
        """
        Get detailed run data for a specific category and run.
        
        Args:
            category: Category name
            run_id: Run ID (timestamp)
            
        Returns:
            Run data dict with test results, or None if not found
        """
        run_dir = self.get_category_runs_dir(category) / run_id
        if not run_dir.exists():
            return None
        
        run_json = run_dir / "run.json"
        if not run_json.exists():
            return None
        
        try:
            data = json.loads(run_json.read_text(encoding="utf-8"))
            
            # Add paths to artifacts
            video_path = run_dir / "video.webm"
            if video_path.exists():
                data["video_path"] = str(video_path)
            
            # Load individual test results with artifact paths
            tests_dir = run_dir / "tests"
            if tests_dir.exists():
                data["test_artifacts"] = {}
                for test_dir in tests_dir.iterdir():
                    if not test_dir.is_dir():
                        continue
                    artifacts = {}
                    
                    screenshot = test_dir / "screenshot.png"
                    if screenshot.exists():
                        artifacts["screenshot"] = str(screenshot)
                    
                    heal_request = test_dir / "heal_request.md"
                    if heal_request.exists():
                        artifacts["heal_request"] = str(heal_request)
                    
                    result_json = test_dir / "result.json"
                    if result_json.exists():
                        artifacts["result"] = json.loads(result_json.read_text(encoding="utf-8"))
                    
                    if artifacts:
                        data["test_artifacts"][test_dir.name] = artifacts
            
            return data
        except (json.JSONDecodeError, IOError):
            return None
