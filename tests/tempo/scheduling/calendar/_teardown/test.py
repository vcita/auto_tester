from playwright.sync_api import Page


def teardown_calendar(page: Page, context: dict) -> None:
    for key in list(context.keys()):
        if key.startswith("calendar_"):
            context.pop(key, None)
    print("  [OK] Calendar context cleared")
