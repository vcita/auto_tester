"""Browser configuration helpers shared by CLI and runner paths."""

from typing import Any, Dict, Optional


DEFAULT_VIEWPORT = {"width": 1280, "height": 720}


def get_browser_viewport(config: Optional[Dict[str, Any]]) -> Dict[str, int]:
    """Return a valid Playwright viewport from config.yaml, or the default."""
    if not isinstance(config, dict):
        return DEFAULT_VIEWPORT.copy()

    browser_config = config.get("browser")
    if not isinstance(browser_config, dict):
        return DEFAULT_VIEWPORT.copy()

    viewport = browser_config.get("viewport")
    if not isinstance(viewport, dict):
        return DEFAULT_VIEWPORT.copy()

    width = _positive_int(viewport.get("width"))
    height = _positive_int(viewport.get("height"))
    if width is None or height is None:
        return DEFAULT_VIEWPORT.copy()

    return {"width": width, "height": height}


def get_browser_window_size_arg(config: Optional[Dict[str, Any]]) -> str:
    viewport = get_browser_viewport(config)
    return f'--window-size={viewport["width"]},{viewport["height"]}'


def _positive_int(value: Any) -> Optional[int]:
    if isinstance(value, bool):
        return None

    if isinstance(value, int) and value > 0:
        return value

    return None
