# Auto-generated from script.md
# Last updated: 2026-06-28
# Source: tests/tempo/clients/new_notes/create_edit_note_no_summary/script.md
# DO NOT EDIT MANUALLY - This file is regenerated from script.md

import re
import sys
from playwright.sync_api import Page, expect

from tests.tempo.clients.notes.note_helpers import UI_TIMEOUT, navigate_to_matter_page


def test_create_edit_note_no_summary(page: Page, context: dict):
    """
    Create a note via the new POV notes popup (new_notes flag ON, note_summary OFF),
    verify it appears with body content and no AI chrome, then edit the body and
    confirm the updated content is reflected on the preview card.
    """

    # The rollout.clients.new_notes flag is enabled in _setup BEFORE login (per-business
    # flag the SPA reads at app load), so the new POV notes UI is already active here.
    matter_id = context.get("created_matter_id")
    if not matter_id:
        raise ValueError("No created_matter_id in context - _setup must run first")

    # Step 0: Ensure we start on the matter detail page (idempotent — _setup left us here).
    print("  Step 0: Navigating to matter page...")
    navigate_to_matter_page(page, context, matter_id)

    if matter_id not in page.url:
        raise ValueError(
            f"Expected to be on matter page {matter_id}, but URL is {page.url}."
        )

    page.wait_for_load_state("domcontentloaded")

    # Wait for angular iframe to be present before setting up frame locators
    angular_iframe = page.locator('iframe[title="angularjs"]')
    angular_iframe.wait_for(state="visible", timeout=UI_TIMEOUT)

    # Step 1: Click the Notes tab
    # script.md Step 1 — nested iframes; Notes tab is in the inner vue iframe
    print("  Step 1: Clicking Notes tab...")
    outer_iframe = page.frame_locator('iframe[title="angularjs"]')
    inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')
    notes_tab = inner_iframe.get_by_role("tab", name="Notes")
    notes_tab.click()
    # Wait for the new-UI notes list region to render (empty-state or a card)
    inner_iframe.get_by_text("No notes found").or_(
        inner_iframe.locator('[data-qa^="NotePreviewCard-"]')
    ).first.wait_for(state="visible", timeout=5000)

    # Step 2: Click "Add note"
    # script.md Step 2 — "Add note" button lives in the OUTER angularjs iframe header
    print("  Step 2: Clicking Add note button...")
    add_note_button = outer_iframe.get_by_role("button", name="Add note")
    add_note_button.click()
    # The "New note" popup renders in the TOP-LEVEL page document (no iframe).
    # Wait for the popup title field to appear.
    title_field = page.locator('[data-qa="add-note-dialog-title"]')
    title_field.wait_for(state="visible", timeout=5000)

    # Step 3a: Type the note title
    # script.md Step 3a — popup is at top-level page, data-qa selector
    print("  Step 3a: Typing note title...")
    title_field = page.locator('[data-qa="add-note-dialog-title"]')
    title_field.click()
    page.wait_for_timeout(100)  # brief focus settle
    title_field.press_sequentially("Automation Note Title")

    # Step 3b: Type the note body
    # script.md Step 3b — contenteditable TinyMCE body at top-level page; requires keyboard.type()
    print("  Step 3b: Typing note body...")
    body_editor = page.locator('#add-note-dialog-editor_textarea')
    body_editor.click()  # focus the contenteditable
    page.wait_for_timeout(100)
    # Rich text editor (contenteditable / TinyMCE): use keyboard.type(), not fill()/press_sequentially()
    page.keyboard.type("Automation note body")

    # Step 4: Save the new note
    # script.md Step 4 — data-qa footer Save button at top-level page
    print("  Step 4: Saving the new note...")
    save_button = page.locator('[data-qa="vc-footer-Save"]')
    save_button.click()
    # Popup closes (top-level title field gone) and the new card appears in the Notes-tab list.
    # Scope to .notes-wrapper so the "Recent note" side-pane widget does NOT count.
    title_field.wait_for(state="hidden", timeout=5000)
    note_card = inner_iframe.locator('.notes-wrapper .VcNotePreviewCard')
    note_card.first.wait_for(state="visible", timeout=5000)

    # Step 5: Verify the note card appears with body content and NO AI chrome
    # script.md Step 5 — scope to .notes-wrapper (excludes "Recent note" widget) +
    # match the -body element with an anchored regex (avoids -body/card-root double-match
    # and the "Edited automation note body" substring collision).
    print("  Step 5: Verifying note card content and absence of AI chrome...")
    created_note_body = "Automation note body"
    note_card = inner_iframe.locator('.notes-wrapper .VcNotePreviewCard').filter(
        has=inner_iframe.locator(
            '[data-qa$="-body"]', has_text=re.compile(rf"^{re.escape(created_note_body)}$")
        )
    )
    expect(note_card).to_have_count(1, timeout=5000)
    expect(note_card).to_be_visible(timeout=5000)

    # No AI chrome: the card must not contain a summary/AI/generating section (note_summary OFF)
    expect(note_card.filter(has_text=re.compile(r"summary|generating", re.I))).to_have_count(0)

    # Step 6: Open the note's 3-dot menu and choose "View/ Edit"
    # script.md Step 6 — reuse the .notes-wrapper-scoped card; 3-dot trigger is found WITHIN it,
    # and the menu item is targeted by the card's dynamic id ("<cardId>-actions-edit").
    print("  Step 6: Opening 3-dot menu and clicking View/Edit...")
    actions_trigger = note_card.locator('[data-qa$="-actions-trigger"]')
    actions_trigger.click()

    # The menu item carries the same dynamic card id: "<cardId>-actions-edit".
    card_id = note_card.get_attribute("data-qa")
    edit_item = inner_iframe.locator(f'[data-qa="{card_id}-actions-edit"]')
    edit_item.wait_for(state="visible", timeout=5000)
    edit_item.click()

    # Edit popup opens at the TOP-LEVEL document, prefilled
    edit_title = page.locator('[data-qa="edit-note-dialog-title"]')
    edit_title.wait_for(state="visible", timeout=5000)

    # Step 7: Verify title and body are prefilled in the edit popup
    # script.md Step 7 — confirms title persisted even though preview card does not display it
    print("  Step 7: Verifying title and body prefill in edit popup...")
    edit_title = page.locator('[data-qa="edit-note-dialog-title"]')
    expect(edit_title).to_have_value("Automation Note Title", timeout=5000)

    edit_body = page.locator('#edit-note-dialog-editor_textarea')
    expect(edit_body).to_contain_text("Automation note body", timeout=5000)

    # Step 8: Clear the body and type new content
    # script.md Step 8 — contenteditable requires keyboard.type(); clear via Ctrl/Cmd+A + Delete
    print("  Step 8: Replacing note body with edited content...")
    edit_body = page.locator('#edit-note-dialog-editor_textarea')
    edit_body.click()  # focus
    page.wait_for_timeout(100)
    # Select-all then delete to clear the contenteditable, then type new content.
    # Use the platform select-all modifier (Cmd on macOS, Ctrl elsewhere).
    select_all = "Meta+a" if sys.platform == "darwin" else "Control+a"
    page.keyboard.press(select_all)
    page.keyboard.press("Delete")
    page.keyboard.type("Edited automation note body")

    # Step 9: Save the edit
    # script.md Step 9 — same data-qa footer Save; wait for edit popup to close
    print("  Step 9: Saving the edit...")
    edit_save_button = page.locator('[data-qa="vc-footer-Save"]')
    edit_save_button.click()
    # Edit popup closes
    edit_title.wait_for(state="hidden", timeout=5000)

    # Step 10: Verify the card reflects the new body (update outcome)
    # script.md Step 10 — scope to .notes-wrapper and match the -body element EXACTLY
    # (anchored regex), so the "Recent note" widget duplicate and the substring collision
    # with the old body are both avoided.
    print("  Step 10: Verifying updated card content...")
    edited_note_body = "Edited automation note body"
    updated_body = inner_iframe.locator('.notes-wrapper [data-qa$="-body"]').filter(
        has_text=re.compile(rf"^{re.escape(edited_note_body)}$")
    )
    expect(updated_body).to_have_count(1, timeout=5000)
    expect(updated_body).to_be_visible(timeout=5000)

    # Old body gone — scoped to .notes-wrapper and exact-matched on the -body element.
    old_body = inner_iframe.locator('.notes-wrapper [data-qa$="-body"]').filter(
        has_text=re.compile(r"^Automation note body$")
    )
    expect(old_body).to_have_count(0, timeout=5000)

    # Context saves
    context["created_note_title"] = "Automation Note Title"
    context["created_note_body"] = "Automation note body"
    context["edited_note_body"] = "Edited automation note body"

    print("  [OK] create_edit_note_no_summary completed successfully")
