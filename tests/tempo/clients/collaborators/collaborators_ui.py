"""UI helpers for the matter-collaborators (additional staff) test.

All collaborator UI lives in the inner Vue matter frame (``#vue_iframe_layout``)
nested inside the outer Angular frame (``iframe[title="angularjs"]``) — mirroring
``reassign_primary_staff``. Selectors below were confirmed valid against integration
by the legacy ``add-remove-staff-in-matter.feature`` baseline run.
"""

import re

from playwright.sync_api import Page, expect

UI_TIMEOUT = 5000
PAGE_READY_TIMEOUT = 5000

# Inner-frame (Vue matter view) selectors — legacy clients.js CollaboratorsDialog/Clients.
MATTER_TITLE = ".matter-name-title"
CHANGE_BTN = ".additional-staff .matter-staff__change--btn"
DIALOG_BODY = ".dialog-cmp-content"
SELECT_INPUT = "div.v-select__selections"
OPTION = ".list-item-wrapper .chip-text.list-item"
CHIP = "span.chip-text"
SAVE_BTN = ".staff__confirm"
# Collaborator avatars render as `.avatar-initials` in the matter card (initials text).
# The matter primary-staff (owner) avatar shares this class, so callers always match the
# EXACT staff initials (e.g. "SB"/"SC"), which never collide with the owner avatar.
AVATAR = ".avatar-initials"
WARNING = ".staff__comming-meeting"


def initials(name: str) -> str:
    """First letter of the first two name words (legacy getInitials, case preserved)."""
    return "".join(word[0] for word in name.split(" ")[:2] if word)


def open_matter(page: Page, client_id: str) -> None:
    app_base = page.url.split("/app/")[0] if "/app/" in page.url else None
    if not app_base:
        raise ValueError(f"Cannot infer app base URL from current page URL: {page.url}")
    page.goto(
        f"{app_base}/app/clients/{client_id}",
        wait_until="domcontentloaded",
        timeout=PAGE_READY_TIMEOUT,
    )
    expect(page).to_have_url(
        re.compile(rf"/app/clients/{re.escape(client_id)}"), timeout=PAGE_READY_TIMEOUT
    )
    page.locator('iframe[title="angularjs"]').wait_for(state="visible", timeout=PAGE_READY_TIMEOUT)


def matter_frame(page: Page):
    """Return the inner Vue matter frame and open the matter detail card."""
    outer = page.frame_locator('iframe[title="angularjs"]')
    inner = outer.frame_locator("#vue_iframe_layout")
    inner.locator(MATTER_TITLE).first.wait_for(state="visible", timeout=PAGE_READY_TIMEOUT)
    inner.locator(MATTER_TITLE).first.click()
    return inner


def open_collaborators_dialog(inner) -> None:
    change_btn = inner.locator(CHANGE_BTN).first
    change_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
    change_btn.click()
    inner.locator(DIALOG_BODY).first.wait_for(state="visible", timeout=UI_TIMEOUT)


def add_staff_in_dialog(inner, name: str) -> None:
    inner.locator(SELECT_INPUT).first.click()
    option = inner.locator(OPTION).filter(has_text=name).first
    option.wait_for(state="visible", timeout=UI_TIMEOUT)
    option.click()
    # Collapse the dropdown overlay before saving (legacy closeStaffSelectionBox).
    inner.locator(DIALOG_BODY).first.click()


def remove_staff_in_dialog(inner, name: str) -> None:
    chip = inner.locator(CHIP).filter(has_text=name).first
    chip.wait_for(state="visible", timeout=UI_TIMEOUT)
    chip.click()


def save_dialog(inner) -> None:
    save = inner.locator(SAVE_BTN).first
    save.wait_for(state="visible", timeout=UI_TIMEOUT)
    save.click()
    inner.locator(DIALOG_BODY).first.wait_for(state="hidden", timeout=PAGE_READY_TIMEOUT)


def _avatar_for(inner, name: str):
    # The avatar element's textContent is the full staff name while only the initials
    # render; `:text-is` matches the rendered (visible) initials exactly.
    return inner.locator(f'{AVATAR}:text-is("{initials(name)}")')


def assert_collaborator_shown(inner, name: str) -> None:
    expect(_avatar_for(inner, name)).to_have_count(1, timeout=UI_TIMEOUT)


def assert_collaborator_absent(inner, name: str) -> None:
    expect(_avatar_for(inner, name)).to_have_count(0, timeout=UI_TIMEOUT)


def read_removal_warning(inner) -> str:
    warning = inner.locator(WARNING).first
    warning.wait_for(state="visible", timeout=UI_TIMEOUT)
    return warning.inner_text().strip()


def assert_no_collaborators(inner, names) -> None:
    """No collaborators remain: none of the given staff initials are shown as avatars.

    Stronger than the legacy change-button text check (the control reads "Add/Remove"
    even while collaborators exist, so a substring "add" check is always true)."""
    for name in names:
        assert_collaborator_absent(inner, name)
