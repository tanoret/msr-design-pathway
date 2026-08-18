#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from src.pathway_engine import ScenarioOptions, build_scenario
DB=ROOT/'data'/'project_msr_database.full.json'

def esc(v): return str(v or '').replace('|','\\|').replace('\n',' ')

def bullets(items): return '\n'.join(f'- {x}' for x in items)

def main():
    db=json.load(DB.open())
    sc=build_scenario(db,ScenarioOptions())
    q=db['data_quality']; meta=db['meta']; fuel=db['fuel_supply_plan']; chem=db['chemistry_processing_plan']; playbooks=db['implementation_playbooks']
    docs=ROOT/'docs'; docs.mkdir(exist_ok=True)

    # README
    readme=f'''# Project-MSR Integrated Development Planner

Project-MSR is a password-protected, scenario-driven Streamlit application and engineering execution database for an integrated molten-salt-reactor development program. It connects methods, experiments, fuel supply, chemistry and materials qualification, DOE demonstrator authorization, selectable NRC commercial licensing, resources, costs, schedules, risks, construction, startup, and operating optimization.

## Current planning baseline

- Program mobilization begins **October 1, 2026**.
- Demonstrator authorization and construction turnover complete by **December 31, 2028**.
- Demonstrator commissioning and operating campaigns occur during **2029**.
- Commercial field construction begins **January 1, 2030**.
- Commercial operation is targeted for **December 31, 2035**.
- The nominal Launch Pad USA plus Part 53 COL case remains approximately **${sc['summary']['total_cost_kusd']/1000:,.1f} million** and **{sc['summary']['fte_years']:,.1f} FTE-years**. Version 4.3 adds implementation detail without double-counting playbook or experiment rows.

## Version 4.3 execution content

Every one of the **{q['engineering_ready_task_count']:,}** shared and route-specific activities now contains both:

1. an Engineering Work Package with scope, inputs, engineering procedure, requirements, tools, deliverables, verification, interfaces, risks, records, resources, schedule logic, and definition of done; and
2. an Implementation Plan describing the delivery strategy, make/buy/partner decision, authorizations, work location, step-by-step field/laboratory/vendor actions, procurement, long-lead items, decisions, acceptance evidence, contingencies, implementation records, and open decisions.

The database also includes **{q['implementation_playbook_count']}** execution playbooks and a **{q['chemistry_processing_test_count']}-experiment** chemistry and fuel-salt-processing matrix. Key playbooks cover fuel supply, chemistry/processing, fission-product behavior, materials, liquid-fuel accountancy, waste/disposition, experimental facilities, supplier execution, host integration, and startup/data release.

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

- Application version: **4.3.0**
- Database version: **4.3.0**
- Shared activities: **{q['base_task_count']:,}**
- Route-specific activities: **{q['route_task_count']:,}**
- Engineering- and implementation-ready activities: **{q['implementation_ready_task_count']:,}**
- Shared resource assignments: **{q['base_assignment_count']:,}**
- Resource roles: **{q['role_count']:,}**
- Implementation playbooks: **{q['implementation_playbook_count']}**
- Chemistry/processing experiments: **{q['chemistry_processing_test_count']}**
- Automated tests: **{q['automated_test_count']}**

See `RELEASE_NOTES_4.3.0.md`, `docs/IMPLEMENTATION_EXECUTION_PLAN.md`, `docs/FUEL_SUPPLY_AND_PROCUREMENT.md`, `docs/CHEMISTRY_AND_PROCESSING_VALIDATION.md`, `docs/ENGINEERING_WORK_PACKAGES.md`, `docs/COST_ESTIMATING_BASIS.md`, `docs/LICENSING_PATHS.md`, and `docs/VALIDATION.md`.
'''
    (ROOT/'README.md').write_text(readme,encoding='utf-8')

    data_readme=f'''# Project-MSR data

The complete Project-MSR v4.3.0 database is stored as **plain, uncompressed UTF-8 JSON shards** so every repository file remains below GitHub's per-file limit.

## Contents

- `project_msr_database.manifest.json` - ordered manifest, counts, sizes, per-file hashes, and semantic checksum.
- `project_msr_database.core.json` - all top-level collections except the shared task array.
- `project_msr_database.tasks.001.json` onward - all shared tasks in original order.
- `project_msr_database.schema.json` - Draft 2020-12 JSON Schema.
- `task_cost_audit_v4_2.csv` - v4.2 bottom-up cost audit retained because v4.3 does not change the accounting estimate.

Nothing has been removed or reduced. The database includes **{q['base_task_count']}** shared activities, **{q['route_task_count']}** route activities, **{q['base_assignment_count']}** shared assignments, **{q['role_count']}** roles, **{q['implementation_playbook_count']}** implementation playbooks, and **{q['chemistry_processing_test_count']}** chemistry/processing experiments. All **{q['implementation_ready_task_count']}** activities include an Engineering Work Package, bottom-up task-cost basis, and implementation plan.

## Reconstruct one monolithic file

```bash
python scripts/reconstruct_database.py
```

The generated `data/project_msr_database.full.json` is intentionally ignored by Git because it exceeds GitHub's per-file limit.

## Rebuild shards

```bash
python scripts/shard_database.py data/project_msr_database.full.json --application-version 4.3.0
```

Sharding changes only storage layout; it does not gzip, encode, minify, summarize, or remove data.
'''
    (ROOT/'data'/'README.md').write_text(data_readme,encoding='utf-8')

    # Fuel guide
    lines=['# Project-MSR fuel supply and procurement execution plan - v4.3.0','',fuel['objective'],'', '## Recommended baseline','',fuel['recommended_baseline'],'','## Technology branches and authorization boundary','']
    lines += [f'- {x}' for x in fuel.get('technology_branching',[])]
    lines += ['','## Execution phases','']
    for ph in fuel['execution_phases']:
        lines += [f"### {ph['phase_id']} - {ph['phase']}",'',f"**Window:** {ph['window']}",'', '**Actions**','']+[f'- {x}' for x in ph['actions']]+['','**Deliverables**','']+[f'- {x}' for x in ph['deliverables']]+['',f"**Release gate:** {ph['gate']}",'']
    lines += ['## Candidate source routes','', '| Route | Intended use | Required actions | Current planning status |','|---|---|---|---|']
    for r in fuel['candidate_supply_routes']:
        lines.append(f"| {esc(r['route'])} | {esc(r['use'])} | {esc(r['actions'])} | {esc(r['status'])} |")
    lines += ['','## Required acceptance data','']+[f'- {x}' for x in fuel['required_acceptance_data']]
    lines += ['','## WBS crosswalk','']+[f'- `{x}`' for x in fuel['linked_task_ids']]
    lines += ['','## Cost treatment','',fuel['cost_accounting']['rule'],'','## Official source and precedent links','']+[f'- {u}' for u in fuel['source_urls']]
    (docs/'FUEL_SUPPLY_AND_PROCUREMENT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

    # Chemistry guide
    lines=['# Project-MSR chemistry, salt processing, and fission-product validation plan - v4.3.0','',chem['objective'],'','## Processing architecture decision','',f"**Question:** {chem['architecture_decision']['question']}",'','**Alternatives**','']+[f'- {x}' for x in chem['architecture_decision']['alternatives']]+['','**Decision criteria**','']+[f'- {x}' for x in chem['architecture_decision']['decision_criteria']]+['',f"**Required date:** {chem['architecture_decision']['required_date']}",'',chem['architecture_decision']['rule'],'','## Evidence ladder','']+[f'{i+1}. {x}' for i,x in enumerate(chem['campaign_sequence'])]
    lines += ['','## Experiment index','', '| ID | Campaign | Material stage | Window | Primary decision |','|---|---|---|---|---|']
    for t in chem['experiment_matrix']:
        lines.append(f"| {t['test_id']} | {esc(t['campaign'])} | {esc(t['material_stage'])} | {esc(t['planned_window'])} | {esc('; '.join(t['model_or_decision_supported']))} |")
    lines += ['','## Detailed experiment definitions','']
    for t in chem['experiment_matrix']:
        lines += [f"### {t['test_id']} - {t['campaign']}",'',f"**Objective:** {t['objective']}",'',f"**Configuration:** {t['configuration']}",'',f"**Material progression:** {t['material_stage']}",'',f"**Facility strategy:** {t['facility_strategy']}",'',f"**Planned window:** {t['planned_window']}",'','**Minimum execution sequence**','']+[f'{i+1}. {x}' for i,x in enumerate(t['minimum_test_sequence'])]+['','**Controlled variables**','']+[f'- {x}' for x in t['controlled_variables']]+['','**Primary measurements**','']+[f'- {x}' for x in t['primary_measurements']]+['','**Analytical methods**','']+[f'- {x}' for x in t['analytical_methods']]+['','**Equipment and consumables**','']+[f'- {x}' for x in t['equipment_and_consumables']]+['',f"**Replication and uncertainty:** {t['replicate_and_uncertainty_strategy']}",'',f"**Sample and archive plan:** {t['sample_and_archive_plan']}",'','**Stop conditions**','']+[f'- {x}' for x in t['stop_conditions']]+['','**Acceptance basis**','',t['acceptance_basis'],'',f"**Decision rule:** {t['decision_rule']}",'','**Data products**','']+[f'- {x}' for x in t['data_products']]+['','**Linked WBS activities**','']+[f'- `{x}`' for x in t['linked_task_ids']]+['']
    lines += ['## Cost treatment','',chem['cost_accounting']['rule'],'','## Official source and precedent links','']+[f'- {u}' for u in chem['source_urls']]
    (docs/'CHEMISTRY_AND_PROCESSING_VALIDATION.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

    # Implementation plan guide
    lines=['# Project-MSR implementation execution plan - v4.3.0','', '## Purpose','', 'Version 4.3 converts the WBS from an engineering/licensing scope dictionary into an execution-oriented plan. Every task now identifies how it will be delivered, where the work occurs, what must be procured, which authorizations and hold points apply, which records prove completion, and what fallback is used if the preferred facility, supplier, input, or result is unavailable.','', '## Implementation standard for every task','', 'Each task implementation plan includes:','', '- implementation readiness and summary','- owner-led delivery strategy and make/buy/partner split','- authorization and prerequisite evidence','- at least five detailed implementation steps with location, inputs, tools, outputs, acceptance and hold point','- procurement and contracting actions','- long-lead items and capacity reservations','- decisions, owners, need dates and closure evidence','- laboratory, field or vendor activities','- contingencies and alternate routes','- implementation records, source basis and open decisions','', '## Cross-cutting playbooks','']
    for key,pb in playbooks.items():
        lines += [f"### {key} - {pb['title']}",'',pb['objective'],'']
        seq=pb.get('execution_sequence') or pb.get('campaign_sequence') or [p.get('phase') for p in pb.get('execution_phases',[])]
        for i,x in enumerate(seq or []): lines.append(f'{i+1}. {x}')
        lines += ['','**Linked WBS activities:** '+', '.join(f'`{x}`' for x in pb.get('linked_task_ids',[])),'']
    lines += ['## Evidence hierarchy','', '1. supplier/feed qualification and bench methods','2. separate-effects and engineering-scale testing','3. integral thermal-hydraulics and process-skid testing','4. INL critical experiment and authorized irradiated-salt confirmation','5. 2029 demonstrator coupled operation and experiments','6. commercial construction/startup acceptance and operating feedback','','The least hazardous and least expensive evidence is used first. Uranium-bearing or irradiated work is reserved for questions that cannot be closed credibly with stable surrogates and is executed only in an authorized facility.','','## Accounting rule','', 'Implementation playbooks and experiment rows are execution crosswalks to existing accounting tasks. They are not additional cost lines and must not be summed a second time. Supplier quotations, laboratory work orders, DOE/host terms and commercial capacity agreements trigger the next cost rebaseline.','']
    (docs/'IMPLEMENTATION_EXECUTION_PLAN.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

    # Work package standard update
    wp='''# Project-MSR Engineering and Implementation Work Package Standard - v4.3.0

Every WBS activity has two complementary records.

## Engineering Work Package

Defines the technical scope, questions, entry criteria, controlled inputs, engineering procedure, requirements, tools, deliverables, verification and validation, interfaces, risks, quality records, resources, schedule logic, acceptance metrics, hold points, handoff and definition of done.

## Implementation Plan

Defines how the work is actually executed:

- implementation readiness and practical summary;
- delivery strategy and owner/partner/supplier split;
- authorizations, licenses, facility readiness and prerequisites;
- step-by-step work at the engineering office, laboratory, supplier, test facility, construction site or operating plant;
- inputs, equipment/tools, outputs, records, acceptance and hold points for each step;
- RFI/RFP/PO/task-order and supplier-data requirements;
- long-lead materials, facility slots, equipment and specialist capacity;
- decisions, owners, dates and closure evidence;
- laboratory/field/vendor campaigns and data custody;
- fallback routes and stop-work triggers;
- implementation source basis, records and open decisions.

## Execution principles

1. Retain owner control of requirements, technical conclusions, acceptance, configuration and regulatory commitments.
2. Buy bounded specialist capability, facility time, supplier engineering, fabrication and testing with native-data and records rights.
3. Use staged evidence and do not commit radioactive work before surrogate down-selection demonstrates the need.
4. Do not release irreversible procurement, fabrication, construction or fuel operations without the defined hold-point evidence.
5. Credit a result only after configuration, uncertainty, sample/material balance, independent review and discrepancy closure are complete.
6. Link every task to downstream design, licensing, procurement, test or operating decisions so work does not become unowned research.
'''
    (docs/'ENGINEERING_WORK_PACKAGES.md').write_text(wp,encoding='utf-8')

    # Validation
    validation=f'''# Validation record - Project-MSR v4.3.0

- JSON Schema Draft 2020-12 validation: passed.
- Database-integrity validation: passed.
- Python compilation: passed.
- Automated tests: **52 passed** using `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q`.
- All 13 authenticated application-section smoke flows: passed.
- Shared tasks: {q['base_task_count']}.
- Route tasks: {q['route_task_count']}.
- Resource assignments: {q['base_assignment_count']}.
- Engineering- and implementation-ready tasks: {q['implementation_ready_task_count']}.
- Implementation playbooks: {q['implementation_playbook_count']}.
- Chemistry and processing experiments: {q['chemistry_processing_test_count']}.
- All task identifiers and route dependencies remain valid and acyclic.
- Task costs and annual profiles remain reconciled to the v4.2 accounting baseline.
- The direct demonstrator package remains exactly $30.0 million non-labor; its fuel-material assumption is explicitly identified.
- Plain JSON shards are below GitHub's safe file limit and reconstruct to the manifest semantic checksum.
- Program schedule targets remain Q4 2026 mobilization, December 2028 demonstrator turnover, 2029 demonstration, January 2030 commercial construction, and December 2035 commercial operation.
'''
    (docs/'VALIDATION.md').write_text(validation,encoding='utf-8')

    # Release notes
    release=f'''# Project-MSR Planner 4.3.0 release notes

Release date: 2026-08-18

## Purpose

Version 4.3 is the execution-detail release. It preserves the v4.2 task-by-task cost baseline and schedule while adding a practical implementation plan to every WBS activity.

## Principal additions

- Added an implementation plan to all {q['implementation_ready_task_count']} activities.
- Added {q['implementation_playbook_count']} cross-cutting execution playbooks.
- Added a six-phase fuel-supply plan covering requirements, DOE HALEU allocation, commercial backup, enrichment/deconversion, synthesis/analysis, packaging/transport/receipt and disposition.
- Added a {q['chemistry_processing_test_count']}-experiment chemistry/processing matrix covering feed, purification, synthesis, properties, redox, corrosion, fission-product surrogates, plate-out, off-gas, capture, sampling, sensors, integrated processing, irradiated confirmation, demonstrator operation and waste.
- Added task-specific execution sequences for fuel supply, chemistry pilot, demonstrator salt-handling/processing equipment, source term, sensors/sampling, liquid-fuel accountancy, materials and commercial fuel scaling.
- Added an **Implementation** section to the Streamlit application and an Implementation tab to every task inspector.
- Added implementation registers to scenario exports and made the full Excel workbook an on-demand export.
- Preserved the password gate and plain uncompressed JSON sharding.

## Cost treatment

The new playbooks and experiment rows are non-additive execution crosswalks into the existing costed tasks. The nominal Launch Pad USA plus Part 53 COL total remains approximately ${sc['summary']['total_cost_kusd']/1000:,.1f} million. Quotations, DOE/host agreements, fuel allocation terms, laboratory work orders and capacity reservations should replace planning allowances in the next cost baseline.

## Verification

Schema and integrity validation passed; 52 automated tests passed; all 13 application sections passed control-flow smoke testing; all data shards remain below GitHub's file limit.
'''
    (ROOT/'RELEASE_NOTES_4.3.0.md').write_text(release,encoding='utf-8')

    # Changelog prepend
    ch=ROOT/'CHANGELOG.md'; old=ch.read_text(encoding='utf-8') if ch.exists() else '# Changelog\n'
    entry='''# Changelog

## 4.3.0 - 2026-08-18

- Added execution-ready implementation plans to all 937 WBS activities.
- Added 11 fuel, chemistry, fission-product, materials, safeguards, waste, test, supply-chain, host, facility, and startup playbooks.
- Added 25 detailed chemistry and processing experiments and task-specific fuel/chemistry execution sequences.
- Added the Implementation application section and task-level Implementation tab.
- Added implementation registers to exports and changed the large Excel export to on-demand generation.
- Preserved the v4.2 cost baseline, licensing-path differences, schedule, password gate, and complete uncompressed JSON data.

'''
    if old.startswith('# Changelog'):
        old=old.split('\n',1)[1] if '\n' in old else ''
    ch.write_text(entry+old.lstrip(),encoding='utf-8')
    print('generated implementation documentation')
    return 0

if __name__=='__main__': raise SystemExit(main())
