## 2026-06-28 — Initial creation from Confluence template
- Created from: https://myvcita.atlassian.net/wiki/spaces/Tempo/pages/4803428386/Flow+A+create_edit_note_no_summary
- Jira task: VCITA2-13033
- Flow: create_edit_note_no_summary
- Feature flags: rollout.clients.new_notes ON, note_summary OFF

## 2026-06-28 — Moved to isolated subcategory (flag-before-login fix)
- Initial focused runs failed: the new POV add-note popup never rendered (legacy dialog
  appeared instead). Root cause: `rollout.clients.new_notes` is a per-business flag the SPA
  reads at app-load time; enabling it mid-test (after login) does not take effect.
- Fix: moved the test from `clients/notes/` into a new isolated subcategory
  `clients/new_notes/` whose `_setup` enables the flag BEFORE login, then creates the matter
  via API. The legacy notes tests under `clients/notes/` keep the flag OFF on the shared account.
- test.py: removed the in-test `enable_features` call (now in `_setup` before login) and the
  unused session-recovery helper; starts on the matter page provided by `_setup`.

## 2026-06-28 — Heal: scope card assertions to the Notes tabpanel
- Focused run failed at card verification (Step 5) with a Playwright strict-mode violation:
  the note body rendered in TWO `NotePreviewCard` elements — the Notes-tab card AND the
  "Recent note" side-pane widget (`NotePreviewCard-recent`). A second fragility: matching the
  card root + its `-body` child, and substring `has_text` colliding "Automation note body" with
  "Edited automation note body".
- Fix (verified in MCP): scope card selectors to the `.notes-wrapper` container (excludes the
  Recent-note widget) and match the `[data-qa$="-body"]` element with an anchored regex
  (`^...$`). Step 6 reuses that scoped card and targets the edit menu item by the card's dynamic
  id (`<cardId>-actions-edit`) instead of `.first`. Added `to_have_count(1)` determinism guards.
- Updated script.md (Steps 4/5/6/10) and test.py to match.

## 2026-06-28 — Heal: portable select-all + validated stable
- Step 8 failed with `Unknown key: "ControlOrMeta"` (not accepted by keyboard.press() in the
  pinned Playwright version). Fixed to a platform modifier: `Meta+a` on macOS, `Control+a` elsewhere.
- Focused run: PASS (all 10 steps). Stress test: 10/10 STABLE on integration. `_category.yaml`
  stability block stamped (stable, 100%, 10 iterations, 2026-06-28).
- Confluence Section 3 (Result) filled: final test path, stress result, maintainer notes.
