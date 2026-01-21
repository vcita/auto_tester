"""Enumerations for test statuses and priorities."""

from enum import Enum


class TestStatus(str, Enum):
    """Status of a test in the system."""
    
    PENDING = "pending"      # Not yet explored/generated
    ACTIVE = "active"        # Ready to run
    DISABLED = "disabled"    # Temporarily turned off
    BLOCKED = "blocked"      # Waiting for bug fix
    
    def __str__(self) -> str:
        return self.value


class TestPriority(str, Enum):
    """Priority level for test execution order."""
    
    CRITICAL = "critical"    # Run first, always
    HIGH = "high"            # Run early
    MEDIUM = "medium"        # Default priority
    LOW = "low"              # Run last
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def sort_order(self) -> int:
        """Return numeric order for sorting (lower = higher priority)."""
        order = {
            TestPriority.CRITICAL: 0,
            TestPriority.HIGH: 1,
            TestPriority.MEDIUM: 2,
            TestPriority.LOW: 3,
        }
        return order[self]
