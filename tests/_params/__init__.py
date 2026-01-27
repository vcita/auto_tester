"""
Test parameters for entity-agnostic tests.

Exports constants used across tests to avoid hardcoding entity names
(property, client, patient, etc.) which vary by vcita vertical.
"""

import re
import yaml
from pathlib import Path

# Load matter entity names from YAML
_yaml_path = Path(__file__).parent / "matter_entities.yaml"
with open(_yaml_path, "r", encoding="utf-8") as f:
    _data = yaml.safe_load(f)
    MATTER_ENTITY_NAMES = _data.get("matter_entity_names", [])

# Build regex pattern for "Add <entity>" button text
# Pattern: "Add\s+(property|client|patient|student|pet)s?" (substring match, case-insensitive)
# This matches "Add property", "Add client", "Add properties", etc.
_entity_pattern = "|".join(MATTER_ENTITY_NAMES)
ADD_MATTER_TEXT_REGEX = re.compile(rf"Add\s+({_entity_pattern})s?", re.IGNORECASE)

__all__ = ["ADD_MATTER_TEXT_REGEX", "MATTER_ENTITY_NAMES"]
