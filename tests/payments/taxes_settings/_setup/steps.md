# Taxes Settings Setup - Steps

## Objective
Log in to the isolated account so the Taxes settings tests start from a clean, predictable taxes list.

## Prerequisites
- Runner created an isolated account (default US / USD).
- `context["username"]`, `context["password"]`, `context["auto_account"]`, and `context["api_base_url"]` are available.

## Steps
1. Log in to the isolated account.

## Expected Result
- The isolated account is logged in and the dashboard is ready.
- The account has no taxes configured yet, so list assertions are deterministic.
