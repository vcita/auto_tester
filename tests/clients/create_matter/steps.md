# Create Matter via Quick Actions

> **Type**: Test
> **Status**: Verified with Playwright MCP
> **Last Updated**: 2026-01-21
> **Knowledge Source**: https://support.vcita.com/hc/en-us/articles/360040922094-Add-Clients-and-Contacts-in-vcita
> **Note**: "Matter" is vcita's general entity - called "Property" for Home Services, "Patient" for Healthcare, etc.

## Objective
Verify that a user can create a new matter using the Quick Actions menu with comprehensive test data, and verify all fields are properly saved.

## Prerequisites
- User must be logged in (Call: login function)
- User should be on the dashboard

## Steps

### Part 1: Open the New Matter Form
1. Click the "Quick Actions" button in the left sidebar
2. Click "Add property" from the Quick Actions menu (under PROPERTIES section)
3. Click "Show more" to expand all contact information fields

### Part 2: Fill Contact Information
4. Fill in "First Name" field with a random first name (required)
5. Fill in "Last Name" field with a random last name/timestamp
6. Fill in "Email" field with a random test email
7. Fill in "Mobile phone" field with a random phone number
8. Fill in "Address" field with a random address
9. Select "Status" from dropdown (e.g., "Existing customer")
10. Fill in "Referred by" field with referral source

### Part 3: Fill Matter Details
11. Fill in "Property address" field with matter location
12. Select "Property type" from dropdown (e.g., "Residential" or "Commercial")
13. Fill in "How can we help you?" field with service request
14. Fill in "Special instructions/requests" field with instructions
15. Fill in "Private notes" field with internal notes

### Part 4: Save and Verify
16. Click "Save" button
17. Verify the matter card opens with the correct name
18. Verify URL contains `/app/clients/` with a matter ID
19. Click "Show more" in Contact information to expand details
20. Verify saved contact fields:
    - Name matches entered name
    - Address matches entered address
    - Referred by matches entered value
21. Open edit dialog and verify:
    - Email matches entered email
    - Phone matches entered phone

## Expected Result
- Matter is successfully created
- Matter card/profile page is displayed
- All entered information is visible and correctly saved
- Contact information shows: name, address, referred by, status
- Matter details are saved (address, type, help request, instructions, notes)

## Test Data
Uses randomly generated data:
- First Name: Random from ["Test", "John", "Jane", "Alex", "Sam"]
- Last Name: "Matter" + timestamp
- Email: test_{timestamp}@vcita-test.com
- Phone: 1-555-{random 7 digits}
- Address: {random number} Test Street, Test City, TC {zip}
- Matter Address: {random number} Property Lane, Property Town, PT {zip}
- Matter Type: "Residential" or "Commercial"
- Help Request: "Looking for regular maintenance services"
- Special Instructions: "Please call before arriving. Gate code: {random}"
- Private Notes: "Test automation record - {timestamp}"
- Referred By: Random from ["Google Search", "Facebook", "Friend Referral", "Website"]

## Context Operations
Saves to context for later tests/cleanup:
- `created_matter_name`: Full name of the created matter
- `created_matter_email`: Email of the created matter
- `created_matter_id`: ID from the URL (for cleanup/delete test)

## Notes
- This account uses "Properties" terminology (Home Services vertical)
- Other verticals may use "Patient", "Client", etc. - all are "matters" internally
- The Quick Actions menu has sections: SCHEDULE, PROPERTIES, SALES, OTHER
- "Add property" is under PROPERTIES section
- Must click "Show more" to see all contact fields (Referred by, Social media, etc.)
- The form is inside an iframe, so proper iframe handling is required
- Property type dropdown has options: "Residential", "Commercial"
- Status dropdown has options: "Existing customer", "Lead", etc.
