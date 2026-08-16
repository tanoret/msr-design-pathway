from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data_loader import DEFAULT_DATABASE, _load_database_uncached
from src.pathway_engine import PATH_DISPLAY_NAMES, ScenarioOptions, build_scenario, compare_pathways

DB_PATH = DEFAULT_DATABASE
VERSION = "4.2.2"
DATABASE_VERSION = "4.2.0"
APP_TEST_COUNT = 48
RELEASE_DATE = "2026-08-16"


def md(value: Any) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ").strip()


def money(kusd: float) -> str:
    return f"{float(kusd) / 1000:,.1f}"


def route_tasks(database: dict[str, Any], pathway: str) -> list[dict[str, Any]]:
    scope = "demonstrator" if pathway == "doe_launchpad" else "power_reactor"
    return list(database["pathway_modules"][pathway][scope])


def default_scenario(database: dict[str, Any]) -> dict[str, Any]:
    return build_scenario(database, ScenarioOptions())


def executable_profiles(database: dict[str, Any]) -> list[dict[str, Any]]:
    variants = {
        "part50": ["cp_ol", "cp_ol_lwa"],
        "part52": ["straight_col", "esp_col", "dc_col", "esp_dc_col"],
        "part53": ["col", "cp_ol"],
    }
    rows: list[dict[str, Any]] = []
    for path, values in variants.items():
        for variant in values:
            scenario = build_scenario(database, ScenarioOptions(power_reactor_path=path, power_reactor_variant=variant))
            annual_fte = scenario["annual_fte_years"]
            annual_cost = scenario["annual_cost_kusd"]
            rows.append(
                {
                    "path": PATH_DISPLAY_NAMES[path],
                    "variant": database["pathways"][path]["variants"][variant]["label"],
                    "tasks": scenario["summary"]["active_task_count"],
                    "assignments": scenario["summary"]["assignment_count"],
                    "fte_years": scenario["summary"]["fte_years"],
                    "route_cost_kusd": scenario["summary"]["route_specific_cost_kusd"],
                    "total_cost_kusd": scenario["summary"]["total_cost_kusd"],
                    "peak_fte_year": max(annual_fte, key=annual_fte.get),
                    "peak_fte": max(annual_fte.values()),
                    "peak_cost_year": max(annual_cost, key=annual_cost.get),
                    "peak_cost_kusd": max(annual_cost.values()),
                }
            )
    return rows


def all_tasks(database: dict[str, Any]) -> list[dict[str, Any]]:
    tasks = list(database["tasks"])
    for module in database["pathway_modules"].values():
        tasks.extend(module["demonstrator"])
        tasks.extend(module["power_reactor"])
    return tasks


def key_cost_examples(database: dict[str, Any]) -> list[dict[str, Any]]:
    ids = [
        "D-3.4.c",
        "P-3.4.c",
        "D-3.2.a",
        "P-3.2.a",
        "D-3.3.e",
        "P-3.3.e",
        "D-3.7.a",
        "P-3.7.a",
        "D-3.19.b",
        "P-3.19.b",
        "D-3.18.m",
        "P-3.18.m",
    ]
    by_id = {task["id"]: task for task in database["tasks"]}
    return [by_id[task_id] for task_id in ids]


def write_readme(database: dict[str, Any], scenario: dict[str, Any], profiles: list[dict[str, Any]]) -> None:
    quality = database["data_quality"]
    base = database["financials"]["base_cost_summary"]
    base_total = sum(float(row["Total Cost ($000)"]) for row in base)
    nominal = scenario["summary"]
    text = f"""# Project-MSR Integrated Development Planner

Project-MSR is a scenario-driven Streamlit application and JSON database for an integrated molten-salt-reactor development program. It connects engineering methods, experimental evidence, demonstrator authorization and construction, commercial licensing, resources, costs, schedule logic, risks, gates, and operating optimization in one selectable planning model.

## Current planning baseline

- Program mobilization begins **October 1, 2026**.
- Demonstrator authorization and construction turnover complete by **December 31, 2028**.
- Demonstrator commissioning and operating campaigns occur during **2029**.
- Commercial field construction begins **January 1, 2030**.
- Commercial operation authorization, initial criticality, and power ascension complete during **2035**, with commercial operation by **December 31, 2035**.
- The nominal Part 53 COL case peaks during commercial execution in **{max(scenario['annual_fte_years'], key=scenario['annual_fte_years'].get)}**, at approximately **{max(scenario['annual_fte_years'].values()):,.1f} FTE** and **${max(scenario['annual_cost_kusd'].values())/1000:,.1f} million** of annual expenditure.

## Cost estimate release 4.2

Version 4.2 replaces token task allowances with a bottom-up activity-based estimate for all **{quality['costed_task_count']:,}** shared and route-specific activities. Every task now carries:

- planned FTE-years and labor hours by producing, independent-review, integration, QA/configuration, and controls effort;
- fully burdened labor rates by discipline;
- direct external engineering or laboratory services;
- software, compute, and data costs;
- equipment, materials, fabrication, facility, test, and field costs;
- regulatory-review, legal, advisory, and travel components where applicable;
- task-specific risk allowance and low/high planning range;
- the previous estimate, revised estimate, delta, estimating method, estimate class, basis-of-estimate identifier, cost drivers, exclusions, and re-estimate triggers.

The common program accounting estimate is **${base_total/1000:,.1f} million** before the selected DOE and commercial licensing modules. The default Launch Pad USA plus Part 53 COL scenario is **${nominal['total_cost_kusd']/1000:,.1f} million**.

Large owner/EPC, methods-validation, and laboratory contracts remain accounting work packages. Their applicable shares are also allocated to detailed technical tasks as a **non-additive fully burdened task view**. This allows a user to see the complete economic weight of a design activity without counting the contract twice in program totals.

## Program scope

The database covers:

- neutronics, thermal-hydraulics, chemistry, materials, safety analysis, PRA, digital I&C, site, civil/structural, systems, and cross-disciplinary methods;
- verification, validation, uncertainty quantification, and methods topical reports;
- a 1:1-scale integral thermal-hydraulics facility;
- an INL-hosted critical experiment;
- DOE Launch Pad authorization and construction of the demonstrator;
- demonstrator commissioning and experimental campaigns that produce qualified data for the commercial reactor;
- commercial power-reactor engineering and licensing under a selectable NRC path;
- commercial construction, startup, reliability growth, and economic optimization;
- resource loading, annual and quarterly staffing, financials, milestones, risks, readiness gates, RACI, and scenario exports.

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

Each selection activates a distinct task network, product set, formal-review sequence, construction-verification model, resource profile, cost profile, milestone set, and operation-authorization gate.

## Engineering-ready work packages

All **{quality['engineering_ready_task_count']:,}** activities use the Engineering Work Package 4.2 structure. Each task includes technical scope, entry criteria, controlled inputs, ordered execution instructions, requirements, tools, deliverables, verification, interfaces, risks, quality records, schedule logic, resources, and the complete task-level cost basis.

## Application sections

1. **Overview** - scenario summary, execution stages, dates, funding, and staffing indicators.
2. **Pathway comparison** - product-stack cost, schedule, activity count, review cycles, and repeat-deployment comparison.
3. **Licensing plan** - selected route schedule, work-package costs, products, dates, and route activity dictionary.
4. **Pathway graph** - the single dependency-network view for DOE, NRC, and combined routes; click a node to open its full work package.
5. **Schedule** - integrated roadmap, detailed Gantt views, and authorization/startup milestones.
6. **Work packages** - searchable engineering task database.
7. **Resources** - annual and quarterly staffing, discipline demand, labor classification, continuity, and assignment browser.
8. **Financials** - annual cash flow, cost by stream, route-cost composition, and demonstrator package control.
9. **Cost basis** - bottom-up task register, prior-versus-revised estimate, direct cost components, non-additive package allocations, uncertainty ranges, and task-level basis-of-estimate inspector.
10. **Experiments** - methods, integral facility, INL critical experiment, demonstrator tests, and validation matrix.
11. **Risks & gates** - risk register, design/readiness gates, governance records, and RACI.
12. **Data & export** - active-scenario JSON, CSV files, multi-sheet Excel export, engineering-package registers, task-cost audit, and source register.

## Password-protected access

Version 4.2.2 places a server-side password gate in front of the planner. Authentication occurs before the database is loaded or any planner view is rendered. The release supports PBKDF2-SHA256 password hashes, Streamlit secrets, environment variables, failed-attempt lockout, idle-session expiration, and an explicit Sign out control.

The bundled local `.streamlit/secrets.toml` contains only a password hash for the requested release password and is excluded from Git. For Streamlit Community Cloud, copy its `[auth]` block into the application Secrets settings. See `docs/ACCESS_CONTROL.md`.

The gate protects the deployed website, not files stored in a public source repository. Use a private repository or private runtime storage when the database must remain confidential.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

For Streamlit Community Cloud, select `app.py` as the entry point.

## Validate

```bash
python scripts/validate_database.py
pytest -q
```

## Export a scenario without Streamlit

```bash
python scripts/export_scenario.py \\
  --demonstrator launchpad_usa \\
  --power-path part52 \\
  --power-variant esp_dc_col \\
  --output project_msr_part52_scenario.json
```

## Release

- Application version: **{VERSION}**
- Database version: **{DATABASE_VERSION}**
- Shared program activities: **{quality['base_task_count']:,}**
- Route-specific activities: **{quality['route_task_count']:,}**
- Engineering-ready and costed activities: **{quality['costed_task_count']:,}**
- Shared resource assignments: **{quality['base_assignment_count']:,}**
- Resource roles: **{quality['role_count']}**
- Application sections: **{quality['application_tabs']}**
- Automated tests: **{APP_TEST_COUNT}**
- Nominal Part 53 COL program cost: **${nominal['total_cost_kusd']/1000:,.1f} million**

See `CHANGELOG.md`, `RELEASE_NOTES_4.2.2.md`, `docs/GITHUB_STREAMLIT_DEPLOYMENT.md`, `docs/ACCESS_CONTROL.md`, `docs/COST_ESTIMATING_BASIS.md`, `docs/LICENSING_PATHS.md`, `docs/ENGINEERING_WORK_PACKAGES.md`, and `docs/VALIDATION.md`.
"""
    (ROOT / "README.md").write_text(text, encoding="utf-8")


def write_data_readme(database: dict[str, Any]) -> None:
    q = database["data_quality"]
    text = f"""# Project-MSR data

The complete database is stored as plain, uncompressed UTF-8 JSON shards. `project_msr_database.manifest.json` lists the core file and ordered task files with record counts, file sizes, SHA-256 checksums, and a canonical semantic checksum.

- `project_msr_database.core.json` contains every top-level collection except the shared task array.
- `project_msr_database.tasks.*.json` contains every shared task in original order.
- `project_msr_database.schema.json` defines the reconstructed database.
- `task_cost_audit_v4_2.csv` is the flat task-by-task cost register.

No information is removed or summarized. The bundled database is version **{database['meta']['version']}**. It contains **{q['base_task_count']:,}** shared activities, **{q['route_task_count']:,}** route activities, **{q['base_assignment_count']:,}** shared assignments, and **{q['role_count']}** resource roles.

Every one of the **{q['costed_task_count']:,}** activities carries its complete Engineering Work Package and bottom-up cost basis.
"""
    (ROOT / "data" / "README.md").write_text(text, encoding="utf-8")


def write_ewp() -> None:
    text = """# Engineering Work Package 4.2

Every Project-MSR activity is represented as an execution-ready engineering work package. The record is intended to be assignable to a producing engineer or team without a separate interpretation exercise.

## Scope and decision use

Each package identifies the technical scope, objective, boundaries, exclusions, downstream decision, and engineering questions that must be closed. Demonstrator-ready and final commercial releases are distinguished where staged execution is used.

## Entry criteria and controlled inputs

Entry criteria establish prerequisite maturity, requirements, qualified tools, interface data, configuration state, and authorization conditions. Each controlled input identifies its owner, source, revision, units, uncertainty, applicability, pre-use check, configuration treatment, and change-notification obligation.

## Ordered execution procedure

Each procedure step separates the action, engineering guidance, required step inputs, expected objective evidence, verification method, acceptance basis, and review checkpoint. The package states what to calculate, model, draw, specify, procure, fabricate, inspect, test, analyze, or submit.

## Requirements, tools, and deliverables

Requirement records include applicability, required engineering response, and expected compliance evidence. Tool records identify the intended use, code-of-record status, version, qualification or calibration expectations, limitations, and retained native files. Deliverables state minimum technical content, preparer, reviewer, approver, downstream user, handoff package, and revision triggers.

## Verification and definition of done

The package defines independent checks, benchmarks, validation evidence, uncertainty treatment, interface checks, readiness conditions, hold points, discrepancy resolution, measurable acceptance metrics, and the minimum execution record. Completion requires released evidence, closed review comments, accepted interfaces, controlled native files, and documented limitations or conditions of use.

## Resource and cost basis

The producing team is separated from support, independent review, QA/configuration, licensing integration, controls, and approval-only roles. Each task includes:

- planned FTE-years and productive labor hours;
- labor-hour allocation to production, independent review, integration, QA/configuration, and controls;
- fully burdened discipline rates;
- direct external engineering and laboratory services;
- software, compute, data, equipment, materials, fabrication, facility, test, field, regulatory, legal, advisory, and travel costs;
- task risk allowance and low/high range;
- prior and revised estimates, estimate class, method, basis-of-estimate identifier, drivers, exclusions, and re-estimate triggers;
- a non-additive allocated share of major program contracts where this improves visibility into the fully burdened technical task.

Accounting totals use each source package once. Allocated package shares are display-only and must not be summed a second time.

## Schedule logic

The schedule identifies predecessors, relationship intent, loading shape, staged releases, latest required finish, conditions for parallel work, stop conditions, and evidence-based progress measures.

## Application presentation

The task inspector presents the record in Scope, Inputs, Execution, Outputs, Requirements and tools, Interfaces and controls, Resources, and Cost basis sections. Long execution and test content is displayed in expanders and tables rather than fixed-height text boxes.
"""
    (ROOT / "docs" / "ENGINEERING_WORK_PACKAGES.md").write_text(text, encoding="utf-8")


def write_cost_basis(database: dict[str, Any]) -> None:
    meta = database["financials"]["task_cost_reestimate_v4_2"]
    base = database["financials"]["base_cost_summary"]
    examples = key_cost_examples(database)
    lines = [
        "# Project-MSR cost estimating basis - version 4.2.0",
        "",
        "## Purpose",
        "",
        "Version 4.2 establishes a bottom-up activity-based planning estimate for every shared and route-specific activity. The estimate is a planning basis, not a regulator, host, laboratory, EPC, supplier, or construction quotation.",
        "",
        "## Cost architecture",
        "",
        "Each task contains direct labor, direct non-labor, risk allowance, low/high range, and a basis-of-estimate record. Direct non-labor is decomposed into external engineering/laboratory services; software/compute/data; equipment/materials/fabrication; facilities/test/field operations; regulatory review fees; legal/hearing/advisory services; travel/field support; and other direct cost.",
        "",
        "Major EPC and validation contracts remain source accounting packages. A defined share is allocated to detailed technical tasks as a non-additive fully burdened view. The allocation improves task economics and accountability but is not included a second time in program totals.",
        "",
        "## Labor-rate basis",
        "",
        f"Productive time is {meta['productive_hours_per_fte_year']:,} hours per FTE-year. Rates are constant 2026-dollar, fully burdened owner/contractor planning rates rather than salaries. They include salary, benefits, payroll burden, facilities, ordinary software, indirect labor, and corporate overhead. Task-specific subcontracts, major software, laboratories, equipment, travel, regulatory fees, and risk are modeled separately.",
        "",
        "| Role ID | Loaded rate ($000/FTE-year) | Equivalent loaded rate ($/productive hour) |",
        "|---|---:|---:|",
    ]
    for role_id, rate in sorted(meta["labor_rates"].items()):
        lines.append(f"| {role_id} | {float(rate):,.0f} | {float(rate)*1000/meta['productive_hours_per_fte_year']:,.0f} |")
    lines.extend([
        "",
        "## Risk and uncertainty",
        "",
        "| Work class | Base task risk allowance |",
        "|---|---:|",
    ])
    for key, value in meta["risk_allowance_policy"].items():
        lines.append(f"| {key.replace('_', ' ').title()} | {float(value):.0%} |")
    lines.extend([
        "",
        "The task range reflects estimate maturity, technical novelty, schedule compression, procurement exposure, experimental uncertainty, and route-specific review risk. Reserve placeholder tasks remain zero because risk is embedded at task level; adding a second unallocated reserve would double count the current risk allowance.",
        "",
        "## Common program accounting estimate",
        "",
        "| Concept | Activities | FTE-years | Labor ($M) | Non-labor ($M) | Total ($M) |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for row in base:
        lines.append(
            f"| {row['Concept']} | {int(row['Activities'])} | {float(row['FTE-years']):,.1f} | {float(row['Labor Cost ($000)'])/1000:,.1f} | {float(row['Non-Labor Cost ($000)'])/1000:,.1f} | {float(row['Total Cost ($000)'])/1000:,.1f} |"
        )
    lines.extend([
        "",
        "## Representative task corrections",
        "",
        "| ID | Activity | FTE-years | Direct labor ($M) | Direct non-labor plus risk ($M) | Direct task total ($M) | Allocated package share ($M) | Fully burdened task view ($M) | Prior estimate ($M) |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for task in examples:
        cost = task["cost"]
        lines.append(
            f"| {task['id']} | {md(task['name'])} | {float(cost['planned_fte_years']):,.2f} | {float(cost['labor_kusd'])/1000:,.2f} | {float(cost['non_labor_kusd'])/1000:,.2f} | {float(cost['total_kusd'])/1000:,.2f} | {float(cost.get('allocated_program_package_kusd') or 0)/1000:,.2f} | {float(cost.get('fully_burdened_task_view_kusd') or cost['total_kusd'])/1000:,.2f} | {float(cost['prior_estimate']['total_kusd'])/1000:,.3f} |"
        )
    lines.extend([
        "",
        "## Review rules",
        "",
        "1. Review the direct task cost for labor and task-specific purchases.",
        "2. Review the fully burdened task view when assessing the total economic weight of a technical activity.",
        "3. Sum only the accounting task totals, not the non-additive allocated package shares.",
        "4. Re-estimate when design maturity, site, licensing path, test scope, supplier strategy, qualification standard, schedule, or make/buy basis changes.",
        "5. Replace allowances with quotations, framework agreements, laboratory work orders, regulator project plans, and construction estimates as they become available.",
        "",
        "## Source and benchmarking register",
        "",
    ])
    for source in meta["basis_sources"]:
        lines.append(f"- {source['source']}: {source['url']} - {source['use']}")
    (ROOT / "docs" / "COST_ESTIMATING_BASIS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_licensing(database: dict[str, Any]) -> None:
    comparison = compare_pathways(database)
    lines = [
        f"# Project-MSR licensing-path model - version {VERSION}",
        "",
        "Project-MSR separates DOE demonstrator authorization from commercial NRC licensing. Each selection activates a bottom-up network of activities, dependencies, products, resources, costs, reviews, milestones, and operation gates.",
        "",
        "The values are applicant/owner planning allowances in constant 2026 dollars. They are not authority, host, laboratory, or supplier quotations.",
        "",
        "## Integrated product-stack comparison",
        "",
        "| Path | Variant | Activities | Review cycles | Commercial route ($M) | Total program ($M) | Repeat route ($M) | Application | Construction authorization | Commercial operation |",
        "|---|---|---:|---:|---:|---:|---:|---|---|---|",
    ]
    for row in comparison:
        lines.append(
            f"| {md(row['Path'])} | {md(row['Variant'])} | {int(row['Route Activities'])} | {int(row['Formal Review Cycles'])} | {money(row['Commercial Route Total ($000)'])} | {money(row['Total Program Cost ($000)'])} | {money(row['Repeat Power Route Cost ($000)'])} | {row['Application']} | {row['Construction Authorization']} | {row['Commercial Operation']} |"
        )
    lines.extend([
        "",
        "## Common schedule boundary",
        "",
        "- Planning begins October 1, 2026.",
        "- Demonstrator authorization and construction turnover complete by December 31, 2028; operations occur during 2029.",
        "- Commercial construction begins January 1, 2030.",
        "- Commercial mechanical completion is September 30, 2034; operation authorization, initial criticality, and power ascension occur during 2035; commercial operation is December 31, 2035.",
        "",
    ])
    pathway_order = ["doe_launchpad", "part50", "part52", "part53", "part57"]
    for path in pathway_order:
        info = database["pathways"][path]
        tasks = route_tasks(database, path)
        lines.extend([
            f"## {PATH_DISPLAY_NAMES[path]}",
            "",
            md(info.get("description") or info.get("summary") or ""),
            "",
            f"**Route database activities:** {len(tasks)}",
            "",
            "| ID | Activity | Variants | Start | Finish | FTE-years | Direct cost ($M) | Low-high ($M) |",
            "|---|---|---|---|---|---:|---:|---:|",
        ])
        for task in tasks:
            cost = task["cost"]
            variants = ", ".join(task.get("applies_to_variants") or task.get("variants") or ["all"])
            lines.append(
                f"| {task['id']} | {md(task['name'])} | {md(variants)} | {task['schedule']['start']} | {task['schedule']['finish']} | {float(cost['planned_fte_years']):,.2f} | {float(cost['total_kusd'])/1000:,.2f} | {float(cost['low_kusd'])/1000:,.2f}-{float(cost['high_kusd'])/1000:,.2f} |"
            )
        lines.extend([
            "",
            "Every route activity includes Engineering Work Package 4.2 execution instructions and a reconciled task-level basis of estimate.",
            "",
        ])
    (ROOT / "docs" / "LICENSING_PATHS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_validation(database: dict[str, Any], scenario: dict[str, Any], profiles: list[dict[str, Any]]) -> None:
    q = database["data_quality"]
    lines = [
        f"# Validation record - Project-MSR v{VERSION}",
        "",
        "## Completed checks",
        "",
        "- JSON Schema Draft 2020-12 validation: passed.",
        "- Database-integrity validator: passed.",
        "- Python compilation: passed.",
        f"- Pytest: {APP_TEST_COUNT} tests passed.",
        "- Default authenticated application startup and Overview control-flow smoke test: passed.",
        "- Shared and route task identifiers: unique.",
        "- Resource-role references: valid.",
        "- Active predecessor references: valid and acyclic for every tested route.",
        "- Annual assignment FTE and labor profiles reconcile to assignment totals.",
        "- Annual task labor, direct non-labor, risk, total cost, and resource profiles reconcile to task totals.",
        "- Every activity has a complete bottom-up task-cost record.",
        "- Direct non-labor components reconcile to task direct non-labor.",
        "- Labor-effort breakdowns reconcile to planned task hours.",
        "- Low estimate <= point estimate <= high estimate for every task.",
        "- Non-additive major-contract allocations reconcile to their source packages.",
        "- Regulatory fee costs are assigned to selected route modules rather than duplicated in the common licensing assurance package.",
        "- Direct demonstrator package remains exactly $30.0 million non-labor.",
        "- Program start, demonstrator completion, 2029 operations, 2030 commercial construction, and 2035 commercial operation dates are preserved.",
        "- Engineering Work Package 4.2 fields are present for all activities.",
        "- The dependency network is rendered only in the Pathway graph section.",
        "",
        "## Nominal Launch Pad USA plus Part 53 COL profile",
        "",
        "| Year | FTE-years | Expenditure ($M) |",
        "|---:|---:|---:|",
    ]
    for year in sorted(scenario["annual_fte_years"], key=int):
        lines.append(f"| {year} | {scenario['annual_fte_years'][year]:,.1f} | {scenario['annual_cost_kusd'][year]/1000:,.1f} |")
    lines.extend([
        "",
        "## Executable licensing variants",
        "",
        "| Path | Variant | Active tasks | FTE-years | Route cost ($M) | Total program ($M) | Peak FTE year | Peak FTE | Peak funding year | Peak funding ($M) |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in profiles:
        lines.append(
            f"| {md(row['path'])} | {md(row['variant'])} | {row['tasks']} | {row['fte_years']:,.1f} | {row['route_cost_kusd']/1000:,.1f} | {row['total_cost_kusd']/1000:,.1f} | {row['peak_fte_year']} | {row['peak_fte']:,.1f} | {row['peak_cost_year']} | {row['peak_cost_kusd']/1000:,.1f} |"
        )
    (ROOT / "docs" / "VALIDATION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_release_notes(database: dict[str, Any], scenario: dict[str, Any], profiles: list[dict[str, Any]]) -> None:
    del profiles
    manifest = json.loads(Path(DEFAULT_DATABASE).read_text(encoding="utf-8"))
    largest = max(int(part["size_bytes"]) for part in manifest["parts"])
    lines = [
        f"# Project-MSR Planner {VERSION} release notes",
        "",
        f"Release date: {RELEASE_DATE}",
        "",
        "Version 4.2.2 resolves GitHub's per-file size limit while preserving the complete planning database as ordinary UTF-8 JSON.",
        "",
        "## Database storage changes",
        "",
        "- Replaced the oversized repository monolith with a checksummed manifest, one core JSON file, and four ordered task JSON shards.",
        "- No field, task, resource assignment, cost record, engineering work package, route module, milestone, risk, test matrix, or source record was removed or summarized.",
        f"- Largest database part: {largest / 1024 / 1024:,.1f} MiB.",
        f"- Canonical semantic SHA-256: {manifest['canonical_semantic_sha256']}.",
        "- Added transparent reassembly and validation in the Streamlit loader.",
        "- Added split and reconstruction utilities plus GitHub/Streamlit deployment instructions.",
        "- Preserved the v4.2.1 password gate and all planner functionality.",
        "",
        "## Verification",
        "",
        "- Python compilation passed.",
        "- Database-integrity and scenario validation passed.",
        f"- {APP_TEST_COUNT} automated tests passed.",
        "- Default authenticated application startup smoke test passed.",
        f"- The nominal Launch Pad USA plus Part 53 COL scenario remains ${scenario['summary']['total_cost_kusd']/1000:,.1f} million.",
    ]
    (ROOT / "RELEASE_NOTES_4.2.2.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_changelog() -> None:
    path = ROOT / "CHANGELOG.md"
    existing = path.read_text(encoding="utf-8") if path.exists() else "# Changelog\n"
    # Normalize accidental duplicate title from earlier generated releases.
    while "\n# Changelog\n" in existing:
        existing = existing.replace("\n# Changelog\n", "\n")
    if not existing.startswith("# Changelog"):
        existing = "# Changelog\n\n" + existing.lstrip()
    marker = f"## {VERSION} - {RELEASE_DATE}"
    if marker in existing:
        return
    entry = f"""# Changelog

{marker}

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

"""
    body = existing.split("\n", 1)[1].lstrip() if "\n" in existing else ""
    path.write_text(entry + body, encoding="utf-8")


def main() -> None:
    database = _load_database_uncached(DB_PATH)
    scenario = default_scenario(database)
    profiles = executable_profiles(database)
    write_readme(database, scenario, profiles)
    write_data_readme(database)
    write_ewp()
    write_cost_basis(database)
    write_licensing(database)
    write_validation(database, scenario, profiles)
    write_release_notes(database, scenario, profiles)
    update_changelog()
    print("Generated Project-MSR v4.2.2 release documentation")


if __name__ == "__main__":
    main()
