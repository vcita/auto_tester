"""Setup for the coupons subcategory.

Logs in to the isolated account, then provisions (via API) the prerequisites the
legacy coupons.feature creates in its Background: three paid ("suggest to pay")
$100 appointment services, one client, and one future appointment per service so
each carries a NOT YET DUE payment request.
"""

from concurrent.futures import ThreadPoolExecutor

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.payments.coupons.coupons_api import (
    create_appointment,
    create_client,
    create_paid_service,
    unique_email,
)

SERVICE_ALIASES = ["appointment_1", "appointment_2", "appointment_3"]
CLIENT_FIRST_NAME = "first"
CLIENT_LAST_NAME = "last"


def setup_coupons(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 2: Create 3 paid ($100) appointment services via API")
    services = {
        alias: create_paid_service(context, name=f"{alias}-{unique_email('s').split('@')[0]}")
        for alias in SERVICE_ALIASES
    }
    context["coupon_services"] = services

    print("  Setup Step 3: Create client via API")
    client = create_client(context, CLIENT_FIRST_NAME, CLIENT_LAST_NAME, unique_email("test"))
    context["coupon_client"] = client
    context["created_client_name"] = client["full_name"]

    # Bookings are the slowest setup step (one heavy scheduling POST each). They
    # can't all run in parallel: the first booking for a brand-new client also
    # creates that client's conversation record, and concurrent bookings race on
    # that creation (server 422). So the first booking is issued sequentially to
    # establish the conversation, then the remaining (independent) ones in parallel.
    print("  Setup Step 4: Schedule one future appointment per service via API")
    first_alias, *rest_aliases = SERVICE_ALIASES
    bookings = {first_alias: create_appointment(context, services[first_alias], client, days_ahead=10)["id"]}
    with ThreadPoolExecutor(max_workers=len(rest_aliases)) as pool:
        for alias, booking_id in pool.map(
            lambda item: (
                item[1],
                create_appointment(context, services[item[1]], client, days_ahead=11 + item[0])["id"],
            ),
            enumerate(rest_aliases),
        ):
            bookings[alias] = booking_id
    context["coupon_bookings"] = bookings

    print(f"  [OK] Coupons setup complete - {len(bookings)} appointments ready with NOT YET DUE payment requests")
