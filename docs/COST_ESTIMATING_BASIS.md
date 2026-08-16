# Project-MSR cost estimating basis - version 4.2.0

## Purpose

Version 4.2 establishes a bottom-up activity-based planning estimate for every shared and route-specific activity. The estimate is a planning basis, not a regulator, host, laboratory, EPC, supplier, or construction quotation.

## Cost architecture

Each task contains direct labor, direct non-labor, risk allowance, low/high range, and a basis-of-estimate record. Direct non-labor is decomposed into external engineering/laboratory services; software/compute/data; equipment/materials/fabrication; facilities/test/field operations; regulatory review fees; legal/hearing/advisory services; travel/field support; and other direct cost.

Major EPC and validation contracts remain source accounting packages. A defined share is allocated to detailed technical tasks as a non-additive fully burdened view. The allocation improves task economics and accountability but is not included a second time in program totals.

## Labor-rate basis

Productive time is 1,680 hours per FTE-year. Rates are constant 2026-dollar, fully burdened owner/contractor planning rates rather than salaries. They include salary, benefits, payroll burden, facilities, ordinary software, indirect labor, and corporate overhead. Task-specific subcontracts, major software, laboratories, equipment, travel, regulatory fees, and risk are modeled separately.

| Role ID | Loaded rate ($000/FTE-year) | Equivalent loaded rate ($/productive hour) |
|---|---:|---:|
| CE | 315 | 188 |
| CM | 240 | 143 |
| CNO | 385 | 229 |
| COST | 220 | 131 |
| CS | 225 | 134 |
| CTO | 365 | 217 |
| CYB | 250 | 149 |
| DATA | 230 | 137 |
| DC | 165 | 98 |
| EE | 220 | 131 |
| ENV | 225 | 134 |
| HFE | 230 | 137 |
| IC | 245 | 146 |
| LAW | 365 | 217 |
| LIC | 260 | 155 |
| MAT | 250 | 149 |
| ME | 225 | 134 |
| OPS | 210 | 125 |
| PC | 210 | 125 |
| PD | 335 | 199 |
| PM | 290 | 173 |
| PRA | 255 | 152 |
| PROC | 210 | 125 |
| QA | 215 | 128 |
| RAD | 220 | 131 |
| RPX | 255 | 152 |
| SA | 260 | 155 |
| SE | 245 | 146 |
| TEST | 215 | 128 |
| TH | 250 | 149 |

## Risk and uncertainty

| Work class | Base task risk allowance |
|---|---:|
| Program Backbone | 12% |
| Engineering | 15% |
| Licensing | 18% |
| Methods And Experiments | 20% |
| Construction | 12% |
| Direct Demonstrator Package | 0% |

The task range reflects estimate maturity, technical novelty, schedule compression, procurement exposure, experimental uncertainty, and route-specific review risk. Reserve placeholder tasks remain zero because risk is embedded at task level; adding a second unallocated reserve would double count the current risk allowance.

## Common program accounting estimate

| Concept | Activities | FTE-years | Labor ($M) | Non-labor ($M) | Total ($M) |
|---|---:|---:|---:|---:|---:|
| Demonstrator | 323 | 139.8 | 33.0 | 90.9 | 123.9 |
| Power Reactor | 306 | 668.4 | 157.7 | 605.3 | 763.0 |
| Shared | 212 | 274.9 | 67.2 | 106.6 | 173.8 |

## Representative task corrections

| ID | Activity | FTE-years | Direct labor ($M) | Direct non-labor plus risk ($M) | Direct task total ($M) | Allocated package share ($M) | Fully burdened task view ($M) | Prior estimate ($M) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| D-3.4.c | Core Nuclear Design & Reactivity Control | 2.50 | 0.63 | 0.38 | 1.02 | 0.00 | 1.02 | 0.018 |
| P-3.4.c | Core Nuclear Design & Reactivity Control | 10.00 | 2.54 | 1.36 | 3.90 | 2.28 | 6.18 | 0.098 |
| D-3.2.a | Seismic Basis: PSHA, GMRS, and SSE | 0.44 | 0.10 | 0.42 | 0.52 | 0.00 | 0.52 | 0.002 |
| P-3.2.a | Seismic Basis: PSHA, GMRS, and SSE | 2.48 | 0.56 | 1.23 | 1.79 | 0.50 | 2.29 | 0.025 |
| D-3.3.e | ASME Section III Pressure Boundary Design (Vessels, Heat Exchangers) | 0.44 | 0.10 | 0.36 | 0.46 | 0.00 | 0.46 | 0.013 |
| P-3.3.e | ASME Section III Pressure Boundary Design (Vessels, Heat Exchangers) | 3.02 | 0.69 | 1.14 | 1.83 | 0.69 | 2.52 | 0.086 |
| D-3.7.a | Safety I&C Functional Requirements & Architecture (IEEE 603) | 0.50 | 0.12 | 0.25 | 0.37 | 0.00 | 0.37 | 0.004 |
| P-3.7.a | Safety I&C Functional Requirements & Architecture (IEEE 603) | 3.02 | 0.75 | 0.80 | 1.55 | 0.61 | 2.16 | 0.030 |
| D-3.19.b | Internal Events (At-Power) PRA Development | 0.50 | 0.13 | 0.31 | 0.43 | 0.00 | 0.43 | 0.023 |
| P-3.19.b | Internal Events (At-Power) PRA Development | 3.30 | 0.85 | 1.05 | 1.89 | 0.83 | 2.73 | 0.169 |
| D-3.18.m | Integrated System Validation (ISV) - Execution | 0.50 | 0.11 | 0.42 | 0.53 | 0.00 | 0.53 | 0.011 |
| P-3.18.m | Integrated System Validation (ISV) - Execution | 2.75 | 0.61 | 1.24 | 1.85 | 0.60 | 2.45 | 0.069 |

## Review rules

1. Review the direct task cost for labor and task-specific purchases.
2. Review the fully burdened task view when assessing the total economic weight of a technical activity.
3. Sum only the accounting task totals, not the non-additive allocated package shares.
4. Re-estimate when design maturity, site, licensing path, test scope, supplier strategy, qualification standard, schedule, or make/buy basis changes.
5. Replace allowances with quotations, framework agreements, laboratory work orders, regulator project plans, and construction estimates as they become available.

## Source and benchmarking register

- U.S. Bureau of Labor Statistics - Nuclear Engineers: https://www.bls.gov/ooh/architecture-and-engineering/nuclear-engineers.htm - Salary reasonableness check before applying benefits, indirects, facilities, and contractor burden.
- U.S. Bureau of Labor Statistics - Architectural and Engineering Managers: https://www.bls.gov/ooh/management/architectural-and-engineering-managers.htm - Management and technical-authority salary reasonableness check.
- NRC 10 CFR 170.20 and Advanced Reactor Fees: https://www.nrc.gov/reading-rm/doc-collections/cfr/part170/part170-0020.html - Regulatory review fee-rate basis for advanced-reactor planning.
- GAO Cost Estimating and Assessment Guide, GAO-20-195G: https://www.gao.gov/products/gao-20-195g - Bottom-up WBS, documented assumptions, uncertainty, and estimate reconciliation practices.
