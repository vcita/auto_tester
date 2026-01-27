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
import json
from datetime import datetime
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
from src.runner.stress_test import StressTestRunner
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
    
    # Check for headless mode, keep-open flag, and until-test
    headless = args.headless if hasattr(args, 'headless') else False
    keep_open = getattr(args, 'keep_open', False)
    until_test = getattr(args, 'until_test', None)
    
    try:
        # Create runner
        runner = TestRunner(
            tests_root,
            headless=headless,
            keep_open=keep_open,
            until_test=until_test,
            config=config,
        )
        
        # Attach CLI reporter for real-time output
        reporter = CLIReporter(runner.events)
        
        # Run tests
        if args.category:
            # Run specific category (optionally only a subcategory)
            subcategory = getattr(args, 'subcategory', None)
            result = runner.run_category(args.category, subcategory_name=subcategory)
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


def cmd_groom_heal_requests(args):
    """Groom heal requests: update statuses and clean up old ones."""
    console.print("\n[bold]Groom Heal Requests Command[/bold]\n")
    console.print("This command is handled by the AI agent through the `/groom_heal_requests` slash command.")
    console.print("Please use the slash command in Cursor to groom heal requests.\n")


def cmd_stress_test(args):
    """Run stress test on categories."""
    config = load_config()
    tests_root = Path(__file__).parent / config.get("tests", {}).get("root_path", "tests")
    
    # Get categories from args
    categories = args.categories if args.categories else []
    
    if not categories:
        console.print("[red]Error: At least one category must be specified[/red]")
        console.print("Usage: stress_test --categories category1 category2 --iterations 10")
        return
    
    # Get iterations
    iterations = args.iterations
    if iterations < 1:
        console.print("[red]Error: Iterations must be at least 1[/red]")
        return
    
    # Check for headless mode and keep-open flag
    headless = args.headless if hasattr(args, 'headless') else False
    keep_open = getattr(args, 'keep_open', False)
    
    try:
        # Validate categories exist
        from src.discovery import TestDiscovery
        discovery = TestDiscovery(tests_root)
        valid_categories = []
        
        for cat_name in categories:
            category = discovery.find_category(cat_name)
            if not category:
                console.print(f"[yellow]Warning: Category '{cat_name}' not found, skipping[/yellow]")
            else:
                valid_categories.append(cat_name)
        
        if not valid_categories:
            console.print("[red]Error: No valid categories found[/red]")
            return
        
        # Run stress test
        stress_runner = StressTestRunner(
            tests_root=tests_root,
            headless=headless,
            keep_open=keep_open,
        )
        
        console.print(f"\n[bold]Starting stress test[/bold]")
        console.print(f"Categories: {', '.join(valid_categories)}")
        console.print(f"Iterations: {iterations}")
        console.print()
        
        results = stress_runner.run_stress_test(
            category_names=valid_categories,
            iterations=iterations,
        )
        
        # Print report
        stress_runner.print_report(results)
        
        # Exit with appropriate code
        total_failed = sum(r.failed_count for r in results)
        if total_failed > 0:
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]Error running stress test: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


def cmd_create_user(args):
    """Create a new user in vcita (signup + onboarding) and update config.yaml with that account. System is then ready to run tests."""
    import os
    import time
    config_path = Path(__file__).parent / "config.yaml"
    if not config_path.exists():
        console.print("[red]config.yaml not found[/red]")
        sys.exit(1)
    config = load_config()
    if "target" not in config:
        config["target"] = {}
    if "auth" not in config["target"]:
        config["target"]["auth"] = {}
    target = config["target"]

    email = getattr(args, "email", None) or f"itzik+autotest.{int(time.time())}@vcita.com"
    if getattr(args, "email", None) is None:
        console.print(f"[dim]Generated email: {email}[/dim]")
    password = getattr(args, "password", None) or os.environ.get("VCITA_TEST_PASSWORD", "vcita123")
    base_url = getattr(args, "base_url", None) or target.get("base_url") or "https://app.vcita.com"
    if getattr(args, "base_url", None) is not None:
        target["base_url"] = args.base_url

    address = getattr(args, "address", None) or os.environ.get("VCITA_TEST_ADDRESS", "123 Test Street")
    console.print("[cyan]Creating user in vcita (signup + onboarding)...[/cyan]")
    console.print(f"  email: {email}")
    console.print(f"  address: {address}")
    console.print("  (Browser will open; complete any CAPTCHA if prompted.)")
    ok = _run_create_user_then_update_config(
        config_path=config_path,
        config=config,
        email=email,
        password=password,
        base_url=base_url.rstrip("/"),
        address=address,
    )
    if not ok:
        sys.exit(1)


def _run_create_user_then_update_config(
    config_path: Path, config: dict, email: str, password: str, base_url: str, address: str = "123 Test Street"
) -> bool:
    """Launch browser, run create_user flow, then update config with the new account. Returns True on success."""
    from playwright.sync_api import sync_playwright

    target = config.get("target") or {}
    target.setdefault("auth", {})

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled"],
        )
        bypass_string = "#vUC5wTG98Hq5=BW+D_1c29744b-38df-4f40-8830-a7558ccbfa6b"
        custom_user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 " + bypass_string
        )
        video_dir = Path.cwd() / ".temp_videos"
        video_dir.mkdir(parents=True, exist_ok=True)
        bw_context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="America/New_York",
            user_agent=custom_user_agent,
            record_video_dir=str(video_dir),
            record_video_size={"width": 1920, "height": 1080},
        )
        bw_context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)
        page = bw_context.new_page()
        run_context = {"base_url": base_url.rstrip("/")}

        video_path = None
        try:
            from tests._functions.create_user.test import fn_create_user
            import os
            phone = os.environ.get("VCITA_TEST_PHONE", "0526111116")
            fn_create_user(
                page,
                run_context,
                email=email,
                password=password,
                phone=phone,
                address=address,
            )
        except Exception as e:
            console.print(f"[red]Create user failed: {e}[/red]")
            import traceback
            console.print(traceback.format_exc())
            failed = True
        else:
            failed = False
        finally:
            if page.video:
                video_path = page.video.path()
            bw_context.close()
            browser.close()
        if video_path and Path(video_path).exists():
            import time as _time
            stamp = _time.strftime("%Y%m%d_%H%M%S", _time.localtime())
            dest = video_dir / f"create_user_{stamp}.webm"
            Path(video_path).rename(dest)
            console.print(f"[dim]Video saved: {dest}[/dim]")
        if failed:
            return False

    # Success: update config with the new account
    target["auth"]["username"] = email
    target["auth"]["password"] = password
    target.pop("login_url", None)
    with open(config_path, "w") as f:
        import yaml
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    console.print("[green]User created and setup updated.[/green]")
    console.print(f"  base_url: {target.get('base_url', '')}")
    console.print(f"  email: {email}")
    console.print("[dim]Config saved. You can run tests with the new user.[/dim]")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="vcita Test Agent - AI-driven browser testing"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Run command - execute tests
    run_parser = subparsers.add_parser("run", help="Run tests. Use --create-user to create a new user first, then run.")
    run_parser.add_argument(
        "--category", "-c",
        help="Run only tests in this category (omit to run all categories)"
    )
    run_parser.add_argument(
        "--create-user",
        dest="create_user",
        action="store_true",
        help="Create a new user in vcita (signup + onboarding), update config, then run tests in one go"
    )
    run_parser.add_argument(
        "--create-user-email",
        dest="create_user_email",
        default=None,
        help="Email for new user when using --create-user (default: itzik+autotest.<timestamp>@vcita.com)"
    )
    run_parser.add_argument(
        "--create-user-password",
        dest="create_user_password",
        default=None,
        help="Password for new user when using --create-user (default: VCITA_TEST_PASSWORD or vcita123)"
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
    run_parser.add_argument(
        "--until-test",
        help="Stop before this test; dump context to until_test_context.json in run dir and leave browser open for manual debugging. For MCP debugging, start a new MCP session and use the dump. Test name can be full path (e.g., 'Events/Schedule Event') or just the test name."
    )
    run_parser.add_argument(
        "--subcategory",
        help="Run only this subcategory (e.g. 'services'). Parent category's setup runs first. Use with --category."
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
    
    # Create user command - create a new user in vcita and update config so tests run with that account
    create_user_parser = subparsers.add_parser("create_user", help="Create a new user in vcita (signup + onboarding) and update config.yaml. Opens browser.")
    create_user_parser.add_argument("--email", default=None, help="Account email (default: itzik+autotest.<timestamp>@vcita.com)")
    create_user_parser.add_argument("--password", default=None, help="Password (default: env VCITA_TEST_PASSWORD or vcita123)")
    create_user_parser.add_argument("--address", default=None, help="Business address in Welcome dialog (default: env VCITA_TEST_ADDRESS or 123 Test Street)")
    create_user_parser.add_argument("--base-url", dest="base_url", default=None, help="Base URL (default: from config; login URL = base_url + '/login')")

    # Stress test command - run categories multiple times
    groom_parser = subparsers.add_parser("groom_heal_requests", help="Groom heal requests: update statuses and clean up old ones")
    
    stress_parser = subparsers.add_parser("stress_test", help="Run stress test on categories")
    stress_parser.add_argument(
        "--categories", "-c",
        nargs="+",
        required=True,
        help="Category names to stress test (can specify multiple)"
    )
    stress_parser.add_argument(
        "--iterations", "-i",
        type=int,
        required=True,
        help="Number of times to run each category"
    )
    stress_parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode"
    )
    stress_parser.add_argument(
        "--keep-open",
        action="store_true",
        help="Keep browser open on failure for debugging"
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
        "create_user": cmd_create_user,
        "stress_test": cmd_stress_test,
        "groom_heal_requests": cmd_groom_heal_requests,
    }
    
    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
