"""
Result models for the test runner.

These dataclasses represent the results of test execution at various levels:
- TestResult: Individual test/setup/teardown result
- CategoryResult: All results within a category
- RunResult: Complete run across all categories
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Literal, Optional


@dataclass
class TestResult:
    """Result of a single test, setup, or teardown execution."""
    
    test_name: str
    test_path: Path
    test_type: Literal["test", "setup", "teardown"]
    status: Literal["passed", "failed", "skipped"]
    duration_ms: int
    error: Optional[str] = None
    error_type: Optional[str] = None
    screenshot: Optional[Path] = None
    context_snapshot: Optional[dict] = None  # Context state at time of result
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization/events."""
        return {
            "test_name": self.test_name,
            "test_path": str(self.test_path),
            "test_type": self.test_type,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "error": self.error,
            "error_type": self.error_type,
            "screenshot": str(self.screenshot) if self.screenshot else None,
        }


@dataclass
class CategoryResult:
    """Result of running all tests in a category."""
    
    category_name: str
    category_path: Path
    setup_result: Optional[TestResult] = None
    test_results: List[TestResult] = field(default_factory=list)
    teardown_result: Optional[TestResult] = None
    stopped_early: bool = False  # True if stopped due to failure
    
    @property
    def passed(self) -> int:
        """Count of passed tests (excluding setup/teardown)."""
        return sum(1 for r in self.test_results if r.status == "passed")
    
    @property
    def failed(self) -> int:
        """Count of failed tests (excluding setup/teardown)."""
        return sum(1 for r in self.test_results if r.status == "failed")
    
    @property
    def skipped(self) -> int:
        """Count of skipped tests (excluding setup/teardown)."""
        return sum(1 for r in self.test_results if r.status == "skipped")
    
    @property
    def total(self) -> int:
        """Total number of tests (excluding setup/teardown)."""
        return len(self.test_results)
    
    @property
    def status(self) -> Literal["passed", "failed", "partial", "skipped"]:
        """Overall category status."""
        if not self.test_results:
            return "skipped"
        if self.setup_result and self.setup_result.status == "failed":
            return "failed"
        if self.failed > 0:
            return "failed" if self.passed == 0 else "partial"
        return "passed"
    
    @property
    def duration_ms(self) -> int:
        """Total duration of all tests in category."""
        total = 0
        if self.setup_result:
            total += self.setup_result.duration_ms
        for r in self.test_results:
            total += r.duration_ms
        if self.teardown_result:
            total += self.teardown_result.duration_ms
        return total
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization/events."""
        return {
            "category_name": self.category_name,
            "category_path": str(self.category_path),
            "status": self.status,
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "total": self.total,
            "duration_ms": self.duration_ms,
            "stopped_early": self.stopped_early,
            "setup_result": self.setup_result.to_dict() if self.setup_result else None,
            "test_results": [r.to_dict() for r in self.test_results],
            "teardown_result": self.teardown_result.to_dict() if self.teardown_result else None,
        }


@dataclass
class RunResult:
    """Result of a complete test run across categories."""
    
    started_at: datetime
    completed_at: Optional[datetime] = None
    category_results: List[CategoryResult] = field(default_factory=list)
    
    @property
    def total_passed(self) -> int:
        """Total passed tests across all categories."""
        return sum(c.passed for c in self.category_results)
    
    @property
    def total_failed(self) -> int:
        """Total failed tests across all categories."""
        return sum(c.failed for c in self.category_results)
    
    @property
    def total_skipped(self) -> int:
        """Total skipped tests across all categories."""
        return sum(c.skipped for c in self.category_results)
    
    @property
    def total_tests(self) -> int:
        """Total number of tests across all categories."""
        return sum(c.total for c in self.category_results)
    
    @property
    def duration_ms(self) -> int:
        """Total duration of the run."""
        if not self.completed_at:
            return 0
        delta = self.completed_at - self.started_at
        return int(delta.total_seconds() * 1000)
    
    @property
    def status(self) -> Literal["passed", "failed", "partial"]:
        """Overall run status."""
        if not self.category_results:
            return "passed"
        if self.total_failed > 0:
            return "failed" if self.total_passed == 0 else "partial"
        return "passed"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization/events."""
        return {
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status,
            "total_passed": self.total_passed,
            "total_failed": self.total_failed,
            "total_skipped": self.total_skipped,
            "total_tests": self.total_tests,
            "duration_ms": self.duration_ms,
            "category_results": [c.to_dict() for c in self.category_results],
        }
