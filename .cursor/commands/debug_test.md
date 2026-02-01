# Debug Test

Run a category normally until it reaches a specific test, then run that test with a **pause (Enter) after each minor action** so you can see exactly what happens.

**Order of operations:** First ensure the target test code includes the necessary pauses; **then** start the run. Do not run until pauses are in place.

---

## Usage

**`/debug_test`** [category] [test name or id]

Examples:
- `/debug_test scheduling/appointments Appointments/_teardown` — add pauses to _teardown code, then run until _teardown with pause after each action
- `/debug_test scheduling/appointments Create Appointment` — add pauses to Create Appointment code, then run it in debug mode
- `/debug_test scheduling/events Events/Schedule Event` — add pauses, then run until Schedule Event with pauses

---

## 1. Resolve scope

**Input (from user):**
- **Category**: Path like `scheduling/appointments`, `scheduling/events`, `clients`.
- **Test**: Name or ID of the test to run in debug mode (e.g. `Appointments/_teardown`, `Create Appointment`, `Events/Schedule Event`, `_setup`).

**How to resolve:**
- **Category**: Use the path as given (e.g. `scheduling/appointments`). Must be a valid category under `tests/`.
- **Test**: Can be the test folder name (e.g. `create_appointment`), the display name from `_category.yaml` (e.g. `Create Appointment`), or a path like `Appointments/_teardown`. The runner matches by name, id, or path.

**Output:** A concrete category path, test identifier, and the target test directory (e.g. `tests/scheduling/appointments/_teardown`).

---

## 2. Add pauses into the test code (before running)

**Do this first.** Do not start the run until the target test code includes the necessary pauses.

1. **Open the target test's `test.py`** (e.g. `tests/<category>/<test_name>/test.py`).

2. **Identify logical actions** in the test:
   - Each distinct step (e.g. "Step 0", "Step 1", or each block that does one thing).
   - Or each meaningful action: a click, a fill, a wait_for, a call to a helper, etc.

3. **Insert a pause before each such action** (or between actions) using the shared pattern:
   - Call the step callback only when it is set (no-op when not in debug mode):
   ```python
   if context.get("step_callback"):
       context["step_callback"]("brief description of next action")
   ```
   - Use a short, clear message (e.g. "Step 0: navigate to dashboard", "Step 1: delete client", "click Create button").

4. **Where to add pauses:**
   - **In the test's own `test.py`:** Add a pause before each logical action or step. Do not add pauses inside `_functions` (e.g. `fn_delete_client`, `fn_delete_service`); those already accept `step_callback` from context and pause internally when run with `--debug-test`.
   - If the test only calls functions that already use `context["step_callback"]`, you may only need to add one pause before each such call (e.g. before "Delete client", before "Delete service").

5. **Keep behavior unchanged when not debugging:** The lines you add must run only when `context.get("step_callback")` is set. When the runner does not use `--debug-test`, `step_callback` is not set and the test runs as before.

6. **Confirm:** After editing, the target test should have pause points before (or between) every minor action so that when run with `--debug-test`, the user is prompted (Enter) after each step.

---

## 3. Run the runner with --debug-test

**Only after the test code includes the necessary pauses**, invoke the runner:

1. Runs the category **normally** (setup, then all tests in order) **until** it reaches the said test (excluding that test).
2. Runs **only** the said test in **debug mode**: `context["step_callback"] = step_callback_with_enter`, so every pause you added (and any inside `_functions`) will print ">>> ABOUT TO: …" and wait for Enter.
3. Stops after that test (no further tests, no teardown). Browser stays open until you press Enter.

**Command to run:**

```bash
python main.py run --category <category> --debug-test "<test>"
```

Use the resolved category path and test name/id. Examples:

```bash
python main.py run --category scheduling/appointments --debug-test "Appointments/_teardown"
python main.py run --category scheduling/appointments --debug-test "Create Appointment"
python main.py run --category scheduling/events --debug-test "Events/Schedule Event"
```

---

## 4. What happens during the run

- **Before the target test:** Setup and all previous tests run as usual (no pauses).
- **Target test:** The runner sets `context["step_callback"] = step_callback_with_enter`. Each pause you added in the test code (and any inside functions like `fn_delete_client`, `fn_delete_service`) will print ">>> ABOUT TO: …" and wait for Enter before the next action.
- **After the target test:** Execution stops. Teardown is **not** run. The browser stays open until you press Enter in the terminal.

---

## 5. Optional: run with subcategory

If the category is under a parent, use `--category` with the parent and optionally `--subcategory`, or the full category path:

```bash
python main.py run --category scheduling --subcategory appointments --debug-test "Appointments/_teardown"
python main.py run --category scheduling/appointments --debug-test "Appointments/_teardown"
```

---

## Summary

- **Slash command:** `/debug_test [category] [test]`
- **Resolve:** Category path + test name/id + target test directory.
- **First:** Open the target test's `test.py` and add pauses: before (or between) each logical action, insert `if context.get("step_callback"): context["step_callback"]("description")`. Do not run until this is done.
- **Then:** Run `python main.py run --category <category> --debug-test "<test>"`.
- **Effect:** Category runs until the given test; that test runs with pause-after-each-action (Enter); then stop and keep browser open until Enter.
