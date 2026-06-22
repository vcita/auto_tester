# Auto-generated from script.md
# Source: tests/salsa/payments/packages/_teardown/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md
"""Teardown for the packages (back-office) subcategory.

Deletes the packages and client-package assignments created during the run (CRUD cleanup),
so the isolated account is left minimal across stress iterations. Best-effort: the runner
tears the account down regardless.
"""

from playwright.sync_api import Page

from tests.salsa.payments.packages.packages_helpers import (
    delete_client_package,
    delete_package,
)


def teardown_packages(page: Page, context: dict) -> None:
    cleanup = context.get("packages_cleanup") or {}
    client_packages = cleanup.get("client_packages") or []
    packages = cleanup.get("packages") or []

    print(f"  Teardown: deleting {len(client_packages)} client-packages, "
          f"{len(packages)} packages")
    for cp_id in client_packages:
        delete_client_package(context, cp_id)
    for pkg_id in packages:
        delete_package(context, pkg_id)
    print("  [OK] packages teardown complete")
