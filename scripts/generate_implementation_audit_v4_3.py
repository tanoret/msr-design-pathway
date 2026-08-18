#!/usr/bin/env python3
"""Generate an implementation audit register and strategic closure register."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "project_msr_database.full.json"
OUT_CSV = ROOT / "data" / "implementation_task_audit_v4_3.csv"
OUT_MD = ROOT / "docs" / "IMPLEMENTATION_GAP_REGISTER.md"


def all_tasks(db: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
    yield from db.get("tasks", [])
    for module in db.get("pathway_modules", {}).values():
        yield from module.get("demonstrator", [])
        yield from module.get("power_reactor", [])


def main() -> None:
    db = json.loads(DB_PATH.read_text(encoding="utf-8"))
    tasks = list(all_tasks(db))
    fields = [
        "task_id", "task_name", "concept", "execution_stream", "phase", "start", "finish",
        "critical", "implementation_readiness", "quality_score", "implementation_summary",
        "linked_playbooks", "task_specific_tests", "implementation_steps", "authorizations",
        "procurement_actions", "long_lead_items", "decision_points", "field_lab_vendor_activities",
        "contingencies", "implementation_records", "open_decisions", "first_hold_point",
    ]
    rows = []
    for task in tasks:
        plan = task.get("implementation_plan", {})
        sched = task.get("schedule", {})
        steps = plan.get("implementation_steps", [])
        rows.append({
            "task_id": task.get("id", ""),
            "task_name": task.get("name", ""),
            "concept": task.get("concept", ""),
            "execution_stream": task.get("execution_stream", ""),
            "phase": task.get("phase", ""),
            "start": sched.get("start", ""),
            "finish": sched.get("finish", ""),
            "critical": sched.get("critical", False),
            "implementation_readiness": plan.get("implementation_readiness", ""),
            "quality_score": plan.get("implementation_quality_score", ""),
            "implementation_summary": plan.get("implementation_summary", ""),
            "linked_playbooks": "; ".join(plan.get("linked_playbooks", [])),
            "task_specific_tests": "; ".join(plan.get("task_specific_test_ids", [])),
            "implementation_steps": len(steps),
            "authorizations": len(plan.get("authorizations_and_prerequisites", [])),
            "procurement_actions": len(plan.get("procurement_and_contracting_actions", [])),
            "long_lead_items": len(plan.get("long_lead_items", [])),
            "decision_points": len(plan.get("decision_points", [])),
            "field_lab_vendor_activities": len(plan.get("field_lab_or_vendor_activities", [])),
            "contingencies": len(plan.get("fallbacks_and_contingencies", [])),
            "implementation_records": len(plan.get("implementation_records", [])),
            "open_decisions": len(plan.get("open_decisions", [])),
            "first_hold_point": steps[0].get("hold_point", "") if steps else "",
        })
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    strategic = [
        ("Salt family and fuel precursor form", "Select the carrier/fuel-salt family, fissile precursor form, composition envelope and operating redox/impurity limits before releasing final synthesis and salt-handling equipment.", "Physics, chemistry, materials and design authority", "2027-03-31", "Approved Fuel Material Requirements Specification and chemistry requirements baseline"),
        ("Demonstrator fuel source and ownership", "Obtain a contractually credible DOE HALEU allocation/ownership route and preserve a commercial enrichment/deconversion backup. Define title, use restrictions, transformation, return/disposition and liability.", "Program, DOE/host interface, fuel procurement and safeguards", "2027-09-30", "Conditional allocation/ownership agreement plus commercial capacity/option strategy"),
        ("Fuel-salt synthesis and analytical facility", "Select an authorized synthesis facility and independent analytical laboratory; qualify the process first with carrier/non-fissile material, then authorized qualification and production batches.", "Fuel/chemistry, QA, safeguards and host", "2027-09-30", "Facility qualification, work orders, qualified synthesis procedure and analytical methods"),
        ("Minimum salt-processing architecture", "Choose which preparation, sampling, monitoring, off-gas, particulate cleanup, targeted processing, drain/recovery, MC&A and waste functions are installed. Do not assume broad online reprocessing without a demonstrated need and authorization path.", "Systems, chemistry, safety analysis, safeguards, operations and design authority", "2027-12-31", "Approved processing architecture down-select and hazards/maintainability review"),
        ("Chemistry laboratory and experimental facility network", "Assign CHEM-01 through CHEM-25 to specific qualified facilities, reserve long-lead slots, define sample/data rights and ensure every waste stream has a disposition path before work begins.", "Chemistry program lead, procurement, QA and facility interfaces", "2027-06-30", "Facility capability matrix, executed work orders, sample/waste plan and integrated campaign schedule"),
        ("Irradiated-salt and hot-cell confirmation", "Secure the authorized INL/DOE facilities, sample transfer, analytical scope, radiological work controls, data rights and waste/disposition route needed for CHEM-22 and CHEM-23.", "INL interface, chemistry, radiation protection and safeguards", "2028-03-31", "Executed host/facility agreement and approved irradiation/hot-cell test plan"),
        ("Commercial fuel capacity and alternate route", "Reserve enrichment, deconversion, synthesis, analytical, packaging and transport capacity early enough to support 2035 operation and qualify an alternate for the most schedule-critical transformation.", "Commercial fuel procurement, fuel engineering and safeguards", "2029-06-30", "Capacity reservations/options, supplier qualification and contingency route"),
        ("Commercial first-article and continuing supply", "Define and accept consecutive first-article batches, production capability, package/transport/receipt readiness, makeup cadence, reserve stock and continuing supplier surveillance.", "Fuel/chemistry, operations, QA, safeguards and licensing", "2033-12-31", "Accepted first-article records, production readiness and continuing supply plan"),
    ]
    lines = [
        "# Project-MSR implementation closure register - v4.3.0",
        "",
        "The v4.3 baseline defines an executable path, but the following choices require real contracts, site/facility commitments, approved specifications or test results before the plan can be considered committed. They are not silently assumed closed.",
        "",
        "| Closure item | Work required | Accountable functions | Need date | Closure evidence |",
        "|---|---|---|---|---|",
    ]
    for item, work, owner, date, evidence in strategic:
        lines.append(f"| {item} | {work} | {owner} | {date} | {evidence} |")
    lines += [
        "",
        "## Execution rules",
        "",
        "1. Use stable nonradioactive salts and fission-product surrogates to screen concepts and qualify equipment wherever they can answer the engineering question.",
        "2. Conduct uranium-bearing and irradiated work only in facilities whose DOE, NRC or Agreement State authority and work controls cover the material and activity.",
        "3. Freeze pre-test predictions and acceptance metrics before releasing measured results to the model-development team.",
        "4. Reconcile salt, gas, deposits, filters/sorbents, samples, residues and waste to a controlled material balance for every credited chemistry or processing campaign.",
        "5. Do not install or credit a processing function solely because it is technically possible; require a safety, chemistry, safeguards, waste, availability or economic decision that needs it.",
        "6. Preserve raw native data, calibration, material/sample genealogy, as-tested configuration, uncertainty, independent review and discrepancy resolution for every qualified dataset.",
        "7. Rebaseline cost and schedule when DOE/host terms, fuel allocation, supplier capacity, facility work orders or production quotations replace the current planning assumptions.",
        "",
        "## Audit register",
        "",
        "The complete 937-row task implementation audit is stored at `data/implementation_task_audit_v4_3.csv` and is also available through the application Data & export section.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_CSV} ({len(rows)} rows) and {OUT_MD}")


if __name__ == "__main__":
    main()
