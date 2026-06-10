# Appointment With Arrival Window — Script

Source for `test.py`. UI primitives live in `schedule_appointments_ui.py`; API setup in
`schedule_appointments_api.py`.

## Test: `test_arrival_window(page, context)`

```
data     = context["schedule_appts"]
service1 = data["service"]["name"]          # "service1" (account default arrival 45m, set in _setup)
client   = data["client"]["full_name"]      # "Chuck Norris"
owner    = data["owner"]["uid"]

# In-test prerequisites: service2 + 15-minute arrival override
service2 = create_appointment_service(context, "service2", staff_uids=[owner])
set_service_arrival_window(context, service2["id"], 15)
service2_name = service2["name"]

# 1. Default resolution — account default (service1) vs service override (service2), 03:00 PM next month
m01 = schedule_appointment(page, context, service_name=service1, client_name=client,
        meeting_date="next_month", start_time="03:00 PM")
assert_meeting(page, m01, service_name=service1, client_name=client, arrival_window="3:00 pm - 3:45 pm")
m02 = schedule_appointment(page, context, service_name=service2_name, client_name=client,
        meeting_date="next_month", start_time="03:00 PM")
assert_meeting(page, m02, service_name=service2_name, client_name=client, arrival_window="3:00 pm - 3:15 pm")
wait_for_client_email_texts(context, ["Estimated arrival time:", "3:00 pm - 3:45 pm"])
wait_for_client_email_texts(context, ["Estimated arrival time:", "3:00 pm - 3:15 pm"])

# 2. In-dialog override — preset "2 hours" and "Custom 75" (1h15m), 04:00 PM next month
m11 = schedule_appointment(page, context, service_name=service1, client_name=client,
        arrival_window="2 hours", meeting_date="next_month", start_time="04:00 PM")
assert_meeting(page, m11, service_name=service1, client_name=client, arrival_window="4:00 pm - 6:00 pm")
m12 = schedule_appointment(page, context, service_name=service2_name, client_name=client,
        arrival_window="Custom 75", meeting_date="next_month", start_time="04:00 PM")
assert_meeting(page, m12, service_name=service2_name, client_name=client, arrival_window="4:00 pm - 5:15 pm")
wait_for_client_email_texts(context, ["Estimated arrival time:", "4:00 pm - 6:00 pm"])
wait_for_client_email_texts(context, ["Estimated arrival time:", "4:00 pm - 5:15 pm"])

# 3. Reschedule arrival-window only — "30 minutes" on the 2-hours appointment
reschedule_appointment(page, m11, arrival_window="30 minutes")
assert_meeting(page, m11, service_name=service1, client_name=client, arrival_window="4:00 pm - 4:30 pm")
wait_for_client_email_texts(context, ["Estimated arrival time:", "4:00 pm - 4:30 pm"])
```

## Arrival-window resolution (legacy)

| Source | Value | Window for a 3:00 PM start |
|---|---|---|
| Account default (service1, no override) | 45 min | 3:00 pm - 3:45 pm |
| Service override (service2) | 15 min | 3:00 pm - 3:15 pm |
| In-dialog preset `2 hours` (service1) | 120 min | 4:00 pm - 6:00 pm |
| In-dialog `Custom 75` (service2) | 75 min (1h 15m) | 4:00 pm - 5:15 pm |
| Reschedule `30 minutes` (service1) | 30 min | 4:00 pm - 4:30 pm |

## Verification mapping (legacy `meeting created with details` + `client gets an email`)

| Legacy column | auto_tester assertion |
|---|---|
| `arrival_window` | `.arrival-window-time` ("Estimated arrival:") contains the expected window |
| `client gets an email where text includes` | automation message-content API email contains `Estimated arrival time:` + window |
