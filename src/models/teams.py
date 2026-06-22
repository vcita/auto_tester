"""Canonical team taxonomy and automation-js provenance mapping.

A test's owning team is the single squad responsible for keeping it working.
Teams mirror the automation-js squad folders, with the legacy ``steps`` squad
folded into ``tempo``.
"""

# The six teams that own autotester tests. Each is also a top-level folder
# under tests/ (team-first modularity).
CANONICAL_TEAMS = (
    "backstage",
    "maestro",
    "salsa",
    "spotlights",
    "tango",
    "tempo",
)

# Maps an automation-js squad folder (the migration provenance) to its
# autotester owning team. ``steps`` has no autotester team of its own; its
# coverage is owned by ``tempo``.
SQUAD_TO_TEAM = {
    "backstage": "backstage",
    "maestro": "maestro",
    "salsa": "salsa",
    "spotlights": "spotlights",
    "tango": "tango",
    "tempo": "tempo",
    "steps": "tempo",
}


def is_canonical_team(value: str) -> bool:
    """Return True when value is one of the canonical team names."""
    return isinstance(value, str) and value.strip().lower() in CANONICAL_TEAMS


def normalize_team(value: str) -> str:
    """Normalize a team or squad name to a canonical team, or '' if unknown."""
    if not isinstance(value, str):
        return ""
    key = value.strip().lower()
    if key in CANONICAL_TEAMS:
        return key
    return SQUAD_TO_TEAM.get(key, "")
