"""Data models for categories and tests."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from .enums import TestStatus, TestPriority


@dataclass
class TestPhaseFiles:
    """Paths to the three phase files for a test."""
    
    steps_md: Path          # Phase 1: Human-readable steps
    script_md: Path         # Phase 2: Detailed script
    test_py: Path           # Phase 3: Executable code
    changelog_md: Path      # Change history
    
    @property
    def has_steps(self) -> bool:
        """Check if steps.md exists."""
        return self.steps_md.exists()
    
    @property
    def has_script(self) -> bool:
        """Check if script.md exists."""
        return self.script_md.exists()
    
    @property
    def has_test(self) -> bool:
        """Check if test.py exists and has content."""
        if not self.test_py.exists():
            return False
        content = self.test_py.read_text(encoding='utf-8').strip()
        # Check if it's more than just a placeholder
        return len(content) > 100 and "def test_" in content


@dataclass
class Test:
    """Represents a single test case."""
    
    # Required fields
    id: str                              # Unique identifier (folder name)
    name: str                            # Human-readable name
    path: Path                           # Path to test folder
    
    # Status and priority
    status: TestStatus = TestStatus.PENDING
    priority: TestPriority = TestPriority.MEDIUM
    
    # Extended metadata
    tags: list[str] = field(default_factory=list)
    owner: Optional[str] = None
    created_date: Optional[datetime] = None
    last_run: Optional[datetime] = None
    estimated_duration: Optional[int] = None  # seconds
    
    # Blocking info (when status is BLOCKED)
    blocked_reason: Optional[str] = None
    blocked_since: Optional[datetime] = None
    
    # Phase files (populated during discovery)
    files: Optional[TestPhaseFiles] = None
    
    # Parent category reference
    category_path: Optional[Path] = None
    
    def __post_init__(self):
        """Initialize phase files if path is set."""
        if self.path and self.files is None:
            self.files = TestPhaseFiles(
                steps_md=self.path / "steps.md",
                script_md=self.path / "script.md",
                test_py=self.path / "test.py",
                changelog_md=self.path / "changelog.md",
            )
    
    @property
    def full_id(self) -> str:
        """Return full test ID including category path."""
        if self.category_path:
            # Convert path to dotted notation: booking/appointments -> booking.appointments
            rel_path = self.category_path.as_posix().replace("/", ".")
            return f"{rel_path}.{self.id}"
        return self.id
    
    @property
    def is_runnable(self) -> bool:
        """Check if test can be run (has code and is active)."""
        return (
            self.status == TestStatus.ACTIVE
            and self.files is not None
            and self.files.has_test
        )
    
    @property
    def needs_exploration(self) -> bool:
        """Check if test needs initial exploration."""
        return (
            self.files is not None
            and self.files.has_steps
            and not self.files.has_script
        )


@dataclass
class SetupTeardown:
    """Represents a setup or teardown for a category."""
    
    path: Path                           # Path to _setup or _teardown folder
    files: Optional[TestPhaseFiles] = None
    
    def __post_init__(self):
        """Initialize phase files if path is set."""
        if self.path and self.files is None:
            self.files = TestPhaseFiles(
                steps_md=self.path / "steps.md",
                script_md=self.path / "script.md",
                test_py=self.path / "test.py",
                changelog_md=self.path / "changelog.md",
            )
    
    @property
    def is_valid(self) -> bool:
        """Check if setup/teardown has required files."""
        return self.files is not None and self.files.has_steps


@dataclass
class Category:
    """Represents a test category (folder with tests)."""
    
    # Required fields
    name: str                            # Category name
    path: Path                           # Path to category folder
    
    # Optional metadata
    description: Optional[str] = None
    
    # Contents
    tests: list[Test] = field(default_factory=list)
    subcategories: list["Category"] = field(default_factory=list)
    
    # Setup and teardown (auto-discovered)
    setup: Optional[SetupTeardown] = None
    teardown: Optional[SetupTeardown] = None
    
    # Parent reference for nested categories
    parent: Optional["Category"] = None
    
    # Execution order: list of test ids and subcategory folder names (path.name) in run order.
    # Defined in parent _category.yaml as execution_order: [id1, id2, ...].
    # When set, runner and GUI use this order; otherwise fallback to legacy run_after / discovery order.
    execution_order: Optional[list[str]] = None
    
    # Deprecated: subcategory-only ordering. Use execution_order in parent instead.
    run_after: Optional[str] = None
    
    @property
    def full_path(self) -> str:
        """Return full category path as string."""
        return self.path.as_posix()
    
    @property
    def all_tests(self) -> list[Test]:
        """Return all tests including from subcategories."""
        tests = list(self.tests)
        for subcat in self.subcategories:
            tests.extend(subcat.all_tests)
        return tests
    
    @property
    def active_tests(self) -> list[Test]:
        """Return only active tests."""
        return [t for t in self.all_tests if t.status == TestStatus.ACTIVE]
    
    @property
    def runnable_tests(self) -> list[Test]:
        """Return tests that are ready to run."""
        return [t for t in self.all_tests if t.is_runnable]
    
    def get_tests_by_priority(self) -> list[Test]:
        """Return all tests sorted by priority."""
        return sorted(self.all_tests, key=lambda t: t.priority.sort_order)
    
    def get_tests_by_tag(self, tag: str) -> list[Test]:
        """Return tests that have a specific tag."""
        return [t for t in self.all_tests if tag in t.tags]
