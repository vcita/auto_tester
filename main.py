#!/usr/bin/env python3
"""
vcita Test Agent - Main Entry Point

An AI-driven browser test agent that:
1. Reads human-readable test scenarios
2. Explores the application to learn the correct behavior
3. Generates and runs Playwright tests
4. Self-heals when tests fail due to UI changes
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rich.console import Console
from rich.table import Table

from src.discovery import TestDiscovery, FunctionDiscovery
from src.discovery.test_discovery import print_discovery_tree
from src.discovery.function_discovery import print_functions_list
from src.models import TestStatus
from src.runner import TestRunner, CLIReporter
from src.gui import run_server

console = Console()


def load_config() -> dict:
    """Load configuration from config.yaml."""
    import yaml
    config_path = Path(__file__).parent / "config.yaml"
    if config_path.exists():
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {}


def cmd_list(args):
    """List all tests or functions."""
    config = load_config()
    tests_root = Path(__file__).parent / config.get("tests", {}).get("root_path", "tests")
    
    # List functions if --functions flag is set
    if args.functions:
        try:
            func_discovery = FunctionDiscovery(tests_root)
            functions = func_discovery.scan()
            print_functions_list(functions)
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
        return
    
    # List tests
    try:
        discovery = TestDiscovery(tests_root)
        categories = discovery.scan()
        
        if not categories:
            console.print("[yellow]No tests found.[/yellow]")
            return
        
        if args.category:
            # Filter to specific category
            category = discovery.find_category(args.category)
            if category:
                categories = [category]
            else:
                console.print(f"[red]Category not found: {args.category}[/red]")
                return
        
        console.print("\n[bold]Test Discovery Results[/bold]\n")
        print_discovery_tree(categories)
        
        # Summary
        all_tests = []
        for cat in categories:
            all_tests.extend(cat.all_tests)
        
        console.print(f"\n[dim]Total: {len(all_tests)} tests[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def cmd_status(args):
    """Show test status summary."""
    config = load_config()
    tests_root = Path(__file__).parent / config.get("tests", {}).get("root_path", "tests")
    
    try:
        discovery = TestDiscovery(tests_root)
        all_tests = discovery.get_all_tests()
        
        if not all_tests:
            console.print("[yellow]No tests found.[/yellow]")
            return
        
        # Count by status
        status_counts = {}
        for status in TestStatus:
            status_counts[status] = len([t for t in all_tests if t.status == status])
        
        # Create summary table
        table = Table(title="Test Status Summary")
        table.add_column("Status", style="bold")
        table.add_column("Count", justify="right")
        table.add_column("Percentage", justify="right")
        
        total = len(all_tests)
        for status, count in status_counts.items():
            pct = (count / total * 100) if total > 0 else 0
            style = {
                TestStatus.ACTIVE: "green",
                TestStatus.PENDING: "yellow",
                TestStatus.DISABLED: "dim",
                TestStatus.BLOCKED: "red",
            }.get(status, "white")
            table.add_row(str(status), str(count), f"{pct:.1f}%", style=style)
        
        table.add_row("", "", "", style="dim")
        table.add_row("[bold]Total[/bold]", f"[bold]{total}[/bold]", "100%")
        
        console.print(table)
        
        # Show runnable vs needs exploration
        runnable = len(discovery.get_runnable_tests())
        needs_explore = len(discovery.get_tests_needing_exploration())
        
        console.print(f"\n[green]Runnable:[/green] {runnable} tests ready to execute")
        console.print(f"[yellow]Needs exploration:[/yellow] {needs_explore} tests need initial setup")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def cmd_run(args):
    """Run tests."""
    config = load_config()
    tests_root = Path(__file__).parent / config.get("tests", {}).get("root_path", "tests")
    
    # Check for headless mode and keep-open flag
    headless = args.headless if hasattr(args, 'headless') else False
    keep_open = getattr(args, 'keep_open', False)
    
    try:
        # Create runner
        runner = TestRunner(tests_root, headless=headless, keep_open=keep_open)
        
        # Attach CLI reporter for real-time output
        reporter = CLIReporter(runner.events)
        
        # Run tests
        if args.category:
            # Run specific category
            result = runner.run_category(args.category)
        else:
            # Run all categories
            result = runner.run_all()
        
        # Print final summary
        from src.runner.models import RunResult
        if isinstance(result, RunResult):
            reporter.print_summary(result)
        else:
            # Single category result - wrap in RunResult for summary
            from datetime import datetime
            run_result = RunResult(
                started_at=datetime.now(),
                completed_at=datetime.now(),
                category_results=[result],
            )
            reporter.print_summary(run_result)
        
        # Exit with appropriate code
        if result.total_failed > 0 if hasattr(result, 'total_failed') else result.failed > 0:
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]Error running tests: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


def cmd_explore(args):
    """Explore and generate test."""
    console.print(f"[bold blue]Exploring: {args.test_path}[/bold blue]")
    # TODO: Implement exploration
    console.print("[yellow]Exploration not yet implemented[/yellow]")


def cmd_init(args):
    """Initialize a new test."""
    config = load_config()
    tests_root = Path(__file__).parent / config.get("tests", {}).get("root_path", "tests")
    
    category_path = tests_root / args.category
    test_path = category_path / args.test_name
    
    if test_path.exists():
        console.print(f"[red]Test already exists: {test_path}[/red]")
        return
    
    # Create test folder and files
    test_path.mkdir(parents=True, exist_ok=True)
    
    # Create steps.md template
    steps_content = f"""# {args.test_name.replace('_', ' ').title()}

## Objective
[Describe what this test verifies]

## Prerequisites
- [List any prerequisites]

## Steps
1. [First step]
2. [Second step]
3. [Continue...]

## Expected Result
- [What success looks like]

## Test Data
- [Any specific test data needed]
"""
    (test_path / "steps.md").write_text(steps_content)
    
    # Create empty script.md
    script_content = f"""# {args.test_name.replace('_', ' ').title()} - Detailed Script

> **Status**: Pending exploration
> **Last Updated**: Not yet explored

## Initial State
- URL: [starting URL]

## Actions
[Will be generated by exploration]

## Success Verification
[Will be generated by exploration]
"""
    (test_path / "script.md").write_text(script_content)
    
    # Create placeholder test.py
    test_content = """# Auto-generated test file
# Status: Pending generation from script.md
# 
# This file will be automatically generated after exploration.

pass
"""
    (test_path / "test.py").write_text(test_content)
    
    # Create changelog
    from datetime import datetime
    changelog_content = f"""# Changelog: {args.test_name}

All changes to steps.md, script.md, and test.py are logged here.

---

## {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Initial Creation
**Phase**: All files
**Author**: Manual (init command)
**Reason**: New test created
**Changes**:
- Created steps.md template
- Created script.md placeholder
- Created test.py placeholder
"""
    (test_path / "changelog.md").write_text(changelog_content)
    
    console.print(f"[green]Created test: {args.category}/{args.test_name}[/green]")
    console.print(f"  [dim]Edit {test_path / 'steps.md'} to define your test[/dim]")


def cmd_gui(args):
    """Start the web GUI."""
    config = load_config()
    project_root = Path(__file__).parent
    tests_root = project_root / config.get("tests", {}).get("root_path", "tests")
    snapshots_dir = project_root / "snapshots"
    heal_requests_dir = project_root / ".cursor" / "heal_requests"
    
    # Get host and port from args
    host = args.host if hasattr(args, 'host') else "127.0.0.1"
    port = args.port if hasattr(args, 'port') else 8080
    
    run_server(
        tests_root=tests_root,
        snapshots_dir=snapshots_dir,
        heal_requests_dir=heal_requests_dir,
        host=host,
        port=port
    )


def main():
    parser = argparse.ArgumentParser(
        description="vcita Test Agent - AI-driven browser testing"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Run command - execute tests
    run_parser = subparsers.add_parser("run", help="Run tests")
    run_parser.add_argument(
        "--category", "-c",
        help="Run only tests in this category"
    )
    run_parser.add_argument(
        "--test", "-t",
        help="Run only this specific test"
    )
    run_parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode"
    )
    run_parser.add_argument(
        "--keep-open",
        action="store_true",
        help="Keep browser open on failure for debugging"
    )
    
    # Explore command - explore and generate tests
    explore_parser = subparsers.add_parser("explore", help="Explore and generate test from steps.md")
    explore_parser.add_argument(
        "test_path",
        help="Path to test folder (e.g., tests/booking/book_consultation)"
    )
    
    # List command - list all tests or functions
    list_parser = subparsers.add_parser("list", help="List all tests or functions")
    list_parser.add_argument(
        "--category", "-c",
        help="List only tests in this category"
    )
    list_parser.add_argument(
        "--functions", "-f",
        action="store_true",
        help="List available functions instead of tests"
    )
    
    # Status command - show test status
    status_parser = subparsers.add_parser("status", help="Show test status and results")
    
    # Init command - create a new test
    init_parser = subparsers.add_parser("init", help="Initialize a new test")
    init_parser.add_argument(
        "category",
        help="Category name (e.g., booking)"
    )
    init_parser.add_argument(
        "test_name",
        help="Test name (e.g., book_consultation)"
    )
    
    # GUI command - start web interface
    gui_parser = subparsers.add_parser("gui", help="Start the web GUI")
    gui_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)"
    )
    gui_parser.add_argument(
        "--port", "-p",
        type=int,
        default=8080,
        help="Port to listen on (default: 8080)"
    )
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    commands = {
        "run": cmd_run,
        "explore": cmd_explore,
        "list": cmd_list,
        "status": cmd_status,
        "init": cmd_init,
        "gui": cmd_gui,
    }
    
    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
