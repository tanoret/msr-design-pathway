# Project-MSR Planner 4.2.0 release notes

Release date: 2026-08-16

Version 4.2 is a complete task-by-task cost re-estimation. It replaces nominal or token engineering allowances with activity-based labor, external services, equipment, test, facility, regulatory, legal, travel, risk, and uncertainty estimates.

## Principal correction

The demonstrator Core Nuclear Design & Reactivity Control package increased from $17.9 thousand to $1.02 million direct. The commercial package is $3.90 million direct and $6.18 million when its non-additive share of the EPC/vendor detailed-engineering contract is displayed.

## Database and application changes

- Re-estimated all 937 activities using a consistent bottom-up basis.
- Added planned labor hours, effort breakdowns, loaded rates, direct-cost components, risk, low/high ranges, estimate class, BOE ID, prior/revised comparison, drivers, exclusions, and triggers.
- Added a non-additive package-allocation view for major EPC and methods-validation contracts.
- Added a dedicated Cost basis application section and cost register.
- Added task-level cost detail to the work-package inspector.
- Updated pathway comparisons, annual cash flow, resources, and exports to use the revised task costs.
- Removed the generic regulatory-fee allowance from the common licensing-assurance package to prevent double counting with selected route modules.
- Preserved the $30.0 million direct demonstrator hardware/construction package and the established schedule dates.

## Nominal integrated estimate

The default Launch Pad USA plus Part 53 COL scenario is $1,222.8 million and 1,180.9 FTE-years. The common program before selected DOE and commercial route modules is $1,060.7 million.

## Verification

The release passes schema validation, the database-integrity validator, Python compilation, 39 automated tests, all 12 application-section smoke flows, and scenario generation for every supported licensing variant.
