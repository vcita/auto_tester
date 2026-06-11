# Nest Existing Matter Under Contact
# Migrated from automation-js matters-management.feature (VCITA2-13952)
# Legacy: client.js clickNestingInMenu + performNesting + getMattersNameList/getContact + getMatterTitleName
# Source: tests/clients/matters_management/nest_matter/script.md

from playwright.sync_api import Page

from tests.tempo.clients.matters_management.matters_helpers import (
    displayed_contact_email,
    expect_title,
    matter_frames,
    matter_list_names,
    nest_matter_under_contact,
    open_matter_page,
)


def test_nest_matter(page: Page, context: dict) -> None:
    """Nest the standalone 'matter client' under the 'contact client' contact."""
    matter_client_id = context["matter_client_id"]
    matter_client_name = context["matter_client_name"]      # "matter client"
    contact_client_name = context["contact_client_name"]    # "contact client"
    contact_client_email = context["contact_client_email"]

    print(f"  Step 1: Opening standalone matter page ({matter_client_id})...")
    inner, outer = open_matter_page(page, context, matter_client_id)

    print(f"  Step 2: Nesting {matter_client_name!r} under {contact_client_name!r}...")
    nest_matter_under_contact(page, inner, outer, contact_client_name, contact_client_email)

    print(f"  Step 3: Verifying {matter_client_name!r} now sits under {contact_client_email!r}...")
    # Verify in-place: after nesting, the standalone matter URL no longer resolves
    # (it became a child matter), but the page is already showing the nested view
    # with the contact email switched (the nest helper waited for that).
    inner, _ = matter_frames(page)
    names = matter_list_names(inner)
    assert any(matter_client_name in n for n in names), (
        f"{matter_client_name!r} not in matter list {names}"
    )
    email = displayed_contact_email(inner)
    assert email == contact_client_email, f"contact email expected {contact_client_email!r}, got {email!r}"
    expect_title(inner, matter_client_name)

    print(f"  [OK] {matter_client_name} nested under {contact_client_email}; title shows {matter_client_name}")
