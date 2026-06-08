# Source: tests/scheduling/appointments/appointments_list/export_list/script.md
# Migrated from automation-js/features/tempo/appointments-list.feature (VCITA2-13953, scenario 2)

from playwright.sync_api import Page

from tests.scheduling.appointments.appointments_list.appointments_list_helpers import (
    assert_download_is_bookings,
    export_appointment_list,
    open_appointment_list,
)


def test_export_list(page: Page, context: dict) -> None:
    """Export the appointments list and verify a 'Bookings' file is downloaded."""
    print("  Step 1: Open the appointments list page")
    open_appointment_list(page, context)

    print("  Step 2: Open the export dialog, confirm export, capture the download")
    download = export_appointment_list(page)

    print(f"  Step 3: Verify the download is the bookings export ({download.suggested_filename!r})")
    assert_download_is_bookings(download)

    print("  [OK] appointments list exported - 'Bookings' file downloaded")
