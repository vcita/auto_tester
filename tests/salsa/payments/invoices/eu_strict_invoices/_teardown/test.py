from playwright.sync_api import Page


def teardown_eu_strict_invoices(page: Page, context: dict) -> None:
    prefixes = (
        "created_",
        "eu_strict_",
        "invoice_",
        "recorded_",
        "refunded_",
        "credit_",
    )
    for key in list(context.keys()):
        if key.startswith(prefixes):
            context.pop(key, None)
