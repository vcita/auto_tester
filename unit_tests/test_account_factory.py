import json

import pytest

from src.runner import account_factory


class _FakeErrorResponse:
    ok = False

    def __init__(self, status_code: int, body, text: str = ""):
        self.status_code = status_code
        self._body = body
        self.text = text

    def json(self):
        if self._body is None:
            raise ValueError("no json body")
        return self._body


def test_handle_create_error_validation_403_fails_fast():
    resp = _FakeErrorResponse(
        403,
        {"errors": {"business_name": ["contains invalid term"]}},
        text='{"errors":{"business_name":["contains invalid term"]}}',
    )

    with pytest.raises(account_factory.AccountCreationError) as exc_info:
        account_factory._handle_create_error(resp, "invoices")

    message = str(exc_info.value)
    assert "invalid request" in message
    assert "transient forbidden" not in message
    # A permanent validation error must not be retried as a transient throttle.
    assert account_factory._is_retryable_create_error(exc_info.value) is False


def test_handle_create_error_plain_403_is_transient():
    resp = _FakeErrorResponse(403, {"message": "rate limited"}, text="rate limited")

    with pytest.raises(account_factory.AccountCreationError) as exc_info:
        account_factory._handle_create_error(resp, "invoices")

    message = str(exc_info.value)
    assert "transient forbidden" in message
    assert account_factory._is_retryable_create_error(exc_info.value) is True


def test_build_auto_email_uses_new_template():
    email = account_factory.build_auto_email("payments", 1778566207)

    assert email == "auto.payments.1778566207@vcita.com"
    assert account_factory.AUTO_EMAIL_PATTERN.match(email)


def test_parse_email_category_supports_current_format():
    assert account_factory.parse_email_category("auto.payments.1778566207@vcita.com") == "payments"


def test_build_auto_email_sanitizes_category_segment():
    email = account_factory.build_auto_email("eu_strict_invoices", 1778566207)

    assert email == "auto.eu-strict-invoices.1778566207@vcita.com"
    assert account_factory.AUTO_EMAIL_PATTERN.match(email)


def test_create_account_posts_admin_payload_for_platinum(monkeypatch):
    posted = {}
    recorded_emails = []

    class FakeResponse:
        ok = True
        status_code = 200
        text = ""

        def json(self):
            return {
                "data": {
                    "pivot_uid": "biz-123",
                    "api_token": "api-token-123",
                    "user_id": "user-123",
                }
            }

    class FakeLedger:
        def record_created(self, email):
            recorded_emails.append(email)

    def fake_post(url, json, headers, timeout):
        # create_account fires a follow-up POST (timezone) after the create call;
        # capture only the account-creation request so the assertions below are
        # not clobbered by the later request's payload.
        if url.endswith("/admin/users/"):
            posted["url"] = url
            posted["json"] = json
            posted["headers"] = headers
            posted["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(account_factory.time, "time", lambda: 1778566207)
    monkeypatch.setattr(account_factory.requests, "post", fake_post)
    monkeypatch.setattr(account_factory, "AccountLedger", FakeLedger)

    account = account_factory.create_account(
        "https://api.example.com/", "admin-token", "directory-123", "payments"
    )

    options = json.loads(posted["json"]["options"])

    assert posted["url"] == "https://api.example.com/admin/users/"
    assert posted["headers"] == {"Authorization": "Admin admin-token"}
    assert posted["json"]["generate_api_token"] is True
    assert options["email"] == "auto.payments.1778566207@vcita.com"
    assert options["business_name"] == "Auto_payments_1778566207"
    assert options["directory_id"] == "directory-123"
    assert options["package_subscription_id"] == account_factory.PLATINUM_PACKAGE_SUBSCRIPTION_ID
    assert recorded_emails == ["auto.payments.1778566207@vcita.com"]
    assert account["pivot_uid"] == "biz-123"
    assert account["auth_token"] == "api-token-123"
    assert account["user_id"] == "user-123"


def test_update_account_country_posts_nested_business_payload(monkeypatch):
    posted = {}

    class FakeResponse:
        ok = True
        status_code = 200
        text = ""

    def fake_post(url, json, headers, timeout):
        posted["url"] = url
        posted["json"] = json
        posted["headers"] = headers
        posted["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(account_factory.requests, "post", fake_post)

    account_factory.update_account_country(
        "https://api.example.com/", "admin-token", "biz-123", "Italy"
    )

    assert posted["url"] == "https://api.example.com/platform/v1/businesses/biz-123"
    assert posted["headers"] == {"Authorization": "Admin admin-token"}
    assert posted["json"] == {
        "business": {
            "business": {
                "country_name": "Italy",
            },
        },
    }
