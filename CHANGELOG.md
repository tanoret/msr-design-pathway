# Changelog

## 4.3.0 - 2026-08-18

- Added execution-ready implementation plans to all 937 WBS activities.
- Added 11 fuel, chemistry, fission-product, materials, safeguards, waste, test, supply-chain, host, facility, and startup playbooks.
- Added 25 detailed chemistry and processing experiments and task-specific fuel/chemistry execution sequences.
- Added the Implementation application section and task-level Implementation tab.
- Added implementation registers to exports and changed the large Excel export to on-demand generation.
- Preserved the v4.2 cost baseline, licensing-path differences, schedule, password gate, and complete uncompressed JSON data.

## 4.3.0 - 2026-08-18

- Added execution-ready implementation plans to all 937 WBS activities.
- Added 11 fuel, chemistry, fission-product, materials, safeguards, waste, test, supply-chain, host, facility, and startup playbooks.
- Added 25 detailed chemistry and processing experiments and task-specific fuel/chemistry execution sequences.
- Added the Implementation application section and task-level Implementation tab.
- Added implementation registers to exports and changed the large Excel export to on-demand generation.
- Preserved the v4.2 cost baseline, licensing-path differences, schedule, password gate, and complete uncompressed JSON data.

## 4.2.2 - 2026-08-16

- Replaced the oversized monolithic repository database with plain UTF-8 JSON shards.
- Preserved all database fields, records, task order, engineering work packages, and cost data.
- Added a checksummed manifest and canonical semantic database digest.
- Added transparent shard loading and validation to the app and command-line tools.
- Added database split/reconstruction utilities and GitHub/Streamlit deployment guidance.
- Added tests enforcing GitHub-safe file sizes and complete database equivalence.

## 4.2.1 - 2026-08-16

- Added a fail-closed password gate before database loading and application rendering.
- Added PBKDF2-SHA256 password hashing, constant-time verification, Streamlit secrets, and environment-variable configuration.
- Added temporary lockout after repeated failed attempts, idle-session expiration, and a sidebar Sign out control.
- Added `scripts/set_password.py`, a local hashed secrets file, a secrets template, and deployment guidance.
- Added five authentication tests, increasing the automated suite to 44 tests.
- Preserved the complete 4.2.0 planning database, task costs, pathway logic, schedules, plots, and exports.

## 4.2.0 - 2026-08-16

- Re-estimated all 937 shared and route-specific activities using a bottom-up activity-based cost model.
- Replaced token engineering allowances with planned FTE-years, labor hours, loaded rates, direct non-labor components, task risk, and low/high ranges.
- Added basis-of-estimate identifiers, estimate class/method, prior-versus-revised deltas, cost drivers, exclusions, double-counting controls, and re-estimate triggers.
- Added non-additive allocation of major EPC and validation contracts to detailed technical tasks while preserving one-time accounting totals.
- Increased the demonstrator Core Nuclear Design & Reactivity Control activity from approximately $18 thousand to approximately $1.02 million direct; the commercial equivalent is approximately $3.90 million direct and $6.18 million fully burdened.
- Added the Cost basis application section, task-level cost inspector, flat cost audit CSV, and cost estimating basis document.
- Reconciled resource assignments, annual labor, annual direct non-labor, task totals, route totals, and integrated scenario totals.
- Removed duplicate generic regulatory-fee cost from the common licensing assurance package.
- Preserved the $30 million direct demonstrator package and established schedule milestones.
- Expanded validation to 39 tests and 12 application-section smoke flows.

## 4.1.0 - 2026-08-15

- Rephased the integrated portfolio so resource and funding demand peak in 2032 during commercial detailed engineering and construction, rather than during initial mobilization.
- Preserved the Q4 2026 program start, December 2028 demonstrator construction/authorization target, 2029 demonstrator operations, January 2030 commercial construction start, and December 2035 commercial-operation target.
- Added staged demonstrator-ready and final commercial releases for methods, salt properties, kinetics, source term, instrumentation, materials, maintainability, safeguards, and topical reports.
- Shifted commercial design, supplier engineering, qualification, construction evidence, and startup effort later while retaining a sustained post-startup technical core.
- Added field-producing engineering, commissioning, supplier-acceptance, and as-built closeout resources without adding management layers.
- Rebalanced supplier and experimental allowances through existing infrastructure, reusable instrumentation/data systems, combined test configurations, fixed-scope work packages, and milestone-based procurement.
- Rebuilt annual task, assignment, labor, non-labor, and FTE profiles so the standalone database and scenario exports reconcile exactly.
- Standardized every Plotly figure with a shared visual grammar, responsive sizing, readable typography, unit labels, hovercards, export controls, compact legends, and route-consistent colors.
- Improved the pathway graph with compact fixed-size node labels, readable hover content, click-to-inspect behavior, and no text overflow.
- Removed duplicate network visualizations; the dependency network appears only in the Pathway graph section.
- Expanded the automated suite to 34 tests and executed all 11 application sections through the control-flow smoke harness.


## 3.0.0 - 2026-08-15

- Rebuilt the visual layer with a custom responsive design system, branded navigation, dashboard cards, compact controls, and styled Plotly/data views.
- Added an eleventh application section, **Pathway graph**, with separate demonstrator, commercial, and combined route networks.
- Added click-to-open graph behavior using Plotly selection events and synchronized task inspection.
- Simplified the internal presentation by removing supplemental route-status callouts and executive-leadership narrative from the interface and task text.
- Retained required executive resource and approval assignments while removing executive-leadership narrative from task presentation.
- Upgraded all 841 shared tasks and 96 route tasks to the Engineering Work Package 3.0 model.
- Added structured entry criteria, controlled inputs, execution procedures, requirements, tool qualification, deliverable registers, verification, interfaces, task risks, records, definition of done, resource plans, and execution controls.
- Improved task-specific input ownership, step evidence, independent verification, compliance evidence, deliverable ordering, and acceptance ordering.
- Expanded data and Excel exports with engineering-package summary, inputs, procedure, requirements, toolchain, outputs, verification, interfaces, and risk-control registers.
- Optimized scenario construction by sharing immutable engineering-package detail while copying only scenario-mutated structures.
- Expanded the automated suite to 31 tests and executed all 11 application sections with the control-flow smoke harness.

## 2.0.0 - 2026-08-15

- Corrected the architecture so DOE Launch Pad applies only to the demonstrator and commercial power-reactor licensing is selected independently.
- Replaced small route overlays with 96 bottom-up authorization and licensing activities.
- Added distinct Part 50 CP/OL, Part 52 COL/ESP/DC/ITAAC, Part 53 PRA/SRE safety-case, and proposed Part 57 readiness/manufacturing/fleet work packages.
- Added current Part 57 mode that carries a complete executable Part 50, 52, or 53 fallback.
- Added product-stack-specific cost, resource, schedule, milestone, construction-verification, operation-authorization, and repeat-deployment modeling.
- Added active-scenario JSON, CSV, and Excel exports.

## 1.1.0 - 2026-08-15

- Initial Project-MSR JSON database and Streamlit scenario-planning prototype.
