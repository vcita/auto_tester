"""Data models for reusable functions."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class FunctionParameter:
    """A parameter that a function accepts."""
    
    name: str
    type: str = "string"  # string, number, boolean
    required: bool = True
    description: Optional[str] = None


@dataclass
class FunctionReturn:
    """A value that a function returns (saves to context)."""
    
    name: str
    description: Optional[str] = None


@dataclass
class FunctionPhaseFiles:
    """Paths to the three phase files for a function."""
    
    steps_md: Path
    script_md: Path
    test_py: Path
    changelog_md: Path
    
    def validate(self) -> list[str]:
        """
        Validate that all required files exist.
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        if not self.steps_md.exists():
            errors.append(f"Missing steps.md: {self.steps_md}")
        
        if not self.script_md.exists():
            errors.append(f"Missing script.md: {self.script_md}")
        
        if not self.test_py.exists():
            errors.append(f"Missing test.py: {self.test_py}")
        
        if not self.changelog_md.exists():
            errors.append(f"Missing changelog.md: {self.changelog_md}")
        
        return errors
    
    @property
    def is_valid(self) -> bool:
        """Check if all required files exist."""
        return len(self.validate()) == 0


@dataclass
class Function:
    """Represents a reusable function."""
    
    # Required fields
    id: str                                    # Folder name / unique identifier
    name: str                                  # Human-readable name
    path: Path                                 # Path to function folder
    
    # Optional metadata
    description: Optional[str] = None
    
    # Parameters and returns
    parameters: list[FunctionParameter] = field(default_factory=list)
    returns: list[FunctionReturn] = field(default_factory=list)
    
    # Phase files
    files: Optional[FunctionPhaseFiles] = None
    
    # Validation state
    is_valid: bool = False
    validation_errors: list[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize phase files if path is set."""
        if self.path and self.files is None:
            self.files = FunctionPhaseFiles(
                steps_md=self.path / "steps.md",
                script_md=self.path / "script.md",
                test_py=self.path / "test.py",
                changelog_md=self.path / "changelog.md",
            )
    
    def validate(self) -> bool:
        """
        Validate the function has all required files.
        
        Returns:
            True if valid, False otherwise
        """
        self.validation_errors = []
        
        if self.files:
            self.validation_errors = self.files.validate()
        else:
            self.validation_errors.append("No files configured")
        
        self.is_valid = len(self.validation_errors) == 0
        return self.is_valid
    
    def get_required_parameters(self) -> list[FunctionParameter]:
        """Get list of required parameters."""
        return [p for p in self.parameters if p.required]
    
    def get_optional_parameters(self) -> list[FunctionParameter]:
        """Get list of optional parameters."""
        return [p for p in self.parameters if not p.required]
    
    def has_parameter(self, name: str) -> bool:
        """Check if function has a parameter with given name."""
        return any(p.name == name for p in self.parameters)
    
    def get_parameter(self, name: str) -> Optional[FunctionParameter]:
        """Get a parameter by name."""
        for p in self.parameters:
            if p.name == name:
                return p
        return None
