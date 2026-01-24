"""
Heal request generator for the test runner.

When a test fails, generates a markdown file with all the context
needed for Cursor to fix the test.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json

from .models import TestResult


class HealRequestGenerator:
    """
    Generates heal request files when tests fail.
    
    A heal request contains:
    - Error details and stack trace
    - Screenshot of the failure
    - Current context state
    - Relevant test files (steps.md, script.md, test.py)
    
    These files are placed in .cursor/heal_requests/ for manual
    processing by Cursor.
    """
    
    def __init__(self, heal_requests_dir: Optional[Path] = None):
        """
        Initialize the generator.
        
        Args:
            heal_requests_dir: Directory to save heal requests.
                              Defaults to .cursor/heal_requests/
        """
        self.heal_requests_dir = heal_requests_dir or Path(".cursor/heal_requests")
    
    def generate(
        self,
        result: TestResult,
        category_name: str,
        context: Dict[str, Any],
        additional_info: Optional[str] = None,
    ) -> Path:
        """
        Generate a heal request file for a failed test.
        
        Args:
            result: The failed test result
            category_name: Name of the category
            context: Current context state
            additional_info: Any additional information to include
            
        Returns:
            Path to the generated heal request file
        """
        self.heal_requests_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{result.test_name}_{timestamp}.md"
        file_path = self.heal_requests_dir / filename
        
        content = self._build_content(result, category_name, context, additional_info)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return file_path
    
    def _build_content(
        self,
        result: TestResult,
        category_name: str,
        context: Dict[str, Any],
        additional_info: Optional[str],
    ) -> str:
        """Build the markdown content for the heal request."""
        
        lines = [
            f"# Heal Request: {category_name}/{result.test_name}",
            "",
            f"> **Generated**: {datetime.now().isoformat()}",
            f"> **Test Type**: {result.test_type}",
            f"> **Duration**: {result.duration_ms}ms",
            f"**Status**: `open`",
            "",
            "---",
            "",
            "## What Failed",
            "",
        ]
        
        # Error explanation
        if result.error:
            lines.extend([
                "```",
                result.error or "Unknown error",
                "```",
                "",
            ])
        
        lines.append(f"**Error Type**: `{result.error_type}`")
        lines.append("")
        
        # Test location (so they know where to find the files)
        test_path = result.test_path
        lines.extend([
            "## Test Location",
            "",
            f"Test files are located at: `{test_path}`",
            "",
            "- `steps.md` - Test steps and requirements",
            "- `script.md` - Test script and flow",
            "- `test.py` - Test implementation code",
            "- `changelog.md` - History of previous fixes",
            "",
        ])
        
        # Screenshot reference
        if result.screenshot:
            lines.extend([
                "## Screenshot",
                "",
                f"Screenshot saved at: `{result.screenshot}`",
                "",
                "**Analyze the screenshot to understand the UI state at failure.**",
                "",
            ])
        
        # Brief context summary (just keys, not full values)
        if context:
            # Filter out internal metadata
            user_context = {k: v for k, v in context.items() if not k.startswith("_")}
            if user_context:
                lines.extend([
                    "## Context Summary",
                    "",
                    f"Context had {len(user_context)} keys: {', '.join(sorted(user_context.keys()))}",
                    "",
                    "Full context is available in the test run artifacts.",
                    "",
                ])
        
        # Additional info
        if additional_info:
            lines.extend([
                "## Additional Information",
                "",
                additional_info,
                "",
            ])
        
        # Brief instructions
        lines.extend([
            "---",
            "",
            "## Next Steps",
            "",
            "1. Review the error message above",
            "2. Check the screenshot to see the UI state",
            "3. Read the test files at the location above",
            "4. Review changelog.md for previous fixes",
            "5. Use Playwright MCP to debug if needed",
            "",
            "See `.cursor/rules/heal.mdc` for detailed healing process.",
        ])
        
        return "\n".join(lines)
    
    def list_pending_requests(self) -> list:
        """
        List all pending heal requests.
        
        Returns:
            List of heal request file paths
        """
        if not self.heal_requests_dir.exists():
            return []
        
        return sorted(self.heal_requests_dir.glob("*.md"))
    
    def mark_resolved(self, request_path: Path) -> None:
        """
        Mark a heal request as resolved by moving it to a resolved folder.
        
        Args:
            request_path: Path to the heal request file
        """
        resolved_dir = self.heal_requests_dir / "resolved"
        resolved_dir.mkdir(exist_ok=True)
        
        if request_path.exists():
            new_path = resolved_dir / request_path.name
            request_path.rename(new_path)
