# Implement Test

Build a complete test following the 3-phase methodology.

Follow the rules in .cursor/rules/build.mdc to implement this test.

---

## IMPORTANT: Always Use URLs from config.yaml

When accessing vcita during MCP exploration:
- **Login URL**: Use **base_url + "/login"** from config.yaml (target.base_url). Never hardcode the host.
- **Credentials**: Use values from config.yaml target.auth section.
- **New test user**: Run `python main.py create_user` to create a new user in vcita and update config.

---

## PHASE 1: Create steps.md

Follow .cursor/rules/phase1_steps.mdc

- Check tests/_functions/_functions.yaml for existing functions to reuse
- Research the feature at the vcita support / knowledge center
- Write human-readable steps describing WHAT to do

## PHASE 2: Create script.md via MCP Exploration

Follow .cursor/rules/phase2_script.mdc

- Use Playwright MCP to explore and validate each step
- Document LOCATOR DECISION tables for every interactive element
- Record VERIFIED PLAYWRIGHT CODE from MCP tool output

### Key UI Interaction Patterns (CRITICAL)

**These patterns were learned from real debugging sessions and MUST be applied when interacting with UI elements:**

1. **Hover before interacting with hidden buttons**: If buttons only appear on hover, hover over the parent element first, then wait before finding/clicking them.
2. **Use MCP to inspect DOM during interaction**: When debugging complex UI interactions, use MCP to inspect the actual DOM structure while hovering/interacting, rather than guessing from code.
3. **Use multiple class checks for button identification**: When multiple similar buttons exist, require multiple classes and explicitly exclude unwanted classes.
4. **Check for confirmation dialogs after menu actions**: After clicking menu items, a confirmation dialog may appear in a different iframe context; handle it explicitly.
5. **Use evaluate() for reliable clicking**: If Playwright's click() fails on visible elements, use `element.evaluate()` with `scrollIntoView()` and `click()` for more reliable interaction.
6. **CRITICAL: Don't update test code until MCP flow succeeds**: Complete the entire flow step-by-step with MCP before updating script.md or test.py. Only code after the flow works in MCP. This ensures you understand the actual UI behavior and have verified the approach works end-to-end.
7. **Matter entity agnosticism**: Do not hardcode matter entity labels (e.g. "Properties", "Clients", "Add property", "Delete properties?"). Use regex or positional selectors so tests work across verticals (clients, properties, patients, students, pets). See `.cursor/rules/project.mdc` § Matter Entity Name Agnosticism.

**See `.cursor/rules/build.mdc` section "Key UI Interaction Patterns (CRITICAL)" for detailed examples and code patterns.**

## PHASE 3: Generate test.py

Follow .cursor/rules/phase3_code.mdc

- Copy VERIFIED PLAYWRIGHT CODE exactly from script.md
- Never modify or improve the verified locators

**CRITICAL: Only generate test.py AFTER you've completed the entire flow with MCP and verified it works end-to-end. Don't update test code until MCP flow succeeds.**

---

## PHASE 3.5: Validate Test Adheres to Rules (BEFORE Running)

**CRITICAL: Before running the test, you MUST validate that the test code adheres to all project rules, especially navigation rules.**

**This validation MUST happen AFTER generating test.py but BEFORE running the test.**

### Navigation Rules (CRITICAL):

**The ONLY allowed direct navigation is:**
- ✅ Login page: **base_url + "/login"** from config (entry point, rarely used - only in setup/login functions)
- ✅ Public marketing pages (entry points)

**NEVER allowed in regular tests:**
- ❌ `page.reload()` or `page.refresh()` - Must use UI navigation or wait for updates
- ❌ `page.goto()` to internal URLs (e.g., `/app/dashboard`, `/app/settings/services`, `/app/clients/{id}`)
- ❌ Direct URL navigation to bypass UI flows

**Why this matters:**
- Tests must simulate real user behavior
- Direct navigation bypasses UI elements that might be broken
- Page reloads bypass the natural UI refresh flow
- If navigation is needed, use UI elements (menus, buttons, links)

**Reference rules:**
- See `.cursor/rules/project.mdc` section "Real User Actions Rule (CRITICAL)"
- See `.cursor/rules/build.mdc` section "CRITICAL: No Fallbacks or Alternative Flows"

### Validation Checklist:

**Before proceeding to run the test, verify ALL THREE files (test.py, script.md, steps.md):**

1. **Check test.py for violations:**
   ```bash
   # Search for page.reload or page.refresh
   grep -n "page\.reload\|page\.refresh" tests/{category}/{test_name}/test.py
   
   # Search for page.goto to internal URLs (exclude login)
   grep -n "page\.goto" tests/{category}/{test_name}/test.py | grep -v "login"
   ```
   - [ ] No `page.reload()` or `page.refresh()` calls (except if explicitly documented as product bug workaround)
   - [ ] No `page.goto()` to internal URLs (only login page, i.e. base_url + "/login" from config, is acceptable)
   - [ ] All navigation uses UI elements (clicks, menus, buttons)
   - [ ] If previous test should leave browser in correct state, test verifies state instead of navigating

2. **Check script.md for violations:**
   ```bash
   # Search for page.reload or page.refresh in script.md
   grep -n "page\.reload\|page\.refresh" tests/{category}/{test_name}/script.md
   
   # Search for page.goto to internal URLs
   grep -n "page\.goto" tests/{category}/{test_name}/script.md | grep -v "login"
   ```
   - [ ] VERIFIED PLAYWRIGHT CODE blocks don't contain `page.reload()` or `page.goto()` to internal URLs
   - [ ] Navigation steps use UI elements, not direct URLs
   - [ ] Any navigation is documented with proper justification

3. **Check steps.md for violations:**
   ```bash
   # Search for mentions of reload or direct URL navigation
   grep -n -i "reload\|refresh\|navigate to url\|page\.goto" tests/{category}/{test_name}/steps.md | grep -v "login"
   ```
   - [ ] Steps describe UI navigation, not URL navigation
   - [ ] No mentions of "reload page" or "navigate to URL" (except login entry point)

4. **If violations are found:**
   - **STOP immediately** - Do NOT proceed to run the test
   - **Document the violations** - List which file(s) and line(s) have violations
   - **Fix the violations** by replacing with UI-based navigation:
     - Replace `page.reload()` with waiting for updates or UI-based refresh
     - Replace `page.goto()` with UI navigation (check current state, navigate via sidebar/menu if needed)
   - **Re-validate with MCP** if navigation approach changed significantly
   - **Re-run this validation step** - Check again for violations
   - **Only after all violations are fixed** - Proceed to PHASE 4 (Run and Validate)

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
page.goto("<some_host>/app/dashboard")  # never hardcode host; use UI navigation or base_url from config
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

**Only proceed to PHASE 4 (Run and Validate) after validation passes with zero violations (or documented product bug workarounds).**

---

## PHASE 4: Run and Validate

**ALWAYS use the runner to execute tests. Category is the atomic test unit.**

```bash
python main.py run --category <category_name>
```

- The runner handles captcha bypass, timeouts, video recording, and screenshots
- Fix any failures until the category passes
- On failure, check:
  - Console output for error messages
  - Screenshots in `_runs/<run_id>/` folder
  - Video recordings for visual debugging

**IMPORTANT: If you made any fixes during this phase (e.g., fixed selectors, timing issues, navigation), you MUST re-run PHASE 3.5 (Validate Test Adheres to Rules) before proceeding to PHASE 5.**

---

## PHASE 5: Update changelog.md

---

## CRITICAL: Continue Until Complete - Don't Stop Unless You Don't Know How to Continue

**When implementing tests, you MUST continue working through all phases until completion. Do NOT stop unless you genuinely don't know how to proceed.**

**This is a CRITICAL instruction: Continue the work without stopping unless you run into a wall and don't know how to continue.**

### Why:
- Tests are only useful when fully implemented and validated
- Partial implementations create technical debt
- Stopping mid-way requires context switching and re-familiarization
- Complete implementations provide immediate value

### When to Continue:
- ✅ You know the next step but it's tedious - CONTINUE
- ✅ You've done similar work before - CONTINUE
- ✅ The pattern is clear from previous tests - CONTINUE
- ✅ You need to explore more with MCP - CONTINUE
- ✅ You need to generate more files - CONTINUE
- ✅ You're implementing multiple tests in a category - CONTINUE through all of them

### When You Can Stop:
- ❌ You encounter a genuine blocker with no clear path forward
- ❌ You need information only the user can provide (credentials, decisions, etc.)
- ❌ You discover a product bug that needs user decision on how to proceed
- ❌ You've completed ALL phases for ALL tests in the category

### Implementation Checklist:
Before stopping, verify you've completed:
- [ ] All steps.md files created for all tests
- [ ] All script.md files created with verified code from MCP exploration
- [ ] All test.py files generated from script.md
- [ ] PHASE 3.5 validation completed for all tests
- [ ] Tests run and pass (PHASE 4)
- [ ] Changelog.md files updated (PHASE 5)

**If any item is incomplete and you know how to do it, CONTINUE working. Don't ask for permission - just continue.**
