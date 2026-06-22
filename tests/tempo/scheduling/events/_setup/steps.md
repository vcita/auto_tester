# Events Setup

## Objective
Prepare the system for event scheduling tests by creating:
- A group event service for scheduling event instances
- A test client to add as an attendee

Then navigate to the Calendar page.

## Prerequisites
- **Parent (Scheduling) setup has run**: browser is on Settings > Services page; user is logged in.
- Events setup does **not** navigate to Services; it only creates the service and client, then goes to Calendar.

## Steps
1. Call: login (if not already logged in)
2. Create a group event service for testing (assume we are already on Services page)
   - Name: "Event Test Workshop {timestamp}"
   - Max attendees: 10
   - Duration: 60 minutes
   - Price: 25
   - Location: Face to face
   - After create: navigate away from Services and back (known UI issue – list does not show new service until refreshed)
   - save_to_context: event_group_service_id, event_group_service_name
3. Call: create_client
   - first_name: "Event"
   - last_name: "TestClient{timestamp}"
   - save_to_context: event_client_id, event_client_name, event_client_email
4. Navigate to Calendar page

## Expected Result
- Group event service is created and available
- Test client is created and available
- Browser is on the Calendar page
- Context contains:
  - event_group_service_id: ID of the group event service
  - event_group_service_name: Name of the group event service
  - event_client_id: ID of the test client
  - event_client_name: Full name of the test client
  - event_client_email: Email of the test client
