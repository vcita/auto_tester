# Schedule Appointments With Different Meeting States — Script

Source for `test.py`. UI primitives live in `schedule_appointments_ui.py`.

## Test: `test_meeting_states(page, context)`

```
data          = context["schedule_appts"]
service       = data["service"]["name"]          # "service1"
user_staff    = data["user_staff"]["name"]       # "user_staff"
manager_staff = data["manager_staff"]["name"]    # "optimus_prime" (API-provisioned, see note)

# 1. INVITED — new client inline + assigned existing staff + client confirmation
m1 = schedule_appointment(page, context, service_name=service,
        new_client={"first_name": "rick", "last_name": "morty", "email": f"client{data['seq']}@vmeetme.com"},
        assigned_staff=user_staff, client_confirmation=True)
assert_meeting(page, m1, service_name=service, client_name="rick morty",
               assigned_staff=user_staff, state="INVITED")

# 2. SCHEDULED — manager staff + next-month all-day
m2 = schedule_appointment(page, context, service_name=service, client_name="rick morty",
        assigned_staff=manager_staff,
        meeting_date="next_month", start_time="01:00 AM", end_time="05:00 AM", all_day=True)
assert_meeting(page, m2, service_name=service, client_name="rick morty",
               assigned_staff=manager_staff, state="SCHEDULED", meeting_date="next_month")

# 3. COMPLETED — existing client + manager staff + previous month
m3 = schedule_appointment(page, context, service_name=service, client_name="rick morty",
        assigned_staff=manager_staff, meeting_date="previous_month")
assert_meeting(page, m3, service_name=service, client_name="rick morty",
               assigned_staff=manager_staff, state="COMPLETED", meeting_date="previous_month")
```

> Product-change note: the legacy scenario created `optimus-prime` via the dialog's "create new
> staff" entry. That action now persists the appointment and navigates to the appointment page
> (it no longer creates a staff inline), so the manager staff is provisioned via the Platform API
> in `_setup` and selected through the assigned-staff dropdown — preserving every assertion.

## Verification mapping (legacy `meeting created with details`)

| Legacy column | autotester assertion |
|---|---|
| `meeting_name` | `div.summary-header h3` contains `service1` |
| `client_name` | `[data-qa='display-name']` contains `rick morty` |
| `assigned_staff` | `[data-qa='assigned-staff']` contains the (new) staff |
| `meeting_state` | `[data-qa='appointment-state']` == INVITED / SCHEDULED / COMPLETED |
| `meeting_date` | `[data-qa='appointment-date']` contains the resolved month + day 10 |
| `is_more_than_a_day` | implied by all-day SCHEDULED next-month booking (state/date asserted) |
