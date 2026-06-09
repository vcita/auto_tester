"""Create a client through all four channels (VCITA2-14007).

Migrated from automation-js/features/steps/client-create-new-CRM.feature.
Exercises new-CRM dialog, API, livesite leave-details, and contact-form widget
creation; verifies CRM searchability for each and the email/conversation outcomes
for the two inbound channels.
"""

import time

from playwright.sync_api import Page

from tests import account_api
from tests.clients.client_create_paths.client_create_helpers import (
    assert_email_with_subject,
    crm_create_client,
    crm_search_assert,
)
from tests.clients.client_create_paths.client_create_channels import (
    assert_portal_conversation,
    livesite_leave_details,
)
from tests.online_presence.contact_form_widget.contact_form_helpers import (
    submit_contact_form,
)

THANK_YOU = "Thank you for your message"


def test_client_creation_channels(page: Page, context: dict) -> None:
    seq = int(time.time())
    business_email = context["username"]

    # 1) New-CRM dialog
    crm_create_client(page, context, "first", "last", f"test+{seq}@vmeetme.com")
    crm_search_assert(page, context, "first", "first last")
    print("  [OK] Created client via new-CRM dialog and found it in CRM")

    # 2) API
    account_api.create_client(
        context, first_name="api_first", last_name="api_last", email=f"testapi+{seq}@vmeetme.com"
    )
    crm_search_assert(page, context, "api_first", "api_first api_last")
    print("  [OK] Created client via API and found it in CRM")

    # 3) Livesite leave-details
    livesite_leave_details(
        page,
        context,
        {
            "subject": "Hi Contact Request",
            "message": "hello",
            "email": business_email,
            "first_name": "form_first",
            "last_name": "form_last",
        },
    )
    assert_email_with_subject(context, THANK_YOU)
    assert_email_with_subject(context, "Hi Contact Request")
    crm_search_assert(page, context, "form_first", "form_first form_last")
    assert_portal_conversation(page, context, "Hi Contact Request")
    print("  [OK] Livesite leave-details created client, emails delivered, CRM updated, portal conversation shown")

    # 4) Contact-form widget
    submit_contact_form(
        page,
        context,
        {
            "first_name": "widget_first",
            "last_name": "widget_last",
            "email": "widget@vmeetme.com",
            "message": "hello",
        },
    )
    # Second THANK_YOU must be a *new* email (the livesite channel already sent one),
    # so require >= 2 to avoid re-asserting the earlier message.
    assert_email_with_subject(context, THANK_YOU, min_count=2)
    assert_email_with_subject(context, "Message from widget_first widget_last")
    crm_search_assert(page, context, "widget_first", "widget_first widget_last")
    print("  [OK] Contact-form widget created client, emails delivered, CRM updated")
