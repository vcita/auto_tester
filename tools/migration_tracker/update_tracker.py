#!/usr/bin/env python3
"""
Update the migration coverage tracker: upsert one row into the Google Sheet
(source of truth) and refresh the Confluence dashboard in place.

Run from the repo root after a migration is validated and the PR is open:

    python -m tools.migration_tracker.update_tracker upsert \
        --feature features/tempo/calendar-settings.feature \
        --path tests/scheduling/calendar_settings \
        --status "In review" --scope "..." \
        --original "2 scenarios / 14 steps, 74.0s" \
        --migrated "3/3, ~43s" --improvement "~42% faster" \
        --stability "stress 10/10 on 2026-06-04" \
        --jira-key VCITA2-13796 --jira-url https://.../VCITA2-13796 \
        --pr-label "PR #50" --pr-url https://github.com/vcita/autotester/pull/50 \
        --refresh-confluence --ff-migrated 18 --ff-total 113 \
        --sc-migrated 36 --sc-total 279

`init` (one-time) seeds an empty, shared sheet from a 12-field rows JSON.
See tools/migration_tracker/README.md for setup.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import config, confluence
from .formatting import normalize_durations
from .google_sheets import SheetsClient
from .sheet_format import build_init_requests


def _hyperlink(label: str, url: str) -> str:
    if not label:
        return ""
    if not url:
        return label
    safe = label.replace('"', '""')
    return f'=HYPERLINK("{url}","{safe}")'


def _row_to_cells(feature, path, status, scope, original, migrated,
                  improvement, stability, jira_cell, pr_cell) -> list:
    return [feature, path, status, scope, original, migrated,
            improvement, stability, jira_cell, pr_cell]


def _sheet_url() -> str:
    return f"https://docs.google.com/spreadsheets/d/{config.SHEET_ID}/edit"


def _client() -> SheetsClient:
    return SheetsClient(
        config.require("MIGRATION_TRACKER_GSA_KEY", config.GSA_KEY_PATH),
        config.require("MIGRATION_TRACKER_SHEET_ID", config.SHEET_ID),
    )


def cmd_init(args: argparse.Namespace) -> int:
    rows = json.loads(Path(args.rows).read_text())
    data = rows[1:]
    client = _client()
    sheet_id = client.ensure_tab(config.SHEET_TAB)

    values = [config.COLUMNS]
    for r in data:
        feature, path, status, scope, original, migrated, improvement, stability, \
            jira_label, jira_url, pr_label, pr_url = r
        values.append(_row_to_cells(
            feature, path, status, scope, original, normalize_durations(migrated),
            improvement, stability,
            _hyperlink(jira_label, jira_url), _hyperlink(pr_label, pr_url),
        ))

    client.update_values(f"{config.SHEET_TAB}!A1", values)
    client.batch_update(build_init_requests(sheet_id, len(config.COLUMNS), len(values)))
    share = client.share_anyone_reader()
    print(f"Seeded {len(data)} rows into '{config.SHEET_TAB}'. {share}")
    print(f"Service account: {client.service_account_email}")
    print(f"Sheet URL: {_sheet_url()}")
    return 0


def cmd_upsert(args: argparse.Namespace) -> int:
    client = _client()
    cells = _row_to_cells(
        args.feature, args.path, args.status, args.scope, args.original,
        normalize_durations(args.migrated), args.improvement, args.stability,
        _hyperlink(args.jira_key, args.jira_url),
        _hyperlink(args.pr_label, args.pr_url),
    )
    keys = [row[0] if row else "" for row in client.get_values(f"{config.SHEET_TAB}!A:A")]
    try:
        index = keys.index(args.feature)  # 0-based incl. header
        client.update_values(f"{config.SHEET_TAB}!A{index + 1}", [cells])
        print(f"Updated existing row {index + 1} for {args.feature}")
    except ValueError:
        client.append_values(f"{config.SHEET_TAB}!A1", [cells])
        print(f"Appended new row for {args.feature}")

    if args.refresh_confluence:
        _refresh_confluence(args, latest_path=args.path)
    return 0


def cmd_confluence(args: argparse.Namespace) -> int:
    _refresh_confluence(args, latest_path=args.latest_path)
    return 0


def _refresh_confluence(args: argparse.Namespace, latest_path: str) -> None:
    totals = {
        "feature_files_migrated": args.ff_migrated,
        "feature_files_total": args.ff_total,
        "scenarios_migrated": args.sc_migrated,
        "scenarios_total": args.sc_total,
    }
    summary = _summary_updates(args, latest_path)

    base_file = getattr(args, "base_file", "")
    if base_file:
        doc, version, title = json.loads(Path(base_file).read_text()), None, None
    else:
        doc, version, title = confluence.fetch_current()

    doc = confluence.refresh(doc, _sheet_url(), totals, summary)

    if args.emit:
        payload = json.dumps(doc, ensure_ascii=False, indent=2)
        Path(args.emit).write_text(payload)
        print(f"Wrote Confluence ADF doc ({len(payload)} bytes) to {args.emit}")
        return
    if version is None:
        _, version, title = confluence.fetch_current()
    result = confluence.publish(doc, version, title)
    print(f"Published Confluence v{result['version']}: {result['url']}")


def _summary_updates(args: argparse.Namespace, latest_path: str) -> dict:
    """Build the Summary metric-row updates from whatever values were provided."""
    updates: dict[str, str] = {}
    if args.ff_total:
        updates["Candidate migration progress by feature file"] = (
            f"{args.ff_migrated} / {args.ff_total} candidate feature files migrated, "
            f"{args.ff_total - args.ff_migrated} left")
    if args.sc_total:
        updates["Candidate migration progress by scenario"] = (
            f"{args.sc_migrated} / {args.sc_total} candidate scenario definitions migrated, "
            f"{args.sc_total - args.sc_migrated} left")
    if args.tracked_ff or args.tracked_sc:
        updates["Tracked migrated scope, including non-candidates"] = (
            f"{args.tracked_ff} feature files, {args.tracked_sc} scenario definitions")
    if args.validated_scopes:
        updates["Validated autotester scopes"] = str(args.validated_scopes)
    if latest_path:
        updates["Latest migrated scope"] = latest_path
    if args.jira_key:
        updates["Latest Jira"] = args.jira_key
    if args.latest_branch:
        updates["Latest branch"] = args.latest_branch
    return updates


def _add_row_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--feature", required=True)
    parser.add_argument("--path", required=True)
    parser.add_argument(
        "--status", default="In review",
        help="Lifecycle status: Proposed | In progress | Needs stabilization | "
             "In review (PR open) | Merged (PR merged) | Blocked",
    )
    parser.add_argument("--scope", default="")
    parser.add_argument("--original", default="")
    parser.add_argument("--migrated", default="")
    parser.add_argument("--improvement", default="")
    parser.add_argument("--stability", default="")
    parser.add_argument("--jira-key", default="")
    parser.add_argument("--jira-url", default="")
    parser.add_argument("--pr-label", default="")
    parser.add_argument("--pr-url", default="")


def _add_totals_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--ff-migrated", type=int, default=0)
    parser.add_argument("--ff-total", type=int, default=0)
    parser.add_argument("--sc-migrated", type=int, default=0)
    parser.add_argument("--sc-total", type=int, default=0)
    parser.add_argument("--tracked-ff", type=int, default=0,
                        help="Tracked migrated feature files (incl. non-candidates)")
    parser.add_argument("--tracked-sc", type=int, default=0,
                        help="Tracked migrated scenario definitions (incl. non-candidates)")
    parser.add_argument("--validated-scopes", type=int, default=0)
    parser.add_argument("--latest-branch", default="",
                        help="Latest branch — PR text, e.g. 'VCITA2-13796_migrate_x — PR #50'")
    parser.add_argument("--base-file",
                        help="Load the base ADF doc from this file instead of fetching the live page (one-time restore)")
    parser.add_argument("--emit", help="Write the ADF doc to this file instead of publishing")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Seed an empty shared sheet from a rows JSON")
    init.add_argument("--rows", required=True, help="Path to the 12-field rows JSON")
    init.set_defaults(func=cmd_init)

    upsert = sub.add_parser("upsert", help="Insert/update one row (+ optional Confluence refresh)")
    _add_row_args(upsert)
    upsert.add_argument("--refresh-confluence", action="store_true")
    _add_totals_args(upsert)
    upsert.set_defaults(func=cmd_upsert)

    conf = sub.add_parser("confluence", help="Refresh only the Confluence dashboard in place")
    conf.add_argument("--latest-path", required=True, help="autotester path of the newest migration")
    conf.add_argument("--jira-key", default="")
    conf.add_argument("--jira-url", default="")
    conf.add_argument("--pr-label", default="")
    conf.add_argument("--pr-url", default="")
    _add_totals_args(conf)
    conf.set_defaults(func=cmd_confluence)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
