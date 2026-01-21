"""
CLI reporter for the test runner.

Subscribes to runner events and prints pretty output to the terminal
using the Rich library.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.tree import Tree

from .events import EventEmitter, RunnerEvent
from .models import RunResult, CategoryResult, TestResult


class CLIReporter:
    """
    CLI event consumer that prints pretty output.
    
    Subscribes to runner events and displays real-time progress
    in the terminal.
    
    Usage:
        runner = TestRunner(tests_root)
        reporter = CLIReporter(runner.events)
        result = runner.run_all()
        reporter.print_summary(result)
    """
    
    def __init__(self, events: EventEmitter):
        """
        Initialize the CLI reporter.
        
        Args:
            events: EventEmitter to subscribe to
        """
        self.console = Console()
        self.events = events
        self._current_category = None
        self._test_count = 0
        self._passed_count = 0
        self._failed_count = 0
        
        # Subscribe to events
        events.on(RunnerEvent.RUN_STARTED, self._on_run_started)
        events.on(RunnerEvent.RUN_COMPLETED, self._on_run_completed)
        events.on(RunnerEvent.CATEGORY_STARTED, self._on_category_started)
        events.on(RunnerEvent.CATEGORY_COMPLETED, self._on_category_completed)
        events.on(RunnerEvent.BROWSER_STARTING, self._on_browser_starting)
        events.on(RunnerEvent.BROWSER_STARTED, self._on_browser_started)
        events.on(RunnerEvent.BROWSER_CLOSING, self._on_browser_closing)
        events.on(RunnerEvent.TEST_STARTED, self._on_test_started)
        events.on(RunnerEvent.TEST_PROGRESS, self._on_test_progress)
        events.on(RunnerEvent.TEST_COMPLETED, self._on_test_completed)
        events.on(RunnerEvent.TEST_FAILED, self._on_test_failed)
        events.on(RunnerEvent.HEAL_REQUEST_CREATED, self._on_heal_request_created)
    
    def _on_run_started(self, data: dict) -> None:
        """Handle run started event."""
        self.console.print()
        self.console.print(Panel(
            f"[bold]vcita Test Runner[/bold]\n"
            f"Categories: {data['total_categories']} | Tests: {data['total_tests']}",
            border_style="blue",
        ))
        self.console.print()
        
        # Reset counters
        self._test_count = 0
        self._passed_count = 0
        self._failed_count = 0
    
    def _on_run_completed(self, data: dict) -> None:
        """Handle run completed event."""
        # Summary is printed by print_summary()
        pass
    
    def _on_category_started(self, data: dict) -> None:
        """Handle category started event."""
        self._current_category = data['category']
        
        category_info = f"[bold cyan]Category: {data['category']}[/bold cyan]"
        if data.get('has_setup'):
            category_info += " [dim](has setup)[/dim]"
        
        self.console.print(f"\n[bold]{'>'*3}[/bold] {category_info}")
    
    def _on_category_completed(self, data: dict) -> None:
        """Handle category completed event."""
        result = data['result']
        status = result.get('status', 'unknown')
        
        if status == 'passed':
            self.console.print(f"    [green]Category completed: {result['passed']} passed[/green]")
        elif status == 'failed':
            self.console.print(f"    [red]Category stopped: {result['failed']} failed, {result.get('skipped', 0)} skipped[/red]")
        elif status == 'partial':
            self.console.print(f"    [yellow]Category partial: {result['passed']} passed, {result['failed']} failed[/yellow]")
    
    def _on_browser_starting(self, data: dict) -> None:
        """Handle browser starting event."""
        self.console.print(f"    [dim]Browser launching...[/dim]")
    
    def _on_browser_started(self, data: dict) -> None:
        """Handle browser started event."""
        self.console.print(f"    [dim]Browser ready[/dim]")
    
    def _on_browser_closing(self, data: dict) -> None:
        """Handle browser closing event."""
        self.console.print(f"    [dim]Browser closing...[/dim]")
    
    def _on_test_started(self, data: dict) -> None:
        """Handle test started event."""
        test_type = data['test_type']
        test_name = data['test']
        
        if test_type == 'setup':
            prefix = "[Setup]"
            style = "cyan"
        elif test_type == 'teardown':
            prefix = "[Teardown]"
            style = "cyan"
        else:
            index = data.get('index', 0)
            total = data.get('total', 0)
            prefix = f"[Test {index}/{total}]"
            style = "white"
        
        self.console.print(f"    [{style}]{prefix}[/{style}] {test_name}")
    
    def _on_test_progress(self, data: dict) -> None:
        """Handle test progress event."""
        message = data.get('message', '')
        self.console.print(f"        [dim]{message}[/dim]")
    
    def _on_test_completed(self, data: dict) -> None:
        """Handle test completed event."""
        result = data['result']
        status = result['status']
        duration_ms = result['duration_ms']
        duration_str = f"{duration_ms/1000:.1f}s" if duration_ms >= 1000 else f"{duration_ms}ms"
        
        if status == 'passed':
            self.console.print(f"        [green]{'>'} Passed[/green] ({duration_str})")
            self._passed_count += 1
        elif status == 'failed':
            self.console.print(f"        [red]{'X'} Failed[/red] ({duration_str})")
            self._failed_count += 1
        elif status == 'skipped':
            self.console.print(f"        [yellow]{'~'} Skipped[/yellow]")
        
        self._test_count += 1
    
    def _on_test_failed(self, data: dict) -> None:
        """Handle test failed event."""
        error = data.get('error', 'Unknown error')
        error_type = data.get('error_type', 'Error')
        
        # Truncate long errors
        if len(error) > 200:
            error = error[:200] + "..."
        
        self.console.print(f"        [red]Error: {error_type}[/red]")
        self.console.print(f"        [dim]{error}[/dim]")
    
    def _on_heal_request_created(self, data: dict) -> None:
        """Handle heal request created event."""
        path = data.get('path', '')
        self.console.print(f"        [yellow]Heal request: {path}[/yellow]")
    
    def print_summary(self, result: RunResult) -> None:
        """
        Print final summary of the run.
        
        Args:
            result: RunResult from the test run
        """
        self.console.print()
        
        # Build summary table
        table = Table(title="Test Results Summary", border_style="blue")
        table.add_column("Category", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Passed", justify="right", style="green")
        table.add_column("Failed", justify="right", style="red")
        table.add_column("Skipped", justify="right", style="yellow")
        table.add_column("Duration", justify="right")
        
        for cat_result in result.category_results:
            status_style = {
                "passed": "[green]PASSED[/green]",
                "failed": "[red]FAILED[/red]",
                "partial": "[yellow]PARTIAL[/yellow]",
                "skipped": "[dim]SKIPPED[/dim]",
            }.get(cat_result.status, cat_result.status)
            
            duration_str = f"{cat_result.duration_ms/1000:.1f}s"
            
            table.add_row(
                cat_result.category_name,
                status_style,
                str(cat_result.passed),
                str(cat_result.failed),
                str(cat_result.skipped),
                duration_str,
            )
        
        self.console.print(table)
        
        # Overall summary
        total_duration = f"{result.duration_ms/1000:.1f}s" if result.duration_ms else "0s"
        
        if result.total_failed == 0:
            summary_style = "green"
            summary_text = f"All tests passed! ({result.total_passed} tests)"
        elif result.total_passed == 0:
            summary_style = "red"
            summary_text = f"All tests failed! ({result.total_failed} tests)"
        else:
            summary_style = "yellow"
            summary_text = f"Partial: {result.total_passed} passed, {result.total_failed} failed"
        
        self.console.print()
        self.console.print(Panel(
            f"[{summary_style}]{summary_text}[/{summary_style}]\n"
            f"Duration: {total_duration}",
            border_style=summary_style,
        ))
