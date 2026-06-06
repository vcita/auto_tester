"""Quick-actions widget UI helpers for the quick_actions_widget migration (VCITA2-13863).

The widget renders on the top-level POV dashboard page (verified live: 6
`.quick-action-item`, 1 `.quick-actions-widget`, 1 edit button at frame `''`).
Clicking the client action opens the Angular new-client dialog inside
`iframe[title="angularjs"]`.
"""

import time

from playwright.sync_api import Page, expect

UI_TIMEOUT = 5_000

WIDGET = ".quick-actions-widget"
ACTION_ITEM = ".quick-action-item"
EDIT_BUTTON = "[data-qa='edit-button']"
EDIT_MODAL = "[data-qa='edit-quick-actions-modal']"
DRAGGABLE_LIST = "[data-qa='vc-draggable-list']"
SAVE_BUTTON = "[data-qa='vc-footer-Save']"
CANCEL_BUTTON = "[data-qa='vc-footer-Cancel']"
ERROR_ALERT = "[data-qa='vc-alert']"
NEW_CLIENT_DIALOG = "md-dialog.new-client-dialog-component"


def _angular_frame(page: Page):
    return page.frame_locator('iframe[title="angularjs"]')


def open_dashboard(page: Page) -> None:
    app_base = page.url.split("/app/")[0]
    page.goto(f"{app_base}/app/dashboard", wait_until="domcontentloaded", timeout=15_000)
    page.locator(WIDGET).first.wait_for(state="visible", timeout=UI_TIMEOUT)


def displayed_actions(page: Page) -> list[str]:
    page.locator(WIDGET).first.wait_for(state="visible", timeout=UI_TIMEOUT)
    items = page.locator(ACTION_ITEM)
    items.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    names = []
    for i in range(items.count()):
        data_name = items.nth(i).get_attribute("data-name") or ""
        names.append(data_name.replace("item-", ""))
    return names


def assert_actions(page: Page, expected: list[str]) -> None:
    # The widget re-renders lazily after a save; poll until the expected set shows.
    deadline = time.monotonic() + UI_TIMEOUT / 1000
    actual: list[str] = []
    while time.monotonic() < deadline:
        actual = displayed_actions(page)
        if all(name in actual for name in expected):
            return
        time.sleep(0.2)
    missing = [name for name in expected if name not in actual]
    raise AssertionError(f"Quick actions missing {missing}; displayed={actual}")


def assert_actions_in_order(page: Page, ordered_csv: str) -> None:
    deadline = time.monotonic() + UI_TIMEOUT / 1000
    actual = ""
    while time.monotonic() < deadline:
        actual = ",".join(displayed_actions(page))
        if ordered_csv in actual:
            return
        time.sleep(0.2)
    raise AssertionError(f"Expected order {ordered_csv!r} within {actual!r}")


def click_action(page: Page, name: str) -> None:
    page.locator(f'{ACTION_ITEM}[data-name="item-{name}"]').first.click()


def assert_new_client_modal(page: Page) -> None:
    dialog = _angular_frame(page).locator(NEW_CLIENT_DIALOG)
    expect(dialog.first).to_be_visible(timeout=UI_TIMEOUT)


# --- Edit modal -----------------------------------------------------------

def _checkbox(page: Page, name: str):
    """The native (visually hidden) Vuetify checkbox input for an action."""
    return page.locator(f"{DRAGGABLE_LIST} [role='checkbox'][data-qa='item-{name}']").first


def open_edit_modal(page: Page) -> None:
    page.locator(WIDGET).first.wait_for(state="visible", timeout=UI_TIMEOUT)
    page.locator(WIDGET).first.hover()
    page.locator(EDIT_BUTTON).first.click()
    page.locator(EDIT_MODAL).first.wait_for(state="visible", timeout=UI_TIMEOUT)
    # The list loads its saved checked-state lazily; wait for it before toggling
    # so we never save a half-loaded selection (at least one action is always on).
    page.locator(f"{DRAGGABLE_LIST} [role='checkbox'][aria-checked='true']").first.wait_for(
        state="attached", timeout=UI_TIMEOUT
    )


def _set_checkbox(page: Page, name: str, checked: bool) -> None:
    cb = _checkbox(page, name)
    cb.wait_for(state="attached", timeout=UI_TIMEOUT)
    if (cb.get_attribute("aria-checked") == "true") == checked:
        return
    # The native <input> is visually hidden; click its Vuetify wrapper instead.
    cb.locator("xpath=..").click()
    expect(cb).to_have_attribute("aria-checked", "true" if checked else "false", timeout=UI_TIMEOUT)


def save_actions(page: Page) -> None:
    page.locator(SAVE_BUTTON).first.click()
    page.locator(EDIT_MODAL).first.wait_for(state="hidden", timeout=UI_TIMEOUT)


def remove_actions(page: Page, names: list[str]) -> None:
    open_edit_modal(page)
    for name in names:
        _set_checkbox(page, name, False)
    save_actions(page)


def add_actions(page: Page, names: list[str]) -> None:
    open_edit_modal(page)
    for name in names:
        _set_checkbox(page, name, True)
    save_actions(page)


def _list_item(page: Page, name: str):
    return _checkbox(page, name).locator(
        'xpath=ancestor::div[contains(@class,"list-group-item")]'
    ).first


def reorder_actions(page: Page, source: str, target: str) -> None:
    """Drag ``source`` above ``target`` in the edit modal (SortableJS list)."""
    open_edit_modal(page)
    handle = _list_item(page, source).locator("[data-qa*='VcIcon']").first
    target_item = _list_item(page, target)
    handle.scroll_into_view_if_needed()
    src = handle.bounding_box()
    tgt = target_item.bounding_box()
    src_x, src_y = src["x"] + src["width"] / 2, src["y"] + src["height"] / 2
    tgt_x = tgt["x"] + tgt["width"] / 2
    drop_y = tgt["y"] + 4  # just inside the target's top -> insert before it

    page.mouse.move(src_x, src_y)
    page.mouse.down()
    page.wait_for_timeout(150)
    page.mouse.move(src_x, src_y - 12, steps=5)  # nudge to start the drag
    page.wait_for_timeout(120)
    page.mouse.move(tgt_x, drop_y, steps=20)  # travel to the target
    page.wait_for_timeout(120)
    page.mouse.move(tgt_x, drop_y - 2, steps=4)  # settle past the insert line
    page.wait_for_timeout(120)
    page.mouse.up()
    save_actions(page)


def _toggle_all(page: Page, checked: bool) -> None:
    # Collect names first: toggling re-sorts the list, so index-based iteration
    # while toggling would skip rows.
    checkboxes = page.locator(f"{DRAGGABLE_LIST} [role='checkbox']")
    names = [
        (checkboxes.nth(i).get_attribute("data-qa") or "").replace("item-", "")
        for i in range(checkboxes.count())
    ]
    for name in filter(None, names):
        _set_checkbox(page, name, checked)


def save_all_actions_expecting_error(page: Page, checked: bool) -> None:
    """Open the modal, toggle every action to ``checked``, save, and assert the
    validation error keeps the modal open; then cancel.

    Stronger than the legacy presence-only check: an invalid save must NOT close
    the modal (a valid save does), and the alert must be visible.
    """
    open_edit_modal(page)
    _toggle_all(page, checked)
    page.locator(SAVE_BUTTON).first.click()
    expect(page.locator(EDIT_MODAL).first).to_be_visible(timeout=UI_TIMEOUT)
    expect(page.locator(ERROR_ALERT).first).to_be_visible(timeout=UI_TIMEOUT)
    page.locator(CANCEL_BUTTON).first.click()
    page.locator(EDIT_MODAL).first.wait_for(state="hidden", timeout=UI_TIMEOUT)
