# Schedule Appointment With Additional Recipients — Script

Source for `test.py`. UI primitives live in `schedule_appointments_ui.py`.

## Test: `test_additional_recipients(page, context)`

```
data      = context["schedule_appts"]
service   = data["service"]["name"]      # "service1"
client    = data["client"]["full_name"]  # "Chuck Norris"
recipient = f"test2+{data['seq']}@vmeetme.com"

# 1. Typed recipient (trailing comma commits the chip)
meeting1 = schedule_appointment(page, context, service_name=service, client_name=client,
                                additional_recipients=f"{recipient},")
assert_meeting(page, meeting1, service_name=service, client_name=client,
               additional_recipients=recipient)

# 2. Recipient chosen "from list"
meeting2 = schedule_appointment(page, context, service_name=service, client_name=client,
                                additional_recipients="from list")
assert_meeting(page, meeting2, service_name=service, client_name=client,
               additional_recipients=recipient)
```

## Verification mapping (legacy `meeting created with details`)

| Legacy column | autotester assertion |
|---|---|
| `meeting_name` | `div.summary-header h3` contains `service1` |
| `client_name` | `[data-qa='display-name']` contains `Chuck Norris` |
| `additional_recipients` | `[data-qa='additional-recipients']` contains `test2+<seq>@vmeetme.com` |
