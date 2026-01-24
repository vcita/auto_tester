# Stress Test

Run stress tests on categories to check for consistency and flakiness.

## Usage

```
/stress_test categories: <category1> [category2 ...] iterations: <number>
```

## Examples

```
/stress_test categories: clients iterations: 10
/stress_test categories: clients scheduling iterations: 20
/stress_test categories: scheduling/services iterations: 5
```

## What It Does

1. Runs the specified categories the given number of times
2. Tracks pass/fail rates for each category
3. Analyzes failure reasons and patterns
4. Provides a detailed report showing:
   - Pass rate for each category
   - Stability status (STABLE/FLAKY/UNSTABLE)
   - Failure reasons grouped by error type
   - Details of failed iterations

## Execution Instructions

When the user invokes `/stress_test` with input, you MUST:

1. **Parse the user's input** to extract:
   - Look for patterns like "categories: X Y Z" or "category: X" or just category names
   - Look for "iterations: N" or "iterations N" or just a number
   - Extract category names (can be multiple, space-separated)
   - Extract iterations number

2. **Validate the input**:
   - Ensure at least one category is specified
   - Ensure iterations is a positive integer
   - If missing, ask the user for clarification

3. **Execute the stress test command** using the terminal:
   ```bash
   python main.py stress_test --categories <category1> [category2 ...] --iterations <number>
   ```
   
   Use the `run_terminal_cmd` tool to execute this command. The command will:
   - Show progress bars during execution
   - Display a detailed report when complete
   - Return exit code 0 if all tests pass, 1 if any fail
   
   **IMPORTANT - Monitoring Required:**
   - Stress tests can take a long time (each iteration takes ~2 minutes, so 20 iterations = ~40 minutes)
   - You MUST let the test run and monitor it periodically
   - Check progress every 5 minutes by:
     - Reading the output file if redirected to a file
     - Checking if the process is still running
     - Looking for completion markers in the output (e.g., "Stress Test Report", "Summary", "STABLE", "FLAKY", "UNSTABLE", "Total runs")
   - Continue monitoring until:
     - The test completes and shows the final report, OR
     - You detect an issue (process crashed, stuck, or error pattern)
   - If running in background or redirecting output, periodically check the output file for progress
   - When the test completes, display the full final report to the user

4. **Capture and display the output**:
   - The command output includes the full stress test report
   - Show the user the complete report including:
     - Summary table with pass rates
     - Failure analysis (if any failures)
     - Overall summary
   - If monitoring, provide periodic updates on progress

5. **Handle errors gracefully**:
   - If categories don't exist, the command will warn and skip them
   - If there's an execution error, show the error message
   - Always provide clear feedback to the user

## Input Parsing Examples

User says: `/stress_test categories: clients iterations: 10`
- Categories: ["clients"]
- Iterations: 10

User says: `/stress_test clients scheduling 5 times`
- Categories: ["clients", "scheduling"]
- Iterations: 5

User says: `/stress_test run clients 10 iterations`
- Categories: ["clients"]
- Iterations: 10

## Options

The user can also specify:
- `headless` or `--headless` - Run browser in headless mode
- `keep-open` or `--keep-open` - Keep browser open on failure

Add these flags to the command if mentioned.

## Output Format

The report includes:
- **Summary Table**: Category, iterations, passed/failed counts, pass rate, status
- **Failure Analysis**: Grouped failure reasons with counts
- **Failed Iterations**: List of which runs failed and why
- **Overall Summary**: Total runs, pass rate, and overall status

## Interpretation

- **STABLE** (100% pass rate): Tests are consistently passing
- **FLAKY** (80-99% pass rate): Tests show some inconsistency
- **UNSTABLE** (<80% pass rate): Tests are unreliable and need investigation

## Important

- Always use the `run_terminal_cmd` tool to execute the command
- Do NOT try to run the stress test logic directly in Python
- The command handles all the complexity and provides formatted output
- **You MUST monitor the test**: Let it run and check progress every 5 minutes until completion or until you detect an issue
- Show the complete final report to the user when the test completes
- Provide periodic progress updates while monitoring
