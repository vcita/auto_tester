# Heal Test

Fix a failing test by following the systematic debugging and healing process.

Follow the rules in `.cursor/rules/heal.mdc` to heal this test.

---

## IMPORTANT: Always Use URLs from config.yaml

When accessing vcita during MCP exploration:
- **Login URL**: Use `https://www.vcita.com/login` (from config.yaml target.login_url)
- **NEVER** use `app.vcita.com/login` - it triggers Cloudflare blocks
- **Credentials**: Use values from config.yaml target.auth section

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
Add "## Healing Result" section to the heal request file with:
- Issue Type (Test Bug / Product Bug)
- Root Cause
- Fix Applied
- MCP Validation confirmation
- Files Updated
- Category re-run result (PASS/FAIL)

**If test remains unresolved after 5 attempts:**
Add "## Healing Result - UNRESOLVED" section with:
- Issue Type (Test Bug / Product Bug / Unknown)
- Summary of all 5 attempts
- What was tried during debugging (list each attempt)
- MCP observations from each attempt
- Patterns noticed across attempts
- **Estimation of what might be the issue** (even if unvalidated)
- Hypotheses that need further investigation
- Why the issue couldn't be resolved

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
   - **STOP the healing process**
   - Mark the heal request as **"UNRESOLVED"**
   - Document in heal request:
     - Summary of all 5 attempts
     - What was tried during debugging
     - What MCP observations revealed
     - Any patterns noticed across attempts
   - Document in failed run log:
     - Mark as "UNRESOLVED" (not "Healed")
     - Include summary of attempts
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
- [ ] changelog.md updated
- [ ] Heal request updated
- [ ] Failed run log updated
- [ ] **Category re-run to validate fix**
- [ ] If test failed again: Retried healing process (up to 5 times)
- [ ] If unresolved after 5 attempts: Documented as "UNRESOLVED" with estimation
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
