# Script — set_terms

Phase 2 (HOW). Helpers in `payment_settings_api.py` / `payment_settings_ui.py`.

## Step 1 — set terms (API)
```python
set_terms_and_policies(context, "terms and policies example")
# POST /platform/v1/payment/settings {payment_settings:{terms_and_conditions_type:"text", terms_and_conditions_value:"..."}}
```

## Step 2 — API read-back
```python
get_terms_and_policies(context)  # GET payment/settings -> terms_and_conditions_value
```

## Step 3 — UI display
```python
read_terms_text(page, context)  # goto ?tab=terms-and-policies, read [data-qa=terms-and-policies-tab-text-area]
```
The settings page mounts nested frames, so the textarea is located by scanning frames.
