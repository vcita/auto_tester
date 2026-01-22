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
    
    def start_run(self) -> str:
        """
        Generate and set the current run_id (timestamp-based).
        
        Returns:
            The generated run_id (format: YYYYMMDD_HHMMSS)
        """
        self.current_run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._current_categories = []
        return self.current_run_id
    
    def get_category_runs_dir(self, category: str) -> Path:
        """
        Get the _runs directory for a category.
        
        Args:
            category: Category name
            
        Returns:
            Path to tests/{category}/_runs/
        """
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
        
        # Save run.json
        run_json_path = run_dir / "run.json"
        run_data = result.to_dict()
        run_data["run_id"] = self.current_run_id
        run_data["saved_at"] = datetime.now().isoformat()
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
        }
        
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
                    runs.append(data)
                except (json.JSONDecodeError, IOError):
                    # Skip corrupted files
                    pass
        
        return runs
    
    def list_all_runs(self) -> List[Dict]:
        """
        List all runs from the index directory.
        
        Returns:
            List of run index data, newest first
        """
        if not self.index_dir.exists():
            return []
        
        runs = []
        for index_file in sorted(self.index_dir.iterdir(), key=lambda f: f.name, reverse=True):
            if index_file.suffix != ".json":
                continue
            try:
                data = json.loads(index_file.read_text(encoding="utf-8"))
                runs.append(data)
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
