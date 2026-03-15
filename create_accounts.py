#!/usr/bin/env python3
"""
Create a fresh business account via the Create Business API for each test category.

Mirrors the _create_account pattern from vcita/automation-js (api/accounts.js).
Environment-specific URLs follow automation-js/runtime/envs.js conventions.

Usage:
    python create_accounts.py                     # production (default)
    python create_accounts.py --env=integration   # integration env
    python create_accounts.py --env=aviv          # custom feature env
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Optional

import requests
import yaml
from rich.console import Console
from rich.table import Table

sys.path.insert(0, str(Path(__file__).parent / "src"))
from src.discovery import TestDiscovery

console = Console()

KNOWN_ENVS = {
    "production": "https://api.vcita.biz",
    "integration": "https://api2.meet2know.com",
}

FEATURE_ENV_TEMPLATE = "https://core-{name}.external.int-eks.vchost.co"

DEFAULT_PASSWORD = "vcita123"
COUNTRY = "United States"
BUSINESSES_PATH = "/platform/v1/businesses"
REQUEST_TIMEOUT = 30
MAX_RETRIES = 1
RETRY_BACKOFF = 2


def resolve_api_base_url(env: str) -> str:
    if env in KNOWN_ENVS:
        return KNOWN_ENVS[env]
    return FEATURE_ENV_TEMPLATE.format(name=env)


def load_directory_token() -> Optional[str]:
    token = os.environ.get("VCITA_DIRECTORY_TOKEN")
    if token:
        return token

    config_path = Path(__file__).parent / "config.yaml"
    if not config_path.exists():
        return None
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
        return (config.get("target") or {}).get("directory_token")
    except Exception:
        return None


def create_account(api_base_url: str, token: str, category_name: str) -> dict:
    """
    Create a business account for a single category.

    Follows the _create_account pattern from automation-js/api/accounts.js:
    POST /platform/v1/businesses with admin_account + business + meta payload.

    Returns the parsed JSON response on success.
    Raises on unrecoverable HTTP errors (401).
    """
    timestamp = int(time.time())
    email = f"auto.api.{category_name.lower()}.{timestamp}@vcita.com"
    business_name = f"Auto_{category_name}_{timestamp}"

    payload = {
        "admin_account": {
            "email": email,
            "password": DEFAULT_PASSWORD,
            "country_name": COUNTRY,
        },
        "business": {
            "name": business_name,
            "country_name": COUNTRY,
        },
        "meta": {},
    }

    url = f"{api_base_url.rstrip('/')}{BUSINESSES_PATH}"
    headers = {"Authorization": f"Token {token}"}

    last_error = None
    for attempt in range(1 + MAX_RETRIES):
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
            _handle_http_error(resp, category_name)
            data = resp.json()
            console.print(f"  [green]Created[/green] {business_name}  email={email}")
            return data
        except _FatalTokenError:
            raise
        except _SkipCategoryError:
            raise
        except Exception as exc:
            last_error = exc
            if attempt < MAX_RETRIES:
                console.print(f"  [yellow]Retry {attempt + 1}/{MAX_RETRIES} for {category_name}...[/yellow]")
                time.sleep(RETRY_BACKOFF * (attempt + 1))

    raise _SkipCategoryError(f"All retries exhausted for {category_name}: {last_error}")


class _FatalTokenError(Exception):
    pass


class _SkipCategoryError(Exception):
    pass


def _handle_http_error(resp: requests.Response, category_name: str) -> None:
    if resp.ok:
        return

    status = resp.status_code
    try:
        body = resp.json()
    except Exception:
        body = {"message": resp.text[:500]}

    detail = body.get("message") or body.get("data") or resp.text[:300]

    if status == 401:
        raise _FatalTokenError(
            f"401 Unauthorized — token is invalid or expired. "
            f"Set VCITA_DIRECTORY_TOKEN env var or target.directory_token in config.yaml. "
            f"Detail: {detail}"
        )

    if status in (400, 409):
        raise _SkipCategoryError(f"HTTP {status} for {category_name}: {detail}")

    if status >= 500:
        raise RuntimeError(f"HTTP {status} server error for {category_name}: {detail}")

    resp.raise_for_status()


def discover_categories() -> list[str]:
    config_path = Path(__file__).parent / "config.yaml"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
    else:
        config = {}

    tests_root = Path(__file__).parent / config.get("tests", {}).get("root_path", "tests")
    discovery = TestDiscovery(tests_root)
    categories = discovery.scan()
    return [cat.path.name for cat in categories if cat.path]


def run(env: str) -> None:
    api_base_url = resolve_api_base_url(env)
    console.print(f"[bold]Environment:[/bold] {env}")
    console.print(f"[bold]API base:   [/bold] {api_base_url}")

    token = load_directory_token()
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
            data = create_account(api_base_url, token, cat_name)
            biz = data.get("data", {}).get("business", {})
            results.append({
                "category": cat_name,
                "business_id": biz.get("business", {}).get("id", "N/A"),
                "auth_token": biz.get("meta", {}).get("auth_token", "N/A"),
                "email": biz.get("admin_account", {}).get("email", "N/A"),
                "name": biz.get("business", {}).get("name", "N/A"),
                "status": "OK",
            })
        except _FatalTokenError as exc:
            console.print(f"[red]FATAL: {exc}[/red]")
            sys.exit(1)
        except _SkipCategoryError as exc:
            console.print(f"  [red]Skipped: {exc}[/red]")
            results.append({
                "category": cat_name,
                "business_id": "-",
                "auth_token": "-",
                "email": "-",
                "name": "-",
                "status": f"FAILED ({exc})",
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
        style = "green" if r["status"] == "OK" else "red"
        token_display = r["auth_token"][:12] + "..." if len(r["auth_token"]) > 15 else r["auth_token"]
        table.add_row(r["category"], f"[{style}]{r['status']}[/{style}]", r["business_id"], r["email"], token_display)

    console.print(table)

    ok_count = sum(1 for r in results if r["status"] == "OK")
    console.print(f"\n[bold]{ok_count}/{len(results)}[/bold] accounts created successfully.")


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
