"""
Shared test parameters. Load from YAML so a single edit adds new values everywhere.
"""

import re
from pathlib import Path
from typing import List

import yaml

_PARAMS_DIR = Path(__file__).resolve().parent
_MATTER_ENTITIES_PATH = _PARAMS_DIR / "matter_entities.yaml"


def load_matter_entity_names() -> List[str]:
    """Return list of matter entity names (property, client, patient, etc.) from params file."""
    if not _MATTER_ENTITIES_PATH.exists():
        return ["property", "client", "patient", "student", "pet"]
    with open(_MATTER_ENTITIES_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    names = data.get("matter_entity_names") or []
    return [str(n).strip().lower() for n in names if n]


# Prefer loading from file so tests use the single source of truth
MATTER_ENTITY_NAMES: List[str] = load_matter_entity_names()


def add_matter_text_regex(substring: bool = True):
    """
    Return a compiled regex to match "Add <entity>" or "Add <entity>s" in the UI.
    Entity list comes from matter_entities.yaml.
    - substring=True (default): pattern like Add\\s+(a|b|c)s? for use within a section.
    - substring=False: pattern like ^Add\\s+(a|b|c)s?$ for exact match.
    """
    alternation = "|".join(re.escape(name) for name in MATTER_ENTITY_NAMES)
    if substring:
        pattern = rf"Add\s+({alternation})s?"
    else:
        pattern = rf"^Add\s+({alternation})s?$"
    return re.compile(pattern, re.IGNORECASE)


# Pre-built regex for "Add <entity>(s)?" (substring, for use inside Quick actions panel)
ADD_MATTER_TEXT_REGEX = add_matter_text_regex(substring=True)
