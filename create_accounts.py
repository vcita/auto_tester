#!/usr/bin/env python3
"""
Create a fresh business account via the Create Business API for each test category.

Standalone script that wraps the shared account_factory and env_config modules.

Usage:
    python create_accounts.py                     # production (default)
    python create_accounts.py --env=integration   # integration env
    python create_accounts.py --env=aviv          # custom feature env
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.discovery import TestDiscovery
from src.runner.account_factory import (
    create_account,
    load_directory_token,
    FatalTokenError,
    AccountCreationError,
)
from src.runner.env_config import resolve_api_base_url

console = Console()


def _load_config() -> dict:
    import yaml
    config_path = Path(__file__).parent / "config.yaml"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def discover_categories() -> list[str]:
    config = _load_config()
    tests_root = Path(__file__).parent / config.get("tests", {}).get("root_path", "tests")
    discovery = TestDiscovery(tests_root)
    categories = discovery.scan()
    return [cat.path.name for cat in categories if cat.path]


def run(env: str) -> None:
    api_base_url = resolve_api_base_url(env)
    console.print(f"[bold]Environment:[/bold] {env}")
    console.print(f"[bold]API base:   [/bold] {api_base_url}")

    config = _load_config()
    token = load_directory_token(config)
    if not token:
        console.print(
            "[red]No directory token found. "
            "Set VCITA_DIRECTORY_TOKEN env var or add target.directory_token in config.yaml.[/red]"
        )
        sys.exit(1)

    category_names = discover_categories()
    if not category_names:
        console.print("[yellow]No categories discovered — nothing to create.[/yellow]")
        return

    console.print(f"[bold]Categories:[/bold] {', '.join(category_names)}\n")

    results: list[dict] = []
    for cat_name in category_names:
        console.print(f"[cyan]Creating account for category: {cat_name}[/cyan]")
        try:
            account = create_account(api_base_url, token, cat_name)
            results.append({
                "category": cat_name,
                "business_id": account["business_id"],
                "auth_token": account["auth_token"],
                "email": account["email"],
                "name": account["name"],
                "status": "OK",
            })
            console.print(f"  [green]Created[/green] {account['name']}  email={account['email']}")
        except FatalTokenError as exc:
            console.print(f"[red]FATAL: {exc}[/red]")
            sys.exit(1)
        except AccountCreationError as exc:
            console.print(f"  [red]Skipped: {exc}[/red]")
            results.append({
                "category": cat_name,
                "business_id": "-",
                "auth_token": "-",
                "email": "-",
                "name": "-",
                "status": "SKIPPED",
                "detail": str(exc),
            })

    _print_summary(results)


def _print_summary(results: list[dict]) -> None:
    console.print()
    table = Table(title="Account Creation Summary")
    table.add_column("Category", style="bold")
    table.add_column("Status")
    table.add_column("Business ID")
    table.add_column("Email")
    table.add_column("Auth Token")

    for r in results:
        status = r["status"]
        style = "green" if status == "OK" else "yellow" if status == "SKIPPED" else "red"
        token_val = r["auth_token"]
        token_display = token_val[:4] + "***" if token_val not in ("-", "N/A", "") else token_val
        table.add_row(r["category"], f"[{style}]{status}[/{style}]", r["business_id"], r["email"], token_display)

    console.print(table)

    ok_count = sum(1 for r in results if r["status"] == "OK")
    skip_count = sum(1 for r in results if r["status"] == "SKIPPED")
    console.print(f"\n[bold]{ok_count}/{len(results)}[/bold] accounts created successfully.", end="")
    if skip_count:
        console.print(f"  [yellow]{skip_count} skipped.[/yellow]")
    else:
        console.print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a business account for each test category via the Create Business API."
    )
    parser.add_argument(
        "--env",
        default="production",
        help="Target environment. 'production' (default), 'integration', or a feature-env name (e.g. 'aviv').",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(args.env)
