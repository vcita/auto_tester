"""Duration formatting helpers for the coverage tracker.

The "Original result" column shows durations as `<m>m<s>s` (e.g. `1m47.029s`)
for values >= 60s and bare seconds (e.g. `24.224s`) below 60s. We normalize the
"Migrated result" durations to the same shape so both columns read consistently.
"""

from __future__ import annotations

import re

# A number directly followed by `s` is a seconds value (e.g. `73.6s`, `~204s`).
_DURATION_RE = re.compile(r"(~?)(\d+(?:\.\d+)?)s")


def _to_minutes_seconds(match: re.Match) -> str:
    tilde, raw = match.group(1), match.group(2)
    value = float(raw)
    if value < 60:
        return match.group(0)
    minutes = int(value // 60)
    remainder = round(value - minutes * 60, 3)
    seconds = f"{remainder:.3f}".rstrip("0").rstrip(".")
    return f"{tilde}{minutes}m{seconds}s"


def normalize_durations(text: str) -> str:
    """Rewrite every `>=60s` duration in `text` as `<m>m<s>s`, leaving the rest."""
    return _DURATION_RE.sub(_to_minutes_seconds, text)
