"""
Test Discovery Module

Scans the tests/ folder to find all categories and tests.
Uses hybrid approach:
- Auto-detect: Any folder with steps.md is a test
- Enrich: _category.yaml provides metadata overrides
"""

import yaml
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.models import Category, Test, TestStatus, TestPriority, SetupTeardown


class TestDiscovery:
    """Discovers and loads test categories and tests from the filesystem."""
    
    CATEGORY_FILE = "_category.yaml"
    STEPS_FILE = "steps.md"
    SETUP_FOLDER = "_setup"
    TEARDOWN_FOLDER = "_teardown"
    FUNCTIONS_FOLDER = "_functions"
    
    def __init__(self, tests_root: str | Path):
        """
        Initialize test discovery.
        
        Args:
            tests_root: Path to the tests/ directory
        """
        self.tests_root = Path(tests_root)
        if not self.tests_root.exists():
            raise ValueError(f"Tests root does not exist: {self.tests_root}")
    
    def scan(self) -> list[Category]:
        """
        Scan the tests directory and return all categories.
        
        Returns:
            List of top-level Category objects (with nested subcategories)
        """
        categories = []
        
        for item in sorted(self.tests_root.iterdir()):
            # Skip hidden folders, _functions folder, and non-directories
            if not item.is_dir():
                continue
            if item.name.startswith(".") or item.name.startswith("_"):
                continue
            
            category = self._scan_category(item)
            if category:
                categories.append(category)
        
        return categories
    
    def _scan_category(
        self, 
        path: Path, 
        parent: Optional[Category] = None
    ) -> Optional[Category]:
        """
        Scan a single category folder.
        
        Args:
            path: Path to the category folder
            parent: Parent category (for nested categories)
            
        Returns:
            Category object or None if not a valid category
        """
        # Load category metadata from YAML if exists
        category_file = path / self.CATEGORY_FILE
        yaml_data = self._load_category_yaml(category_file)
        
        # Auto-discover setup and teardown
        setup = self._discover_setup_teardown(path, self.SETUP_FOLDER)
        teardown = self._discover_setup_teardown(path, self.TEARDOWN_FOLDER)
        
        # execution_order must be a list (avoid string or other type from YAML)
        raw_order = yaml_data.get("execution_order")
        execution_order = raw_order if isinstance(raw_order, list) and len(raw_order) > 0 else None

        # Create category
        category = Category(
            name=yaml_data.get("name", path.name.replace("_", " ").title()),
            path=path.relative_to(self.tests_root),
            description=yaml_data.get("description"),
            parent=parent,
            setup=setup,
            teardown=teardown,
            execution_order=execution_order,
            run_after=yaml_data.get("run_after"),  # Deprecated; used only when execution_order is not set
        )
        
        # Build test metadata lookup from YAML
        yaml_tests = {t["id"]: t for t in yaml_data.get("tests", [])}
        # Keep track of test order from YAML
        yaml_test_order = [t["id"] for t in yaml_data.get("tests", [])]
        
        # First, scan subdirectories to find all tests and subcategories
        discovered_tests = []
        discovered_subcategories = []
        
        for item in sorted(path.iterdir()):
            if not item.is_dir() or item.name.startswith("."):
                continue
            
            # Skip special folders
            if item.name in (self.SETUP_FOLDER, self.TEARDOWN_FOLDER, self.FUNCTIONS_FOLDER):
                continue
            
            # Check if it's a test folder (has steps.md)
            if (item / self.STEPS_FILE).exists():
                test = self._create_test(item, yaml_tests.get(item.name, {}), category)
                discovered_tests.append(test)
            
            # Check if it's a subcategory (has _category.yaml or contains test folders)
            elif self._is_category(item):
                subcategory = self._scan_category(item, parent=category)
                if subcategory:
                    discovered_subcategories.append(subcategory)
        
        # Order tests based on YAML order, then append any tests not in YAML
        ordered_tests = []
        test_by_id = {t.id: t for t in discovered_tests}
        
        # First add tests in YAML-specified order
        for test_id in yaml_test_order:
            if test_id in test_by_id:
                ordered_tests.append(test_by_id[test_id])
        
        # Then add any discovered tests not in YAML (alphabetical order)
        for test in discovered_tests:
            if test not in ordered_tests:
                ordered_tests.append(test)
        
        category.tests = ordered_tests
        category.subcategories = discovered_subcategories
        
        # Only return category if it has tests or subcategories
        if category.tests or category.subcategories:
            return category
        
        return None
    
    def _discover_setup_teardown(self, category_path: Path, folder_name: str) -> Optional[SetupTeardown]:
        """
        Auto-discover setup or teardown folder.
        
        Args:
            category_path: Path to the category folder
            folder_name: Either "_setup" or "_teardown"
            
        Returns:
            SetupTeardown object if valid folder exists, None otherwise
        """
        folder_path = category_path / folder_name
        
        if not folder_path.exists() or not folder_path.is_dir():
            return None
        
        # Check if it has steps.md (minimum requirement)
        if not (folder_path / self.STEPS_FILE).exists():
            return None
        
        return SetupTeardown(path=folder_path)
    
    def _is_category(self, path: Path) -> bool:
        """Check if a directory is a category (has _category.yaml or test folders)."""
        if (path / self.CATEGORY_FILE).exists():
            return True
        
        # Check if any subdirectory has steps.md
        for item in path.iterdir():
            if item.is_dir() and (item / self.STEPS_FILE).exists():
                return True
        
        return False
    
    def _load_category_yaml(self, path: Path) -> dict:
        """Load and parse _category.yaml file."""
        if not path.exists():
            return {}
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data if data else {}
        except Exception as e:
            print(f"Warning: Failed to parse {path}: {e}")
            return {}
    
    def _create_test(
        self, 
        path: Path, 
        yaml_data: dict, 
        category: Category
    ) -> Test:
        """
        Create a Test object from a folder.
        
        Args:
            path: Path to the test folder
            yaml_data: Metadata from _category.yaml (may be empty)
            category: Parent category
            
        Returns:
            Test object
        """
        test_id = path.name
        
        # Parse status
        status_str = yaml_data.get("status", "pending")
        try:
            status = TestStatus(status_str)
        except ValueError:
            status = TestStatus.PENDING
        
        # Parse priority
        priority_str = yaml_data.get("priority", "medium")
        try:
            priority = TestPriority(priority_str)
        except ValueError:
            priority = TestPriority.MEDIUM
        
        # Parse dates
        created_date = self._parse_date(yaml_data.get("created_date"))
        last_run = self._parse_datetime(yaml_data.get("last_run"))
        blocked_since = self._parse_date(yaml_data.get("blocked_since"))
        
        return Test(
            id=test_id,
            name=yaml_data.get("name", test_id.replace("_", " ").title()),
            path=path,
            status=status,
            priority=priority,
            tags=yaml_data.get("tags", []),
            owner=yaml_data.get("owner"),
            created_date=created_date,
            last_run=last_run,
            estimated_duration=yaml_data.get("estimated_duration"),
            blocked_reason=yaml_data.get("blocked_reason"),
            blocked_since=blocked_since,
            category_path=category.path,
        )
    
    def _parse_date(self, value) -> Optional[datetime]:
        """Parse a date value from YAML."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                pass
        return None
    
    def _parse_datetime(self, value) -> Optional[datetime]:
        """Parse a datetime value from YAML."""
        return self._parse_date(value)
    
    def find_test(self, test_id: str) -> Optional[Test]:
        """
        Find a test by its ID or full ID.
        
        Args:
            test_id: Test ID (e.g., "book_consultation" or "booking.book_consultation")
            
        Returns:
            Test object or None
        """
        categories = self.scan()
        
        for category in categories:
            for test in category.all_tests:
                if test.id == test_id or test.full_id == test_id:
                    return test
        
        return None
    
    def find_category(self, category_path: str) -> Optional[Category]:
        """
        Find a category by its path.
        
        Args:
            category_path: Category path (e.g., "booking" or "booking/appointments")
            
        Returns:
            Category object or None
        """
        categories = self.scan()
        
        def search(cats: list[Category], path: str) -> Optional[Category]:
            for cat in cats:
                if cat.path.as_posix() == path:
                    return cat
                found = search(cat.subcategories, path)
                if found:
                    return found
            return None
        
        return search(categories, category_path)
    
    def get_all_tests(self) -> list[Test]:
        """Get all tests from all categories."""
        tests = []
        for category in self.scan():
            tests.extend(category.all_tests)
        return tests
    
    def get_runnable_tests(self) -> list[Test]:
        """Get all tests that are ready to run."""
        return [t for t in self.get_all_tests() if t.is_runnable]
    
    def get_tests_needing_exploration(self) -> list[Test]:
        """Get all tests that need initial exploration."""
        return [t for t in self.get_all_tests() if t.needs_exploration]


def print_discovery_tree(categories: list[Category], indent: int = 0) -> None:
    """
    Print a tree view of discovered categories and tests.
    
    Args:
        categories: List of categories to print
        indent: Current indentation level
    """
    prefix = "  " * indent
    
    for category in categories:
        print(f"{prefix}[DIR] {category.name}")
        
        # Show setup if exists
        if category.setup:
            print(f"{prefix}  [SETUP] _setup/")
        
        # Show tests
        for test in category.tests:
            status_icon = {
                TestStatus.PENDING: "[PENDING]",
                TestStatus.ACTIVE: "[ACTIVE]",
                TestStatus.DISABLED: "[DISABLED]",
                TestStatus.BLOCKED: "[BLOCKED]",
            }.get(test.status, "[?]")
            
            print(f"{prefix}  {status_icon} {test.name} [{test.priority}]")
        
        # Show teardown if exists
        if category.teardown:
            print(f"{prefix}  [TEARDOWN] _teardown/")
        
        # Recurse into subcategories
        if category.subcategories:
            print_discovery_tree(category.subcategories, indent + 1)
