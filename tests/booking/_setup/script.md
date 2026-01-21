# Booking Category Setup - Detailed Script

> **Status**: Pending exploration
> **Last Updated**: Not yet explored

## Actions

### Step 1: Login
- **Action**: Call function
- **Function**: login
- **Parameters**:
  - username: "test@vcita.com"
  - password: "testpassword123"
- **Expected return**: logged_in_user saved to context

### Step 2: Navigate to Booking
- **Action**: Click
- **Target**: Booking menu item
- **Element hints**:
  - `get_by_role("link", name="Booking")`
  - `[data-nav="booking"]`
  - `.nav-booking`
- **Wait for**: Booking page to load

### Step 3: Verify Booking Accessible
- **Action**: Verify
- **Target**: Booking content area
- **Element hints**:
  - `.booking-container`
  - `[data-page="booking"]`
- **Condition**: Element is visible

## Success Verification
- User is logged in (logged_in_user in context)
- Booking section is displayed
