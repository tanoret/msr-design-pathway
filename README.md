# Project-MSR Integrated Development Planner

Project-MSR is a password-protected, scenario-driven Streamlit application and engineering execution database for an integrated molten-salt-reactor development program. It connects methods, experiments, fuel supply, chemistry and materials qualification, DOE demonstrator authorization, selectable NRC commercial licensing, resources, costs, schedules, risks, construction, startup, and operating optimization.

## Current planning baseline

- Program mobilization begins **October 1, 2026**.
- Demonstrator authorization and construction turnover complete by **December 31, 2028**.
- Demonstrator commissioning and operating campaigns occur during **2029**.
- Commercial field construction begins **January 1, 2030**.
- Commercial operation is targeted for **December 31, 2035**.
- The nominal Launch Pad USA plus Part 53 COL case remains approximately **$1,222.8 million** and **1,180.9 FTE-years**. Version 4.3 adds implementation detail without double-counting playbook or experiment rows.

## Version 4.3 execution content

Every one of the **937** shared and route-specific activities now contains both:

1. an Engineering Work Package with scope, inputs, engineering procedure, requirements, tools, deliverables, verification, interfaces, risks, records, resources, schedule logic, and definition of done; and
2. an Implementation Plan describing the delivery strategy, make/buy/partner decision, authorizations, work location, step-by-step field/laboratory/vendor actions, procurement, long-lead items, decisions, acceptance evidence, contingencies, implementation records, and open decisions.

The database also includes **11** execution playbooks, a **25-experiment** chemistry and fuel-salt-processing matrix, and an **8-item implementation closure register** for decisions that still require real contracts, facility commitments, approved specifications or test evidence. Key playbooks cover fuel supply, chemistry/processing, fission-product behavior, materials, liquid-fuel accountancy, waste/disposition, experimental facilities, supplier execution, host integration, and startup/data release.

Twenty-one high-consequence work packages contain bespoke execution sequences for chemistry methods, property data, source term, online instrumentation and sampling, liquid-fuel MC&A, materials/corrosion, fuel sourcing and receipt, INL data qualification, demonstrator chemistry/source-term/materials campaigns, commercial fuel production, and operating optimization.

## Licensing architecture

The demonstrator and commercial reactor are selected independently.

### Demonstrator

- **Launch Pad USA** - external host configuration.
- **Launch Pad INL** - INL parcel and site-services configuration.

DOE Launch Pad applies only to the demonstrator.

### Commercial power reactor

- **10 CFR Part 50** - Construction Permit followed by Operating License, with optional Limited Work Authorization.
- **10 CFR Part 52** - straight COL, ESP + COL, Design Certification + COL, or ESP + Design Certification + COL.
- **10 CFR Part 53** - risk-informed COL or CP/OL sequence.
- **Proposed 10 CFR Part 57 planning** - readiness plus an executable Part 50/52/53 fallback, or a future-rule sensitivity.

Each choice activates a distinct task network, products, review sequence, construction-verification model, resources, cost, milestones, and operation gate.

## Application sections

1. **Overview**
2. **Pathway comparison**
3. **Licensing plan**
4. **Pathway graph**
5. **Schedule**
6. **Work packages**
7. **Resources**
8. **Financials**
9. **Cost basis**
10. **Experiments**
11. **Implementation** - fuel supply, chemistry/processing tests, other playbooks, and the task execution register
12. **Risks & gates**
13. **Data & export**

The complete dependency graph appears only in Pathway graph. The integrated Excel export is generated on demand because it contains the full implementation and engineering registers.

## Complete database stored as plain JSON shards

The database remains ordinary, human-readable UTF-8 JSON and is split only to keep each repository file below GitHub's 100 MB limit. No record is compressed, minified, summarized, or removed.

```text
data/project_msr_database.manifest.json
data/project_msr_database.core.json
data/project_msr_database.tasks.001.json
...
```

Reconstruct a monolithic local JSON file with:

```bash
python scripts/reconstruct_database.py
```

## Password-protected deployment

Copy the local `[auth]` block into Streamlit Community Cloud **Secrets**. Keep the GitHub repository private when the database itself is confidential; the in-app password gate cannot protect files exposed by a public repository.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Validate

```bash
python scripts/validate_database.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q
PROJECT_MSR_SMOKE_ALL=1 python scripts/smoke_test_app_without_streamlit.py
```

## Release

- Application version: **4.3.1**
- Database version: **4.3.0**
- Shared activities: **841**
- Route-specific activities: **96**
- Engineering- and implementation-ready activities: **937**
- Shared resource assignments: **3,138**
- Resource roles: **30**
- Implementation playbooks: **11**
- Chemistry/processing experiments: **25**
- Program-level implementation closure items: **8**
- High-consequence bespoke implementation packages: **21**
- Automated tests: **54**

See `RELEASE_NOTES_4.3.1.md`, `docs/IMPLEMENTATION_EXECUTION_PLAN.md`, `docs/FUEL_SUPPLY_AND_PROCUREMENT.md`, `docs/CHEMISTRY_AND_PROCESSING_VALIDATION.md`, `docs/IMPLEMENTATION_GAP_REGISTER.md`, `docs/ENGINEERING_WORK_PACKAGES.md`, `docs/COST_ESTIMATING_BASIS.md`, `docs/LICENSING_PATHS.md`, and `docs/VALIDATION.md`.
