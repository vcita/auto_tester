# Add/Remove Matter Collaborators
# Migrated from automation-js/features/steps/add-remove-staff-in-matter.feature (VCITA2-13794)
# Source: tests/clients/collaborators/manage_collaborators/script.md

from playwright.sync_api import Page

from tests.account_api import create_appointment_via_api
from tests.tempo.clients.collaborators.collaborators_ui import (
    add_staff_in_dialog,
    assert_collaborator_absent,
    assert_collaborator_shown,
    assert_no_collaborators,
    matter_frame,
    open_collaborators_dialog,
    open_matter,
    read_removal_warning,
    remove_staff_in_dialog,
    save_dialog,
)

STAFF_B = "Staff B"
STAFF_C = "Staff C"


def test_manage_collaborators(page: Page, context: dict) -> None:
    """Add Staff B and Staff C as collaborators, remove Staff B, then remove Staff C
    and verify the upcoming-appointments warning. Migrates add-remove-staff-in-matter."""
    client = context["collab_client"]
    client_id = context["collab_client_id"]
    client_name = context["collab_client_name"]
    service = context["collab_service"]
    staff_c_uid = context["collab_staff_c"]["uid"]

    print(f"  Step 1: Open matter page for '{client_name}'")
    open_matter(page, client_id)
    inner = matter_frame(page)

    print("  Step 2: Verify Staff B and Staff C are not collaborators yet")
    assert_collaborator_absent(inner, STAFF_B)
    assert_collaborator_absent(inner, STAFF_C)

    print("  Step 3: Add Staff B as collaborator")
    open_collaborators_dialog(inner)
    add_staff_in_dialog(inner, STAFF_B)
    save_dialog(inner)
    assert_collaborator_shown(inner, STAFF_B)

    print("  Step 4: Add Staff C as collaborator")
    open_collaborators_dialog(inner)
    add_staff_in_dialog(inner, STAFF_C)
    save_dialog(inner)
    assert_collaborator_shown(inner, STAFF_C)

    print("  Step 5: Remove Staff B (Staff C remains)")
    open_collaborators_dialog(inner)
    remove_staff_in_dialog(inner, STAFF_B)
    save_dialog(inner)
    assert_collaborator_absent(inner, STAFF_B)
    assert_collaborator_shown(inner, STAFF_C)

    print("  Step 6: Seed a future appointment for the client assigned to Staff C (warning trigger)")
    create_appointment_via_api(context, service, client, staff_uid=staff_c_uid)

    print("  Step 7: Remove Staff C and verify the upcoming-appointments warning")
    open_collaborators_dialog(inner)
    remove_staff_in_dialog(inner, STAFF_C)
    warning = read_removal_warning(inner)
    assert client_name in warning and STAFF_C in warning, (
        f"Expected removal warning to name '{client_name}' and '{STAFF_C}', got: {warning!r}"
    )
    save_dialog(inner)
    assert_no_collaborators(inner, [STAFF_B, STAFF_C])

    print("  [OK] Collaborators add/remove + removal warning verified")
