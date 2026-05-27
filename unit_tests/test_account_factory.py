import json

from src.runner import account_factory


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
