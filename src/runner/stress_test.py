"""
Stress Test Runner

Runs categories multiple times to check for consistency and flakiness.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn

from .runner import TestRunner
from .models import CategoryResult


@dataclass
class StressTestRun:
    """Result of a single stress test run."""
    iteration: int
    category_name: str
    result: CategoryResult
    passed: bool
    error: Optional[str] = None
    error_type: Optional[str] = None


@dataclass
class StressTestResult:
    """Result of stress testing a category."""
    category_name: str
    total_iterations: int
    runs: List[StressTestRun] = field(default_factory=list)
    
    @property
    def passed_count(self) -> int:
        """Number of successful runs."""
        return sum(1 for run in self.runs if run.passed)
    
    @property
    def failed_count(self) -> int:
        """Number of failed runs."""
        return len(self.runs) - self.passed_count
    
    @property
    def pass_rate(self) -> float:
        """Pass rate as a percentage."""
        if not self.runs:
            return 0.0
        return (self.passed_count / len(self.runs)) * 100
    
    @property
    def failure_reasons(self) -> Dict[str, int]:
        """Count of failures by error type/reason."""
        reasons = {}
        for run in self.runs:
            if not run.passed:
                error_key = run.error_type or "Unknown"
                if run.error:
                    # Use first line of error as key
                    error_first_line = run.error.split('\n')[0].strip()
                    if len(error_first_line) > 100:
                        error_first_line = error_first_line[:100] + "..."
                    error_key = f"{error_key}: {error_first_line}"
                reasons[error_key] = reasons.get(error_key, 0) + 1
        return reasons


class StressTestRunner:
    """
    Runs categories multiple times to check for consistency.
    
    Usage:
        runner = StressTestRunner(tests_root, headless=True)
        result = runner.run_stress_test(["clients", "scheduling"], iterations=10)
        runner.print_report(result)
    """
    
    def __init__(
        self,
        tests_root: Path,
        headless: bool = False,
        keep_open: bool = False,
    ):
        """
        Initialize the stress test runner.
        
        Args:
            tests_root: Path to the tests/ directory
            headless: Whether to run browser in headless mode
            keep_open: Whether to keep browser open on failure
        """
        self.tests_root = tests_root
        self.headless = headless
        self.keep_open = keep_open
        self.console = Console()
    
    def run_stress_test(
        self,
        category_names: List[str],
        iterations: int,
    ) -> List[StressTestResult]:
        """
        Run stress test on specified categories.
        
        Args:
            category_names: List of category names to test
            iterations: Number of times to run each category
            
        Returns:
            List of StressTestResult objects, one per category
        """
        results = []
        
        # Create progress bar
        total_work = len(category_names) * iterations
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=self.console,
        ) as progress:
            
            for category_name in category_names:
                task = progress.add_task(
                    f"Stress testing [cyan]{category_name}[/cyan]",
                    total=iterations
                )
                
                category_result = StressTestResult(
                    category_name=category_name,
                    total_iterations=iterations,
                )
                
                for iteration in range(1, iterations + 1):
                    # Update progress
                    progress.update(
                        task,
                        description=f"Stress testing [cyan]{category_name}[/cyan] (run {iteration}/{iterations})"
                    )
                    
                    # Run the category
                    try:
                        runner = TestRunner(
                            self.tests_root,
                            headless=self.headless,
                            keep_open=self.keep_open,
                        )
                        
                        result = runner.run_category(category_name)
                        
                        # Determine if passed
                        passed = result.status == "passed"
                        error = None
                        error_type = None
                        
                        if not passed:
                            # Find first failed test
                            failed_test = next(
                                (t for t in result.test_results if t.status == "failed"),
                                None
                            )
                            if failed_test:
                                error = failed_test.error
                                error_type = failed_test.error_type
                            elif result.setup_result and result.setup_result.status == "failed":
                                error = result.setup_result.error
                                error_type = result.setup_result.error_type
                        
                        run = StressTestRun(
                            iteration=iteration,
                            category_name=category_name,
                            result=result,
                            passed=passed,
                            error=error,
                            error_type=error_type,
                        )
                        
                        category_result.runs.append(run)
                        
                    except Exception as e:
                        # Handle unexpected errors
                        run = StressTestRun(
                            iteration=iteration,
                            category_name=category_name,
                            result=None,
                            passed=False,
                            error=str(e),
                            error_type="Exception",
                        )
                        category_result.runs.append(run)
                    
                    progress.advance(task)
                
                results.append(category_result)
        
        return results
    
    def print_report(self, results: List[StressTestResult]) -> None:
        """
        Print a detailed stress test report.
        
        Args:
            results: List of StressTestResult objects
        """
        self.console.print()
        self.console.print(Panel(
            "[bold]Stress Test Report[/bold]",
            border_style="blue",
        ))
        self.console.print()
        
        # Summary table
        summary_table = Table(title="Summary", border_style="blue")
        summary_table.add_column("Category", style="cyan")
        summary_table.add_column("Iterations", justify="right")
        summary_table.add_column("Passed", justify="right", style="green")
        summary_table.add_column("Failed", justify="right", style="red")
        summary_table.add_column("Pass Rate", justify="right")
        summary_table.add_column("Status", justify="center")
        
        for result in results:
            pass_rate_str = f"{result.pass_rate:.1f}%"
            
            if result.pass_rate == 100.0:
                status = "[green]STABLE[/green]"
            elif result.pass_rate >= 80.0:
                status = "[yellow]FLAKY[/yellow]"
            else:
                status = "[red]UNSTABLE[/red]"
            
            summary_table.add_row(
                result.category_name,
                str(result.total_iterations),
                str(result.passed_count),
                str(result.failed_count),
                pass_rate_str,
                status,
            )
        
        self.console.print(summary_table)
        self.console.print()
        
        # Detailed failure analysis
        for result in results:
            if result.failed_count > 0:
                self.console.print(Panel(
                    f"[bold]Category: {result.category_name}[/bold]\n"
                    f"Failed: {result.failed_count}/{result.total_iterations} runs",
                    border_style="red" if result.pass_rate < 50 else "yellow",
                ))
                
                # Failure reasons table
                if result.failure_reasons:
                    reasons_table = Table(title="Failure Reasons", show_header=True, header_style="bold red")
                    reasons_table.add_column("Error Type", style="red")
                    reasons_table.add_column("Count", justify="right")
                    
                    # Sort by count descending
                    sorted_reasons = sorted(
                        result.failure_reasons.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )
                    
                    for error_key, count in sorted_reasons:
                        reasons_table.add_row(
                            error_key,
                            str(count),
                        )
                    
                    self.console.print(reasons_table)
                    self.console.print()
                
                # Show failed iteration details
                failed_runs = [r for r in result.runs if not r.passed]
                if failed_runs:
                    self.console.print("[bold]Failed Iterations:[/bold]")
                    for run in failed_runs[:10]:  # Show first 10 failures
                        error_display = run.error or "Unknown error"
                        if len(error_display) > 150:
                            error_display = error_display[:150] + "..."
                        self.console.print(
                            f"  [red]Run {run.iteration}:[/red] {error_display}"
                        )
                    if len(failed_runs) > 10:
                        self.console.print(f"  [dim]... and {len(failed_runs) - 10} more failures[/dim]")
                    self.console.print()
        
        # Overall summary
        total_runs = sum(r.total_iterations for r in results)
        total_passed = sum(r.passed_count for r in results)
        total_failed = sum(r.failed_count for r in results)
        overall_pass_rate = (total_passed / total_runs * 100) if total_runs > 0 else 0
        
        if overall_pass_rate == 100.0:
            summary_style = "green"
            summary_text = f"All stress tests passed! ({total_passed}/{total_runs} runs)"
        elif overall_pass_rate >= 80.0:
            summary_style = "yellow"
            summary_text = f"Stress tests show some flakiness: {total_passed}/{total_runs} passed ({overall_pass_rate:.1f}%)"
        else:
            summary_style = "red"
            summary_text = f"Stress tests show instability: {total_passed}/{total_runs} passed ({overall_pass_rate:.1f}%)"
        
        self.console.print()
        self.console.print(Panel(
            f"[{summary_style}]{summary_text}[/{summary_style}]\n"
            f"Total runs: {total_runs} | Passed: {total_passed} | Failed: {total_failed}",
            border_style=summary_style,
        ))
