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
            "",
            "---",
            "",
            "## Error",
            "",
            "```",
            result.error or "Unknown error",
            "```",
            "",
            f"**Error Type**: `{result.error_type}`",
            "",
        ]
        
        # Screenshot section
        if result.screenshot:
            lines.extend([
                "## Screenshot (REQUIRED - Analyze this first!)",
                "",
                f"![Error Screenshot]({result.screenshot})",
                "",
            ])
        
        # Video section - check for recent video in snapshots/videos
        videos_dir = Path("snapshots/videos")
        if videos_dir.exists():
            video_files = sorted(videos_dir.glob("*.webm"), key=lambda p: p.stat().st_mtime, reverse=True)
            if video_files:
                latest_video = video_files[0]
                lines.extend([
                    "## Video Recording",
                    "",
                    f"Full test run video: `{latest_video}`",
                    "",
                    "**Watch this video to see the EXACT sequence of actions and identify where things went wrong.**",
                    "",
                ])
        
        # Context section
        if context:
            # Filter out internal metadata
            user_context = {k: v for k, v in context.items() if not k.startswith("_")}
            if user_context:
                lines.extend([
                    "## Context at Failure",
                    "",
                    "```json",
                    json.dumps(user_context, indent=2, default=str),
                    "```",
                    "",
                ])
        
        # Test files section
        test_path = result.test_path
        lines.extend([
            "## Test Files",
            "",
            f"- **Location**: `{test_path}`",
            "",
        ])
        
        # Include steps.md content
        steps_file = test_path / "steps.md"
        if steps_file.exists():
            lines.extend([
                "### steps.md",
                "",
                "```markdown",
                steps_file.read_text(encoding="utf-8"),
                "```",
                "",
            ])
        
        # Include script.md content
        script_file = test_path / "script.md"
        if script_file.exists():
            lines.extend([
                "### script.md",
                "",
                "```markdown",
                script_file.read_text(encoding="utf-8"),
                "```",
                "",
            ])
        
        # Include test.py content
        test_file = test_path / "test.py"
        if test_file.exists():
            lines.extend([
                "### test.py",
                "",
                "```python",
                test_file.read_text(encoding="utf-8"),
                "```",
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
        
        # Instructions
        lines.extend([
            "---",
            "",
            "## Instructions for Fixing",
            "",
            "1. **Analyze the error** - What specifically failed?",
            "2. **Check the screenshot** - What is the current UI state?",
            "3. **Review context** - Is the test missing required data?",
            "4. **Re-explore if needed** - Use Playwright MCP to verify locators",
            "5. **Update files** - Fix test.py, update script.md if flow changed",
            "6. **Log changes** - Update changelog.md with the fix",
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
