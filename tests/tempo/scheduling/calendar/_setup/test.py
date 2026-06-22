import re
import time
from playwright.sync_api import Page, expect

from tests._functions.login.test import fn_login
from tests.tempo.scheduling.appointments.appointment_helpers import open_calendar_page
from tests.tempo.scheduling.calendar.calendar_api import (
    create_client,
    create_platform_staff,
    create_service,
    unique_email,
)


def setup_calendar(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not username or not password:
        raise ValueError("username and password must exist in context")

    if "logged_in_user" not in context:
        print("  Setup Step 1: Logging in...")
        fn_login(page, context, username=username, password=password)

    timestamp = int(time.time())
    print("  Setup Step 2: Creating Calendar client via API...")
    client = create_client(context, "Chuck", "Norris", unique_email("test23"))
    context["calendar_client"] = client
    context["created_client_name"] = client["full_name"]
    context["created_client_id"] = client.get("id") or client.get("uid")
    context["created_client_email"] = client.get("email")

    print("  Setup Step 3: Creating Calendar services via API...")
    service_specs = {
        "service1": {"name": f"service1-{timestamp}", "duration": 60, "service_type": "appointment"},
        "service2": {"name": f"service2-{timestamp}", "duration": 90, "service_type": "appointment"},
        "service3": {"name": f"service3-{timestamp}", "duration": 15, "service_type": "appointment"},
        "event1": {"name": f"event1-{timestamp}", "duration": 60, "service_type": "event"},
    }
    services = {}
    for alias, spec in service_specs.items():
        services[alias] = create_service(
            context,
            name=spec["name"],
            duration=spec["duration"],
            service_type=spec["service_type"],
        )
    context["calendar_services"] = services

    print("  Setup Step 4: Creating Staff1 via Platform API...")
    staff = create_platform_staff(context, "Staff1", unique_email("staff"), "user")
    context["calendar_staff"] = [staff]

    print("  Setup Step 5: Opening Calendar...")
    open_calendar_page(page)
    expect(page).to_have_url(re.compile(r".*/app/calendar.*"), timeout=5_000)
    print("  [OK] Calendar setup complete")
