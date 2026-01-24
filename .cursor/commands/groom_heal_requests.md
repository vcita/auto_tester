# Groom Heal Requests

Review and manage heal request statuses, marking them appropriately and cleaning up old ones.

## Usage

```
/groom_heal_requests
```

## What It Does

1. **Reviews all heal requests** in `.cursor/heal_requests/`
2. **Determines status** for each heal request:
   - **"open"** - New heal request, not yet reviewed
   - **"fixed"** - Test has been fixed (marked in heal request or changelog shows fix)
   - **"reported"** - Bug report created for this issue
   - **"expired"** - Test has been fixed (changelog has newer entry) or marked as fixed but old
3. **Updates status** in heal request files
4. **Deletes old requests** - Removes expired/fixed requests older than 7 days

## Status Determination Logic

### "fixed"
- Heal request has "## Healing Result" section indicating test was fixed
- Contains "PASS" or "fixed" or "healed" in the healing result
- OR changelog has an entry newer than the heal request generation date (indicating test was fixed)

### "reported"
- A bug report exists in `.cursor/bug_reports/` that references this test/category
- Bug report date is on or after the heal request generation date

### "expired"
- Changelog has an entry newer than the heal request generation date
- OR heal request has "## Healing Result" section but not marked as fixed

### "open"
- Default status for new heal requests
- No healing result, no newer changelog, no bug report

## Execution Instructions

When the user invokes `/groom_heal_requests`, you MUST:

### Step 1: List All Heal Requests

1. **Read all heal request files** from `.cursor/heal_requests/*.md`
2. **For each heal request file**, extract:
   - File path
   - Generated date (from `**Generated**: YYYY-MM-DDTHH:MM:SS` line)
   - Category and test name (from `# Heal Request: Category/Test Name` header)
   - Current status (from `**Status**: `status`` line, if present)
   - Whether it has "## Healing Result" section
   - Whether it contains "PASS", "fixed", or "healed" in the healing result

### Step 2: Determine Status for Each Request

For each heal request, determine the appropriate status:

1. **Check if marked as fixed:**
   - Look for "## Healing Result" section
   - Check if it contains "PASS", "fixed", or "healed" (case-insensitive)
   - If yes → status = "fixed"

2. **Check for bug report:**
   - Look in `.cursor/bug_reports/` for files that mention the test name or category
   - Check if bug report date (from filename or content) is on or after heal request generation date
   - If yes → status = "reported"

3. **Check changelog for newer entries:**
   - Find the test's changelog: `tests/{category}/{test_name}/changelog.md`
   - Handle name variations (spaces vs underscores, case differences)
   - Check subcategories: `tests/{category}/{subcategory}/{test_name}/changelog.md`
   - Parse the most recent changelog entry date (format: `## YYYY-MM-DD HH:MM:SS`)
   - If changelog date > heal request generation date → status = "expired"

4. **Check for healing result without fix:**
   - If has "## Healing Result" section but not marked as fixed → status = "expired"

5. **Default:**
   - If none of the above → status = "open"

### Step 3: Update Status in Files

For each heal request where status needs to change:

1. **Read the heal request file**
2. **Find or add the status line:**
   - Look for existing `**Status**: `status`` line
   - If found, replace it with new status
   - If not found, add it after the header section (after `**Duration**` line, before `---` separator)
3. **Write the updated content back to the file**

Format for status line:
```markdown
**Status**: `open`
```
or
```markdown
**Status**: `fixed`
```
etc.

### Step 4: Delete Old Requests

For each heal request with status "expired" or "fixed":

1. **Check the generation date**
2. **If generation date is more than 7 days ago:**
   - Delete the file
   - Track it in the deletion list

### Step 5: Display Summary

Create a summary showing:
- Total heal requests processed
- Status breakdown (count for each: open, fixed, reported, expired)
- Number of status updates made
- Number of deletions made
- Any errors encountered (with file names)

## Example Status Update

**Before:**
```markdown
# Heal Request: Services/edit_group_event

> **Generated**: 2026-01-24T10:34:43.536439
> **Test Type**: test
> **Duration**: 20496ms

---
```

**After (if status should be "fixed"):**
```markdown
# Heal Request: Services/edit_group_event

> **Generated**: 2026-01-24T10:34:43.536439
> **Test Type**: test
> **Duration**: 20496ms
**Status**: `fixed`

---
```

## Important Notes

- This command is **safe to run multiple times** - it's idempotent
- Status updates are written back to the heal request files
- Deletions are permanent - old expired/fixed requests are removed
- Handle test name variations carefully (spaces, underscores, case)
- When checking changelogs, also check subcategory paths
- Be careful with date parsing - handle various formats gracefully
- If a file can't be parsed, log the error but continue with other files

## Integration with Heal Process

- New heal requests are created with status "open"
- When `/heal_test` completes successfully, it should update the heal request status to "fixed"
- When `/heal_test` identifies a product bug and creates a bug report, mark status as "reported"
- The grooming process automatically detects when tests are fixed via changelog entries
