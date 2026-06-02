# Test Run Management

## Create Test Run

```bash
# Create test run with specific test cases
polarion-cli create-test-run \
  --title "WMCO 10.19.2 Z-Stream - AWS - 2026-04-23" \
  --test-case-ids "OCP-25593,OCP-28632,OCP-31276"

# Create test run using Lucene query
polarion-cli create-test-run \
  --title "Windows Proxy Tests" \
  --query "type:testcase AND id:(OCP-65980 OR OCP-66670 OR OCP-71173)"

# With template
polarion-cli create-test-run \
  --title "My Test Run" \
  --template "Empty" \
  --test-case-ids "OCP-12345,OCP-12346"
```

## Update Test Result

```bash
# Mark test as passed
polarion-cli update-test-result OSE/20260423-0851 OCP-25593 --result passed

# Mark test as failed with comment
polarion-cli update-test-result 20260423-0851 OCP-56354 \
  --result failed \
  --comment "Service failed to stop correctly"

# Update with executor
polarion-cli update-test-result 20260423-0851 OCP-32273 \
  --result passed \
  --executed-by "rrasouli@redhat.com"
```

**Result values:** `passed`, `failed`, `blocked`

## Get Test Run Status

```bash
polarion-cli get-test-run-status 20260423-0851
polarion-cli get-test-run-status 20260423-0851 | jq '.statistics'
```

## Import Results from Excel

```bash
# Import from dashboard export
polarion-cli import-results dashboard-export.xlsx

# With custom title template
polarion-cli import-results results.xlsx \
  --title-template "WMCO {platform} - {date}"

# With specific template
polarion-cli import-results results.xlsx \
  --template "Empty" \
  --title-template "Release 10.19.2 - {platform} - {date}"
```

**Excel file format:**
- Multi-sheet Excel (.xlsx) files supported
- Each sheet represents a platform/test run
- Test result columns: Test ID (col 1), Title (col 2), Status (col 3), Prow URL (col 4)
- Status values: "Passed", "Failed", "Blocked" (case-insensitive)
- Special sheets:
  - "Summary" sheet is automatically skipped
  - "Variants" sheet (optional): Platform (col 1), Variant (col 2), Job URL (col 3), Build Date (col 4)

**Behavior:**
1. Creates one test run per Excel sheet (excluding Summary and Variants)
2. Adds all test cases from the sheet to the test run
3. Updates test results based on Status column
4. If Variants sheet exists, adds variant links to test run descriptions
5. Skips invalid test IDs automatically
6. Returns JSON summary with URLs to all created test runs
