# Heal Test

Fix a failing test by following the systematic debugging and healing process.

Follow the rules in `.cursor/rules/heal.mdc` to heal this test.

---

## IMPORTANT: Always Use URLs from config.yaml

When accessing vcita during MCP exploration:
- **Login URL**: Use **base_url + "/login"** from config.yaml (target.base_url). Never hardcode the host.
- **Credentials**: Use values from config.yaml target.auth section.
- **New test user**: Run `python main.py create_user` to create a new user in vcita and update config.

---

## STEP 1: Understand What Happened (Logs/Screenshots/Recordings)

**Follow `.cursor/rules/heal.mdc` sections:**
- **"MANDATORY FIRST STEP: Read the Changelog"** - Read changelog.md to learn from past attempts
- **"MANDATORY SECOND STEP: Screenshot AND Video Analysis"** - Analyze visual evidence

**Key actions:**
1. Locate heal request in `.cursor/heal_requests/` (format: `heal_[test_id]_[timestamp].md`)
2. Analyze screenshot and video (if available) from heal request
3. Read error message and current test files (test.py, script.md, steps.md)
4. **After processing snapshot/logs: Read the changelog** - `tests/{category}/{test_name}/changelog.md`
   - Check for any recent changes that might have caused the issue
   - Look for patterns in past healing attempts
   - Note any related fixes or modifications that could be relevant
   - **Regardless of what you find in the changelog, you MUST proceed to MCP debugging**

**Document your initial understanding** - but remember: this is just the starting point. You MUST verify with MCP.

---

## STEP 2: Research with Playwright MCP (MANDATORY)

**CRITICAL: Regardless of whether you think you understand the issue, you MUST use Playwright MCP to simulate the test and observe what actually happens.**

**IMPORTANT: Even if the changelog shows recent changes that might explain the failure, you MUST still debug the test step-by-step with MCP. The changelog provides context, but MCP observation is the only way to understand what's actually happening in the UI.**

**Follow `.cursor/rules/heal.mdc` section "MANDATORY THIRD STEP: Debug with MCP (NO BLIND FIXES!)"** for detailed guidance.

### 2.1: Prepare Browser State with `--until-test`

**BEST PRACTICE: Use `--until-test` to run the category up to (but not including) the failing test, leaving the browser in the correct state for MCP debugging.**

This ensures:
- All previous tests have run (setup, context, navigation state)
- Browser is on the correct page
- Context variables are populated
- You can immediately start debugging the failing test with MCP

**How to use:**

1. **Identify the failing test name** from the heal request or error message
   - Format is usually `Category/Test Name` (e.g., `Services/Edit Group Event`)
   - Or just the test name (e.g., `Edit Group Event`)

2. **Run the category with `--until-test`**:
   ```bash
   python main.py run --category scheduling --until-test "Services/Edit Group Event"
   ```
   Or with just the test name:
   ```bash
   python main.py run --category scheduling --until-test "Edit Group Event"
   ```

3. **The runner will:**
   - Run setup (if exists)
   - Run all tests before the specified test
   - Stop before executing the target test
   - Keep the browser open
   - Display current URL and page title
   - Wait for you to press Enter before closing

4. **Once the browser is open and ready:**
   - The browser is in the exact state it would be before the failing test
   - All context variables from previous tests are available
   - You can now use Playwright MCP to execute the test step-by-step

5. **After completing MCP debugging:**
   - **IMPORTANT: Close the browser** by pressing Enter in the terminal where the runner is waiting
   - This will finalize the video recording (if enabled) and clean up resources
   - The runner will then continue and complete the execution

**Alternative: If `--until-test` doesn't work or you need a different starting point:**
- You can manually navigate to the starting URL in MCP
- Or run the category normally and use `--keep-open` on failure
- But `--until-test` is preferred as it ensures correct state

### 2.2: Execute Test Step-by-Step with MCP

**Key requirements:**
- **This is NOT optional** - mandatory for every heal request
- **Never guess** - Always observe with MCP first
- **Think like a user** - What would they see? What would they experience?
- **Create step checklist** before starting (see heal.mdc for format)
- **Execute test steps one-by-one** using MCP
- **Verify each step visually** with snapshots
- **Document findings** - which steps worked, which failed, what you observed
- **Close the browser when done** - Press Enter in the terminal to close the browser and finalize video recording

See `.cursor/rules/heal.mdc` section "3. Step-by-Step Debugging with MCP (REQUIRED)" for complete process and checklist format.

### 2.3: Key UI Interaction Patterns (CRITICAL)

**These patterns were learned from real debugging sessions and MUST be applied when interacting with UI elements:**

1. **Hover before interacting with hidden buttons**: If buttons only appear on hover, hover over the parent element first, then wait before finding/clicking them.
2. **Use MCP to inspect DOM during interaction**: When debugging complex UI interactions, use MCP to inspect the actual DOM structure while hovering/interacting, rather than guessing from code.
3. **Use multiple class checks for button identification**: When multiple similar buttons exist, require multiple classes and explicitly exclude unwanted classes.
4. **Check for confirmation dialogs after menu actions**: After clicking menu items, a confirmation dialog may appear in a different iframe context; handle it explicitly.
5. **Use evaluate() for reliable clicking**: If Playwright's click() fails on visible elements, use `element.evaluate()` with `scrollIntoView()` and `click()` for more reliable interaction.
6. **CRITICAL: Don't update test code until MCP flow succeeds**: Complete the entire flow step-by-step with MCP before updating test code. Only code after the flow works in MCP. This ensures you understand the actual UI behavior and have verified the fix works end-to-end.

**See `.cursor/rules/heal.mdc` section "3.5. Key UI Interaction Patterns (CRITICAL)" for detailed examples and code patterns.**

---

## STEP 3: Classify the Issue

Based on MCP observations, determine the issue type.

**Follow `.cursor/rules/heal.mdc` section "2. Classify the Issue"** for classification guidance.

### 3.1: Product Bug (System Issue)

**If the failure is due to a product bug (not a test issue):**

**Follow `.cursor/rules/heal.mdc` section "Handling Product Bugs"** for complete process.

**Key actions:**
1. **HALT immediately** - Do NOT try to fix the test
2. **Inform the user** - Clearly state this is a product bug, not a test bug
3. **Document in heal request** - Mark as "Product Bug" / "System Bug" with evidence
4. **Document in failed run log** - Mark as system bug, not test bug
5. **Create bug report** in `.cursor/bug_reports/` (see heal.mdc for format)
6. **Mark test as blocked** in `_category.yaml` (see heal.mdc for format)
7. **Delete the heal request** - it's been processed

**DO NOT proceed to fix the test if it's a product bug.**

### 3.2: Test Bug/Limitation

**If the failure is due to a test issue:**

1. **Document what went wrong:**
   - Root cause (selector issue, timing issue, flow change, etc.)
   - Why the test failed
   - What MCP simulation revealed

2. **Create a plan for how the test should change:**
   - What needs to be fixed (selector, timing, flow, etc.)
   - What approach will work (based on MCP findings)
   - What files need to be updated (steps.md, script.md, test.py)

---

## STEP 4: Validate Fix with MCP (Before Code Changes)

**CRITICAL: Before fixing any code, you MUST validate the fix works end-to-end using MCP.**

**This is the MOST IMPORTANT step - you MUST complete the entire flow with MCP before updating any code files.**

1. **Navigate to starting point** in MCP browser
2. **Execute the ENTIRE test flow** with the proposed fix:
   - Use the new selectors/approach
   - Follow the new flow (if changed)
   - Verify each step works
3. **Complete the full test** - Don't stop at the fix point, run A-Z
4. **Verify the test would pass** - All steps complete successfully
5. **Only if MCP validation passes** - Proceed to update code files

**If MCP validation fails:**
- Go back to Step 2 (research with MCP)
- Understand why the fix didn't work
- Try a different approach
- Validate again with MCP

**DO NOT update code files until MCP validation passes.**

**Remember: Don't update test code until MCP flow succeeds - this is a CRITICAL rule that prevents wasted effort and ensures fixes actually work.**

---

## STEP 5: Fix Files in Correct Order

**Fix files in this order (only fix what needs fixing):**

**Follow `.cursor/rules/heal.mdc` section "4. Update script.md" and "5. Regenerate test.py"** for detailed guidance.

### 5.1: Fix steps.md (if needed)
- Only if the test goals/flow changed
- Update the human-readable steps
- Keep the same structure

### 5.2: Fix script.md (if needed)
- Update the VERIFIED PLAYWRIGHT CODE blocks
- Use the code that worked in MCP validation
- Update LOCATOR DECISION sections if selectors changed
- Document the fix in the step description
- See heal.mdc for examples of selector fixes vs flow changes

### 5.3: Fix test.py
- Copy the VERIFIED PLAYWRIGHT CODE from script.md exactly
- Add HEALED comments explaining what changed
- Never modify the verified code - copy it exactly
- See `.cursor/rules/phase3_code.mdc` for code generation rules

---

## STEP 5.5: Validate Test Adheres to Rules (BEFORE Documenting)

**CRITICAL: Before updating the changelog, you MUST validate that the fixed test code adheres to all project rules, especially navigation rules.**

### Navigation Rules (CRITICAL):

**The ONLY allowed direct navigation is:**
- ✅ Login page: **base_url + "/login"** from config (entry point, rarely used)
- ✅ Public marketing pages (entry points)

**NEVER allowed:**
- ❌ `page.reload()` or `page.refresh()` - Must use UI navigation or wait for updates
- ❌ `page.goto()` to internal URLs (e.g., `/app/dashboard`, `/app/settings/services`, `/app/clients/{id}`)
- ❌ Direct URL navigation to bypass UI flows

**Why this matters:**
- Tests must simulate real user behavior
- Direct navigation bypasses UI elements that might be broken
- Page reloads bypass the natural UI refresh flow
- If navigation is needed, use UI elements (menus, buttons, links)

### Validation Checklist:

Before proceeding to document the fix, verify:

1. **Check test.py for violations:**
   - [ ] No `page.reload()` or `page.refresh()` calls (except if explicitly documented as product bug workaround)
   - [ ] No `page.goto()` to internal URLs (only login page is acceptable)
   - [ ] All navigation uses UI elements (clicks, menus, buttons)
   - [ ] If previous test should leave browser in correct state, test verifies state instead of navigating

2. **Check script.md for violations:**
   - [ ] VERIFIED PLAYWRIGHT CODE blocks don't contain `page.reload()` or `page.goto()` to internal URLs
   - [ ] Navigation steps use UI elements, not direct URLs
   - [ ] Any navigation is documented with proper justification

3. **Check steps.md for violations:**
   - [ ] Steps describe UI navigation, not URL navigation
   - [ ] No mentions of "reload page" or "navigate to URL" (except login)

4. **If violations are found:**
   - **STOP** - Do not proceed to document the fix
   - **Fix the violations** by replacing with UI-based navigation
   - **Re-validate with MCP** if navigation approach changed
   - **Only then** proceed to document the fix

### Common Violations to Fix:

**❌ WRONG:**
```python
page.reload(wait_until="domcontentloaded")
```

**✅ RIGHT:**
```python
# Wait for list to update naturally, or navigate via UI
# If list doesn't update, this might be a product bug - document it
page.wait_for_timeout(2000)  # Wait for backend sync
# Then verify the item appears (with scrolling if needed)
```

**❌ WRONG:**
```python
page.goto(f"{base_url}/app/dashboard")  # base_url from config/context
```

**✅ RIGHT:**
```python
# If not already on dashboard, navigate via UI
if "/app/dashboard" not in page.url:
    # Navigate via sidebar/menu
    dashboard_link = page.get_by_text("Dashboard")
    dashboard_link.click()
    page.wait_for_url("**/app/dashboard**", timeout=10000)
```

**❌ WRONG:**
```python
page.goto(f"{base_url}/app/clients/{matter_id}")  # base_url from config/context
```

**✅ RIGHT:**
```python
# Verify we're already on the correct page (from previous test)
if matter_id not in page.url:
    raise ValueError(f"Expected to be on matter page {matter_id}, but URL is {page.url}")
# Or search and click if navigation is needed
```

### Exception Handling:

**If a `page.reload()` or `page.goto()` is truly necessary as a product bug workaround:**
- Document it clearly in comments as a **product bug workaround**
- Add to changelog explaining why UI navigation doesn't work
- Consider reporting as a product bug if it's a recurring issue
- Still prefer waiting for updates over reload when possible
- **Note**: This should be extremely rare - most cases can be solved with proper waiting or UI navigation

**Only proceed to STEP 6 (Document the Fix) after validation passes with zero violations (or documented product bug workarounds).**

---

## STEP 6: Document the Fix

**Follow `.cursor/rules/heal.mdc` section "6. Update changelog.md"** for changelog format and examples.

### 6.1: Update changelog.md

Add entry to `tests/{category}/{test_name}/changelog.md` following the format in heal.mdc.

**Required fields:**
- Date/time, Issue Type, Phase, Author, Reason, Error
- Root Cause (what MCP revealed)
- Fix Applied (what was changed)
- Changes (list of specific changes)
- Verified Approach (MCP validation confirmation)

### 6.2: Update Heal Request

**If test was fixed:**
1. Add "## Healing Result" section to the heal request file with:
   - Issue Type (Test Bug / Product Bug)
   - Root Cause
   - Fix Applied
   - MCP Validation confirmation
   - Files Updated
   - Category re-run result (PASS/FAIL)
2. **Update the status** in the heal request file:
   - Find the heal request file in `.cursor/heal_requests/` (format: `{test_name}_{timestamp}.md`)
   - Read the file content
   - Look for existing `**Status**: `status`` line
   - If found, replace it with `**Status**: `fixed``
   - If not found, add it after the header section (after `**Duration**` line, before `---` separator)
   - Write the updated content back to the file
   - This marks the heal request as resolved

**If test remains unresolved after 5 attempts:**
- First create and run a standalone debug script from `debug_test_skeleton.py` (see heal.mdc "Escalation: Standalone Debug Script When Stuck"); document what it revealed.
- Then add "## Healing Result - UNRESOLVED" section with:
  - Issue Type (Test Bug / Product Bug / Unknown)
  - Summary of all 5 attempts
  - What was tried during debugging (list each attempt)
  - Standalone debug script findings (if run)
  - MCP observations from each attempt
  - Patterns noticed across attempts
  - **Estimation of what might be the issue** (even if unvalidated)
  - Hypotheses that need further investigation
  - Why the issue couldn't be resolved
- **Keep status as "open"** - the `/groom_heal_requests` command will automatically mark it as "expired" if changelog has newer entries

**If product bug identified:**
1. Create bug report in `.cursor/bug_reports/`
2. **Update status** in the heal request file:
   - Find the heal request file in `.cursor/heal_requests/`
   - Update the status to `**Status**: `reported``
   - Or leave as "open" - the `/groom_heal_requests` command will automatically detect the bug report and mark as "reported"
3. Add "## Healing Result" section indicating it's a product bug

## How to Update Status in Heal Request File

When updating status, follow this pattern:

1. **Read the heal request file** from `.cursor/heal_requests/{test_name}_{timestamp}.md`
2. **Find the status line** (look for `**Status**: `status``)
3. **Update or add the status:**
   - If status line exists: Replace `**Status**: `old_status`` with `**Status**: `new_status``
   - If status line doesn't exist: Add it after the header section, before the `---` separator
4. **Write the file back**

Example status update location:
```markdown
# Heal Request: Category/Test Name

> **Generated**: 2026-01-24T10:34:43.536439
> **Test Type**: test
> **Duration**: 20496ms
**Status**: `fixed`  ← Add or update this line

---
```


### 6.3: Update Failed Run Log

**If the healing process resulted in a test fix:**
- Document in the failed run log
- Mark as "Healed" with reference to changelog entry
- Include summary of what was fixed
- Note that category was re-run and test passed

**If the test remains unresolved after 5 attempts:**
- Document in the failed run log
- Mark as "UNRESOLVED" (not "Healed")
- Include summary of all 5 attempts
- List what was tried during debugging
- **Add your estimation** of what might be the issue (even if unvalidated)
- Note any hypotheses that need further investigation
- Explain why the issue couldn't be resolved

---

## STEP 7: Validate Fix and Retry if Needed

**CRITICAL: After fixing the test, you MUST validate it works by running the category again.**

1. **Run the test category** to validate the fix:
   - Execute the full category that contains this test
   - Verify the test now passes
   - Check for any regressions in other tests

2. **If test passes**: 
   - Healing complete
   - Proceed to STEP 8 (Clean Up)

3. **If test fails again**:
   - **Restart the healing process** from STEP 1
   - Document this as attempt #2, #3, etc. in your notes
   - **Continue retrying up to 5 times** (unless you have a clear understanding of the core issue)
   - Each retry should:
     - Re-read the changelog (new entries may have been added)
     - Re-run MCP debugging (UI may have changed)
     - Try a different approach based on previous attempts
     - Document what was tried in each attempt

4. **After 5 failed attempts without clear understanding**:
   - **Create and run a standalone debug script** (see `.cursor/rules/heal.mdc` section "Escalation: Standalone Debug Script When Stuck"):
     1. Copy `debug_test_skeleton.py` to `debug_<category>_<test_name>.py`
     2. Set TARGET_URL and fill STEP_2 … STEP_N from the failing test's test.py; put the failing step in DEBUG_FOCUS
     3. Run it: `python debug_<category>_<test_name>.py` from project root
     4. Document what was observed (which step fails, UI state, any variant that worked)
   - **Then** mark the heal request as **"UNRESOLVED"**
   - Document in heal request:
     - Summary of all 5 attempts
     - What was tried during debugging
     - What the standalone debug script revealed (if run)
     - What MCP observations revealed
     - Any patterns noticed across attempts
   - Document in failed run log:
     - Mark as "UNRESOLVED" (not "Healed")
     - Include summary of attempts and debug script findings
     - **Add your estimation** of what might be the issue (even if you can't validate it)
     - Note any hypotheses that need further investigation
   - **DO NOT delete the heal request** - leave it for manual review

5. **If you have a clear understanding of the core issue** (even before 5 attempts):
   - Document your understanding
   - If it's a product bug: Follow STEP 3.1 (Product Bug handling)
   - If it requires a different approach: Document and inform the user
   - You may stop early if the issue is clearly understood but unfixable by test changes

---

## STEP 8: Clean Up

**Only proceed if test is fixed and validated:**

1. **Delete the heal request** from `.cursor/heal_requests/` (only if test is fixed)
2. **Verify the fix** - The test should pass in subsequent runs
3. **If test passes**: Healing complete ✅
4. **If test marked as UNRESOLVED**: Keep heal request for manual review

---

## Quality Checklist

**Follow `.cursor/rules/heal.mdc` section "Quality Checklist"** for complete verification list.

**Key items:**
- [ ] Screenshot/video analyzed
- [ ] Changelog was read after processing snapshot/logs (check for recent changes)
- [ ] **Used `--until-test` to prepare browser state for MCP debugging** (or manually navigated to correct state)
- [ ] MCP simulation completed (regardless of changelog findings)
- [ ] **Browser closed after MCP debugging session** (pressed Enter to finalize video and clean up)
- [ ] Issue classified correctly (Test bug vs Product bug)
- [ ] Fix validated with MCP (A-Z before code changes)
- [ ] Files fixed in correct order (steps.md -> script.md -> test.py)
- [ ] **Test code validated for rule adherence** (no `page.reload()` or `page.goto()` to internal URLs)
- [ ] changelog.md updated
- [ ] Heal request updated
- [ ] Failed run log updated
- [ ] **Category re-run to validate fix**
- [ ] If test failed again: Retried healing process (up to 5 times)
- [ ] If unresolved after 5 attempts: Created and ran debug_<category>_<test_name>.py from skeleton; documented findings; then marked UNRESOLVED with estimation
- [ ] Heal request deleted (only if test is fixed) OR marked as "UNRESOLVED"
- [ ] Fix doesn't repeat past failures

---

## Common Issue Patterns

**See `.cursor/rules/heal.mdc` section "Common Issues Found During Step-by-Step Debugging"** for detailed patterns and solutions.

**Quick reference:**
- "Element not found" → Selector changed (find new selector in MCP)
- "Timeout waiting for" → Timing/loading issue (observe loading behavior)
- "Expected X but got Y" → Logic/data issue (verify actual values in UI)
- "Navigation failed" → URL changed (check actual URL pattern)
- "Element not clickable" → Element state issue (observe state, wait for ready)

---

## Remember

**Key principles from `.cursor/rules/heal.mdc`:**
- **NEVER guess** - Always observe with MCP first
- **Think like a user** - What would they see? What would they experience?
- **Understand before fixing** - Don't just try different selectors
- **Validate before coding** - MCP validation is mandatory
- **Document everything** - Changelog, heal request, run log
