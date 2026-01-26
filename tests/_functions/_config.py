"""
Shared config for test functions. Use get_base_url() so tests never hardcode vcita.com.
Base URL comes from context (injected by runner) or from config.yaml.
"""

from pathlib import Path
from typing import Any, Dict, Optional


def get_base_url(context: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> str:
    """
    Return target base URL (no trailing slash). Login URL is base_url + "/login".

    Lookup order: params["base_url"] -> context["base_url"] -> config.yaml target.base_url.

    Raises:
        ValueError: if base_url is not set in params, context, or config.yaml.
    """
    if params and params.get("base_url"):
        return str(params.get("base_url", "")).rstrip("/")
    if context and context.get("base_url"):
        return str(context["base_url"]).rstrip("/")
    base = _load_base_url_from_config()
    if base:
        return base
    raise ValueError(
        "base_url not set: configure target.base_url in config.yaml, "
        "or pass base_url in context/params (runner injects from config)."
    )


def _load_base_url_from_config() -> Optional[str]:
    """Load target.base_url from project root config.yaml. Returns None if missing."""
    # From tests/_functions/_config.py -> project root = parent.parent.parent
    project_root = Path(__file__).resolve().parent.parent.parent
    config_path = project_root / "config.yaml"
    if not config_path.exists():
        return None
    try:
        import yaml
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        target = (config or {}).get("target") or {}
        base = target.get("base_url")
        return str(base).rstrip("/") if base else None
    except Exception:
        return None
