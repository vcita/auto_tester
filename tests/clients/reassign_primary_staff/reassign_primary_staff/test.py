# Reassign Matter Primary Staff
# Migrated from automation-js/features/steps/reassign-matter-primary-staff.feature (VCITA2-13791)
# Source: tests/clients/reassign_primary_staff/reassign_primary_staff/script.md

import re
import time

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, expect

from tests.clients.reassign_primary_staff.reassign_helpers import (
    create_appointment_via_api,
    create_client_via_api,
    create_platform_staff_via_api,
    create_service_via_api,
    get_business_email_by_subject,
)

UI_TIMEOUT = 5000
PAGE_READY_TIMEOUT = 15000
ASSIGN_PROPAGATION_ATTEMPTS = 6

STAFF_B_NAME = "Staff B"
SERVICE_NAME = "test_service"
CLIENT_FIRST = "first"
CLIENT_LAST = "last"


def test_reassign_primary_staff(page: Page, context: dict) -> None:
    """Reassign a matter's primary staff to Staff B and verify reassignment + email.

    Migrates automation-js `reassign-matter-primary-staff.feature`.
    """
    ms = int(time.time() * 1000)
    staff_email = f"staffb+{ms}@vmeetme.com"
    client_email = f"contact+{ms}@vmeetme.com"
    assignment_subject = f"{CLIENT_FIRST} {CLIENT_LAST} was assigned to you"

    # ---- API setup (isolated auto-account) ----
    print("  Step 1: Creating Staff B via Platform API...")
    create_platform_staff_via_api(context, STAFF_B_NAME, staff_email, role="user")

    print("  Step 2: Creating client via API...")
    client = create_client_via_api(context, CLIENT_FIRST, CLIENT_LAST, client_email)
    context["reassign_client_id"] = client["id"]

    print("  Step 3: Creating service via API...")
    service = create_service_via_api(context, SERVICE_NAME)

    print("  Step 4: Scheduling appointment (assigned to owner) via API...")
    create_appointment_via_api(context, service, client)

    # ---- UI: reassign matter primary staff ----
    print(f"  Step 5: Opening matter page for {client['name']}...")
    _open_matter(page, client["id"])
    inner, outer = _matter_frames(page)

    print("  Step 6: Opening change-staff editor...")
    _open_change_staff(inner)

    print(f"  Step 7: Reassigning primary staff to {STAFF_B_NAME} (with appointments)...")
    _select_staff_reassign_and_save(outer, STAFF_B_NAME)

    # ---- Assertion 1: appointment reassigned to Staff B ----
    print(f"  Step 8: Verifying appointment '{SERVICE_NAME}' is assigned to {STAFF_B_NAME}...")
    _assert_appointment_assigned(page, SERVICE_NAME, STAFF_B_NAME)

    # ---- Assertion 2: business assignment email ----
    print(f"  Step 9: Verifying business email with subject {assignment_subject!r}...")
    get_business_email_by_subject(context, assignment_subject)

    print("  [OK] Reassign primary staff verified (appointment + email)")


# --------------------------------------------------------------------------- #
# UI helpers
# --------------------------------------------------------------------------- #
def _open_matter(page: Page, client_id: str) -> None:
    app_base = page.url.split("/app/")[0] if "/app/" in page.url else None
    if not app_base:
        raise ValueError(f"Cannot infer app base URL from current page URL: {page.url}")
    page.goto(f"{app_base}/app/clients/{client_id}", wait_until="domcontentloaded", timeout=30000)
    expect(page).to_have_url(re.compile(rf"/app/clients/{re.escape(client_id)}"), timeout=PAGE_READY_TIMEOUT)
    page.locator('iframe[title="angularjs"]').wait_for(state="visible", timeout=PAGE_READY_TIMEOUT)


def _matter_frames(page: Page):
    """Return (inner Vue matter frame, outer Angular frame)."""
    outer = page.frame_locator('iframe[title="angularjs"]')
    inner = outer.frame_locator("#vue_iframe_layout")
    inner.locator(".matter-name-title").first.wait_for(state="visible", timeout=PAGE_READY_TIMEOUT)
    return inner, outer


def _open_change_staff(inner) -> None:
    inner.locator(".matter-name-title").first.click()
    change_btn = inner.locator(".matter-staff__change--btn").first
    change_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
    change_btn.click()


def _select_staff_reassign_and_save(outer, staff_name: str) -> None:
    # Angular-Material reassign dialog renders in the outer (angular) frame.
    dropdown = outer.locator(".select-container.md-input-has-value").first
    dropdown.wait_for(state="visible", timeout=UI_TIMEOUT)
    dropdown.click()

    option = outer.get_by_role("option", name=staff_name).or_(
        outer.locator("md-option").filter(has_text=staff_name)
    ).first
    option.wait_for(state="visible", timeout=UI_TIMEOUT)
    option.click()

    checkbox = outer.locator(
        'md-checkbox[aria-label="Reassign these appointments to the new assignee"]'
    ).first
    checkbox.wait_for(state="visible", timeout=UI_TIMEOUT)
    if checkbox.get_attribute("aria-checked") != "true":
        checkbox.click()

    save_btn = outer.get_by_role("button", name=re.compile(r"^\s*Save\s*$", re.I)).first
    save_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
    save_btn.click()
    # Dialog closes on success.
    expect(checkbox).to_be_hidden(timeout=PAGE_READY_TIMEOUT)


def _assert_appointment_assigned(page: Page, service_name: str, staff_name: str) -> None:
    last_value = ""
    last_error: str | None = None
    for _ in range(ASSIGN_PROPAGATION_ATTEMPTS):
        try:
            inner, _ = _matter_frames(page)
            _open_bookings_tab(inner)
            booking = inner.locator(".matter-page-list-item").filter(
                has=inner.locator(".booking-title", has_text=service_name)
            ).first
            booking.wait_for(state="visible", timeout=UI_TIMEOUT)
            subtitle = booking.locator(".booking-with").first.inner_text().strip()
            # Subtitle format is "With <name>"; strip the leading word.
            last_value = subtitle.split(" ", 1)[1].strip() if " " in subtitle else subtitle
            if last_value == staff_name:
                return
        except PlaywrightTimeoutError as error:
            last_error = str(error).splitlines()[0]
        page.reload(wait_until="domcontentloaded")

    suffix = f"; last readiness error: {last_error}" if last_error else ""
    raise AssertionError(
        f"Appointment '{service_name}' expected to be assigned to {staff_name!r}, "
        f"got {last_value!r}{suffix}"
    )


def _open_bookings_tab(inner) -> None:
    tab = inner.get_by_role("tab", name=re.compile(r"Bookings", re.I)).or_(
        inner.get_by_text(re.compile(r"^\s*Bookings\s*$", re.I))
    ).first
    tab.wait_for(state="visible", timeout=UI_TIMEOUT)
    tab.click()
