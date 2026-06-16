# Reschedule And Cancel Appointment — Script

Source for `test.py`. UI primitives live in `schedule_appointments_ui.py`.

## Test: `test_reschedule_cancel(page, context)`

```
data    = context["schedule_appts"]
service = data["service"]["name"]      # "service1"
client  = data["client"]["full_name"]  # "Chuck Norris"

# 1. Schedule a past appointment (COMPLETED)
appt_id = schedule_appointment(
    page, context,
    service_name=service, client_name=client,
    meeting_date="previous_month", start_time="01:00 AM", end_time="05:00 AM",
)
assert_meeting(page, appt_id, service_name=service, client_name=client,
               state="COMPLETED", start_time="1:00 AM", end_time="5:00 AM")

# 2. Reschedule to next week (SCHEDULED)
reschedule_appointment(page, appt_id, new_date="next_week",
                       start_time="3:00am", end_time="4:00am")
assert_meeting(page, appt_id, service_name=service, client_name=client,
               state="SCHEDULED", start_time="3:00 AM", end_time="4:00 AM")

# 3. Cancel (CANCELLED, times unchanged)
cancel_appointment(page, appt_id)
assert_meeting(page, appt_id, service_name=service, client_name=client,
               state="CANCELLED", start_time="3:00 AM", end_time="4:00 AM")
```

## Verification mapping (legacy `meeting created with details`)

| Legacy column | auto_tester assertion |
|---|---|
| `meeting_name` | service header `div.summary-header h3` contains `service1` |
| `client_name` | `[data-qa='display-name']` contains `Chuck Norris` |
| `meeting_state` | `[data-qa='appointment-state']` == COMPLETED / SCHEDULED / CANCELLED |
| `start_time` / `end_time` | `[data-qa='appointment-date']` contains the times (case/space-insensitive) |
| reschedule applied | "Rescheduled from" note visible after submit |
