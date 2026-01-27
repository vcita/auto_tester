# Heal Request: scheduling/events/Events/_setup

> **Generated**: 2026-01-27T12:58:35.893540
> **Test Type**: setup
> **Duration**: 0ms
**Status**: `open`

---

## What Failed

## Config

- **base_url**: `https://www.vcita.com`
- **login_url** (derived): `https://www.vcita.com/login`
- **username**: `itzik+autotest.1769462440@vcita.com`

```
Error loading C:\Programming\auto_tester\tests\scheduling\events\_setup\test.py: ImportError: cannot import name 'ADD_MATTER_TEXT_REGEX' from 'tests._params' (C:\Programming\auto_tester\tests\_params\__init__.py)
```

**Error Type**: `ImportError`

## Test Location

Test files are located at: `C:\Programming\auto_tester\tests\scheduling\events\_setup`

- `steps.md` - Test steps and requirements
- `script.md` - Test script and flow
- `test.py` - Test implementation code
- `changelog.md` - History of previous fixes

## Context Summary

Context had 4 keys: base_url, logged_in_user, password, username

Full context is available in the test run artifacts.

---

## Next Steps

1. Review the error message above
2. Check the screenshot to see the UI state
3. Read the test files at the location above
4. Review changelog.md for previous fixes
5. Use Playwright MCP to debug if needed

See `.cursor/rules/heal.mdc` for detailed healing process.