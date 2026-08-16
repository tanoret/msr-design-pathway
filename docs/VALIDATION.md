# Validation record - Project-MSR application v4.2.2 / database v4.2.0

## Completed checks

- Sharded database manifest and per-file checksums: passed.
- Canonical semantic equivalence with the complete v4.2.0 database: passed.
- All repository database files are plain JSON and below 90 MB: passed.
- JSON Schema Draft 2020-12 validation: passed.
- Database-integrity validator: passed.
- Python compilation: passed.
- Authentication hash generation, parsing, and verification tests: passed.
- Password gate executes before database loading and planner rendering: passed.
- Missing authentication configuration fails closed: implemented.
- Failed-attempt lockout, idle-session expiry, and Sign out controls: implemented.
- Pytest: 48 tests passed.
- All 12 authenticated application-section control-flow smoke tests: passed.
- The v4.2.2 application change is limited to database storage, loading, integrity verification, and deployment support; planning outputs remain unchanged.
- Shared and route task identifiers: unique.
- Resource-role references: valid.
- Active predecessor references: valid and acyclic for every tested route.
- Annual assignment FTE and labor profiles reconcile to assignment totals.
- Annual task labor, direct non-labor, risk, total cost, and resource profiles reconcile to task totals.
- Every activity has a complete bottom-up task-cost record.
- Direct non-labor components reconcile to task direct non-labor.
- Labor-effort breakdowns reconcile to planned task hours.
- Low estimate <= point estimate <= high estimate for every task.
- Non-additive major-contract allocations reconcile to their source packages.
- Regulatory fee costs are assigned to selected route modules rather than duplicated in the common licensing assurance package.
- Direct demonstrator package remains exactly $30.0 million non-labor.
- Program start, demonstrator completion, 2029 operations, 2030 commercial construction, and 2035 commercial operation dates are preserved.
- Engineering Work Package 4.2 fields are present for all activities.
- The dependency network is rendered only in the Pathway graph section.

## Nominal Launch Pad USA plus Part 53 COL profile

| Year | FTE-years | Expenditure ($M) |
|---:|---:|---:|
| 2026 | 12.3 | 9.0 |
| 2027 | 122.3 | 103.0 |
| 2028 | 78.4 | 117.1 |
| 2029 | 121.6 | 121.4 |
| 2030 | 128.9 | 123.0 |
| 2031 | 173.0 | 180.5 |
| 2032 | 183.5 | 217.4 |
| 2033 | 118.1 | 183.5 |
| 2034 | 82.9 | 85.6 |
| 2035 | 102.5 | 49.4 |
| 2036 | 29.8 | 15.8 |
| 2037 | 18.4 | 11.0 |
| 2038 | 9.3 | 6.1 |

## Executable licensing variants

| Path | Variant | Active tasks | FTE-years | Route cost ($M) | Total program ($M) | Peak FTE year | Peak FTE | Peak funding year | Peak funding ($M) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 CFR Part 50 | CP then OL | 876 | 1,186.4 | 141.8 | 1,202.4 | 2032 | 189.3 | 2032 | 226.6 |
| 10 CFR Part 50 | CP then OL with optional LWA | 877 | 1,188.1 | 145.1 | 1,205.8 | 2032 | 189.3 | 2032 | 226.6 |
| 10 CFR Part 52 | Straight COL | 874 | 1,181.2 | 169.7 | 1,230.4 | 2032 | 184.4 | 2032 | 220.6 |
| 10 CFR Part 52 | ESP + COL | 876 | 1,190.4 | 195.0 | 1,255.7 | 2032 | 184.4 | 2032 | 220.6 |
| 10 CFR Part 52 | Design Certification + COL | 877 | 1,196.0 | 223.4 | 1,284.1 | 2032 | 184.4 | 2032 | 220.6 |
| 10 CFR Part 52 | ESP + Design Certification + COL | 879 | 1,205.2 | 248.7 | 1,309.4 | 2032 | 184.4 | 2032 | 220.6 |
| 10 CFR Part 53 | Part 53 Combined License | 876 | 1,180.9 | 162.2 | 1,222.8 | 2032 | 183.5 | 2032 | 217.4 |
| 10 CFR Part 53 | Part 53 CP then OL | 877 | 1,191.2 | 185.0 | 1,245.7 | 2032 | 184.9 | 2032 | 220.4 |
