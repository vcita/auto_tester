# Implement Test

Build a complete test following the 3-phase methodology.

Follow the rules in .cursor/rules/build.mdc to implement this test.

---

## IMPORTANT: Always Use URLs from config.yaml

When accessing vcita during MCP exploration:
- **Login URL**: Use `https://www.vcita.com/login` (from config.yaml target.login_url)
- **NEVER** use `app.vcita.com/login` - it triggers Cloudflare blocks
- **Credentials**: Use values from config.yaml target.auth section

---

## PHASE 1: Create steps.md

Follow .cursor/rules/phase1_steps.mdc

- Check tests/_functions/_functions.yaml for existing functions to reuse
- Research the feature at support.vcita.com
- Write human-readable steps describing WHAT to do

## PHASE 2: Create script.md via MCP Exploration

Follow .cursor/rules/phase2_script.mdc

- Use Playwright MCP to explore and validate each step
- Document LOCATOR DECISION tables for every interactive element
- Record VERIFIED PLAYWRIGHT CODE from MCP tool output

## PHASE 3: Generate test.py

Follow .cursor/rules/phase3_code.mdc

- Copy VERIFIED PLAYWRIGHT CODE exactly from script.md
- Never modify or improve the verified locators

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

## PHASE 5: Update changelog.md
