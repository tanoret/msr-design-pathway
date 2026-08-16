# Project-MSR Integrated Development Planner

Project-MSR is a password-protected, scenario-driven Streamlit application for planning an integrated molten-salt-reactor development program. It connects engineering methods, experimental evidence, demonstrator authorization and construction, commercial licensing, resources, costs, schedule logic, risks, readiness gates, and operating optimization in one selectable model.

## Current planning baseline

- Program mobilization begins **October 1, 2026**.
- Demonstrator authorization and construction turnover complete by **December 31, 2028**.
- Demonstrator commissioning and operating campaigns occur during **2029**.
- Commercial field construction begins **January 1, 2030**.
- Commercial authorization, initial criticality, and power ascension complete during **2035**, with commercial operation by **December 31, 2035**.
- The nominal Launch Pad USA plus Part 53 COL case is approximately **$1.223 billion** and peaks during commercial execution in **2032**.

## Program scope

The database covers:

- neutronics, circulating-fuel kinetics, thermal-hydraulics, chemistry, materials, source term, safety analysis, PRA, digital I&C, site, civil/structural, systems, operations, and cross-disciplinary methods;
- verification, validation, uncertainty quantification, and methods topical reports;
- a 1:1-scale integral thermal-hydraulics facility;
- an INL-hosted critical experiment;
- DOE Launch Pad authorization, engineering, construction, commissioning, and operation of the demonstrator;
- demonstrator experimental campaigns that produce qualified data for the commercial reactor;
- commercial power-reactor engineering and licensing under selectable NRC pathways;
- commercial construction, startup, reliability growth, and economic optimization;
- task-level resources, annual and quarterly staffing, financials, milestones, risks, readiness gates, RACI, and scenario exports.

## Licensing architecture

The demonstrator and commercial reactor are selected independently.

### Demonstrator

- **Launch Pad USA** - external host configuration.
- **Launch Pad INL** - INL parcel and site-services configuration.

DOE Launch Pad activities apply only to the demonstrator.

### Commercial power reactor

- **10 CFR Part 50** - Construction Permit followed by Operating License, with an optional Limited Work Authorization variant.
- **10 CFR Part 52** - straight COL, ESP + COL, Design Certification + COL, or ESP + Design Certification + COL.
- **10 CFR Part 53** - risk-informed COL or CP/OL product sequence.
- **Proposed 10 CFR Part 57 planning** - current readiness plus a complete Part 50/52/53 fallback, or a future-rule sensitivity for standardized/manufacturing deployment.

Each selection activates a distinct activity network, product set, review sequence, construction-verification model, resource profile, cost profile, milestone set, and operation-authorization gate.

## Engineering-ready work packages and cost basis

All **937** shared and route-specific activities carry a complete Engineering Work Package 4.2 record, including scope, entry criteria, controlled inputs, execution instructions, requirements, tools, deliverables, verification, interfaces, risks, quality records, schedule logic, resource assignments, and definition of done.

Every activity also carries a bottom-up estimate with planned labor hours, fully burdened discipline rates, direct services and purchases, equipment and test costs, regulatory and legal components where applicable, task risk allowance, estimate range, previous estimate, revision delta, cost drivers, exclusions, and re-estimate triggers.

## Application sections

1. **Overview** - scenario summary, execution stages, dates, funding, and staffing indicators.
2. **Pathway comparison** - product-stack cost, schedule, activity count, review cycles, and repeat-deployment comparison.
3. **Licensing plan** - selected route schedule, products, dates, costs, and route activity dictionary.
4. **Pathway graph** - the single dependency-network view for DOE, NRC, and combined routes; click a node to open its complete work package.
5. **Schedule** - integrated roadmap, detailed Gantt views, and authorization/startup milestones.
6. **Work packages** - searchable engineering task database.
7. **Resources** - annual and quarterly staffing, discipline demand, labor classification, continuity, and assignment browser.
8. **Financials** - annual cash flow, cost by stream, route-cost composition, and demonstrator package control.
9. **Cost basis** - task-level estimate register, direct-cost components, package allocations, uncertainty ranges, and basis-of-estimate inspector.
10. **Experiments** - methods, integral facility, INL critical experiment, demonstrator tests, and validation matrix.
11. **Risks & gates** - risk register, design/readiness gates, governance records, and RACI.
12. **Data & export** - active-scenario JSON, CSV files, multi-sheet Excel export, engineering-package registers, cost audit, and source register.

## Complete database stored as plain JSON shards

The complete database remains ordinary, human-readable UTF-8 JSON. It is split only to comply with GitHub's 100 MB per-file limit. No field, task, engineering work package, resource assignment, cost record, route module, milestone, risk, test matrix, source, or supporting collection is removed, shortened, summarized, minified, encoded, or compressed.

```text
data/project_msr_database.manifest.json
data/project_msr_database.core.json
data/project_msr_database.tasks.001.json
data/project_msr_database.tasks.002.json
data/project_msr_database.tasks.003.json
data/project_msr_database.tasks.004.json
```

The manifest defines original ordering, record counts, file sizes, per-file SHA-256 checksums, and a canonical semantic checksum for the complete logical database. The application verifies the parts and reconstructs the same in-memory database before scenario calculations begin.

To reconstruct one local monolithic JSON file:

```bash
python scripts/reconstruct_database.py
```

The reconstructed file is intentionally ignored by Git because it remains larger than GitHub's per-file limit.

## Password-protected access

The server-side password gate executes before the planning database is loaded and before any engineering, licensing, resource, financial, schedule, graph, risk, or export view is rendered.

The release supports PBKDF2-SHA256 password hashes, Streamlit secrets, environment variables, failed-attempt lockout, idle-session expiration, and an explicit **Sign out** control. The local `.streamlit/secrets.toml` is excluded from Git. Copy its `[auth]` block into the Streamlit Community Cloud **Secrets** settings before deployment.

The website gate does not make files in a public repository confidential. Use a private repository when the database itself must remain restricted.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

For Streamlit Community Cloud, select `app.py` as the entry point and configure the authentication secret.

## Clean Git history after the rejected oversized push

The rejected 184 MB file remains in your local Git history even after it is deleted from the working tree. Because the remote repository is empty, the simplest clean publication is:

```bash
# Run this from a fresh directory containing the unpacked v4.2.2 package.
git init
git branch -M main
git remote add origin git@github.com:tanoret/msr-design-pathway.git
git add .
git commit -m "Release Project-MSR Planner v4.2.2"
git push -u origin main
```

Alternatively, follow `docs/GITHUB_STREAMLIT_DEPLOYMENT.md` to replace the rejected local history in the existing directory.

Before pushing, these commands should print nothing:

```bash
git ls-files data/project_msr_database.json
find . -type f -not -path './.git/*' -size +90M -print
```

## Validate

```bash
python scripts/validate_database.py
pytest -q
```

## Export a scenario without Streamlit

```bash
python scripts/export_scenario.py \
  --demonstrator launchpad_usa \
  --power-path part52 \
  --power-variant esp_dc_col \
  --output project_msr_part52_scenario.json
```

## Release

- Application version: **4.2.2**
- Database version: **4.2.0**
- Shared program activities: **841**
- Route-specific activities: **96**
- Engineering-ready and costed activities: **937**
- Shared resource assignments: **3,138**
- Resource roles: **30**
- Application sections: **12**
- Nominal Part 53 COL program cost: **$1,222.8 million**

See `CHANGELOG.md`, `RELEASE_NOTES_4.2.2.md`, `docs/GITHUB_STREAMLIT_DEPLOYMENT.md`, `docs/ACCESS_CONTROL.md`, `docs/COST_ESTIMATING_BASIS.md`, `docs/LICENSING_PATHS.md`, `docs/ENGINEERING_WORK_PACKAGES.md`, and `docs/VALIDATION.md`.
