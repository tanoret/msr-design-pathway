#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]

from src.data_loader import DEFAULT_DATABASE, load_sharded_database

VERSION = "4.3.0"
EWP_VERSION = "4.3"

SOURCES = {
    "DOE_HALEU_PROGRAM": "https://www.energy.gov/ne/haleu-availability-program",
    "DOE_HALEU_ALLOCATION": "https://www.energy.gov/ne/us-department-energy-haleu-allocation-process",
    "DOE_HALEU_ENRICHMENT": "https://www.energy.gov/ne/haleu-enrichment-services",
    "DOE_HALEU_DECONVERSION": "https://www.energy.gov/ne/haleu-deconversion-services",
    "DOE_HALEU_TRANSPORT": "https://www.energy.gov/ne/haleu-transportation",
    "INL_MCRE_FUEL": "https://inl.gov/feature-story/idaho-lab-produces-first-ever-fuel-for-fast-molten-salt-reactor-experiment-opening-door-to-maritime-commercial-reactor-deployment/",
    "INL_MCRE_PROGRAM": "https://inl.gov/feature-story/the-heartbeat-of-progress-teamwork-fuels-first-of-a-kind-reactor-design-test/",
    "NRIC_LOTUS": "https://nric.inl.gov/lotus/",
    "NRIC_LAUNCHPAD_USA": "https://nric.inl.gov/launch-pad-usa/",
    "NRIC_LAUNCHPAD_INL": "https://nric.inl.gov/launch-pad-inl/",
    "ORNL_LSTL": "https://www.ornl.gov/project/liquid-salt-test-loop",
    "ORNL_FASTR": "https://www.ornl.gov/group/esd/projects",
    "ORNL_PURIFICATION": "https://www.ornl.gov/publication/engineering-scale-batch-purification-ternary-mgcl2-kcl-nacl-salt-using-thermal-and",
    "ORNL_REDOX": "https://www.ornl.gov/publication/redox-potential-control-molten-salt-systems-corrosion-mitigation",
    "ORNL_OFFGAS_MONITORING": "https://www.ornl.gov/publication/monitoring-noble-gases-xe-and-kr-and-aerosols-cs-and-rb-molten-salt-reactor-surrogate",
    "ORNL_XE_CAPTURE": "https://www.ornl.gov/publication/monitoring-xenon-capture-metal-organic-framework-using-laser-induced-breakdown",
    "ORNL_FP_CORROSION": "https://www.ornl.gov/publication/impact-europium-fission-product-surrogate-chromium-corrosion-molten-chloride-salt",
    "ORNL_MASS_ACCOUNTANCY": "https://www.ornl.gov/publication/dynamic-mass-accountancy-modeling-molten-salt-reactor-using-equilibrium-thermodynamics",
    "ORNL_MSRE_FP": "https://www.osti.gov/biblio/4077644",
    "NRC_PART70": "https://www.nrc.gov/reading-rm/doc-collections/cfr/part070/full-text",
    "NRC_PART71": "https://www.nrc.gov/reading-rm/doc-collections/cfr/part071/",
    "NRC_PART74": "https://www.nrc.gov/reading-rm/doc-collections/cfr/part074/",
    "NRC_FUEL_CYCLE_LICENSING": "https://www.nrc.gov/materials/fuel-cycle-fac/licensing",
}


def _months(start: str, finish: str) -> float:
    sy, sm, sd = map(int, start.split("-"))
    fy, fm, fd = map(int, finish.split("-"))
    return max(0.25, (fy - sy) * 12 + (fm - sm) + (fd - sd) / 30.4375)


def _role(task: dict[str, Any]) -> str:
    return str(task.get("responsible_role") or (task.get("engineering_work_package") or {}).get("resource_plan", {}).get("responsible_role") or "Assigned technical lead")


def _team(task: dict[str, Any]) -> list[str]:
    ewp = task.get("engineering_work_package") or {}
    team = list((ewp.get("resource_plan") or {}).get("core_producing_team") or task.get("execution", {}).get("core_producing_team") or [])
    return [str(item) for item in team if item]


def _common_step(step_id: str, action: str, task: dict[str, Any], *, location: str, inputs: list[str], tools: list[str], outputs: list[str], acceptance: str, hold_point: str = "") -> dict[str, Any]:
    return {
        "step_id": step_id,
        "action": action,
        "responsible_role": _role(task),
        "supporting_roles": _team(task),
        "work_location": location,
        "required_inputs": inputs,
        "detailed_guidance": (
            f"Execute this step for {task.get('id')} - {task.get('name')} using the released configuration and input register. "
            "Record the exact revision of every input, identify provisional assumptions before use, and stop work if a change could alter a safety, licensing, procurement, test, or acceptance conclusion."
        ),
        "tools_equipment": tools,
        "outputs_and_records": outputs,
        "acceptance_condition": acceptance,
        "hold_point": hold_point,
    }


def _generic_plan(task: dict[str, Any]) -> dict[str, Any]:
    ewp = task.get("engineering_work_package") or {}
    pattern = str(ewp.get("work_pattern") or "design_engineering")
    domain = str(ewp.get("primary_domain") or "systems_engineering")
    start = str((task.get("schedule") or {}).get("start") or "")
    finish = str((task.get("schedule") or {}).get("finish") or "")
    task_name = str(task.get("name") or "activity")
    responsible = _role(task)

    domain_location = {
        "chemistry": "Qualified chemistry laboratory, salt loop, hot cell, or host facility selected for the material hazard and evidence class",
        "materials": "Qualified materials laboratory, molten-salt loop, fabrication supplier, or hot-cell facility",
        "neutronics": "Controlled analysis environment and, where required, an authorized critical experiment facility",
        "thermal_hydraulics": "Controlled analysis environment, separate-effects rig, ITHF, or plant/test facility",
        "instrumentation_controls": "Engineering testbed, vendor factory, hardware-in-the-loop laboratory, and installed field configuration",
        "procurement_fabrication": "Qualified supplier facility with source surveillance and controlled receiving location",
        "construction_installation": "Authorized construction site and system turnover boundary",
        "site_environmental": "Selected site, qualified field contractor, analytical laboratory, and controlled GIS/data environment",
        "operations_maintenance": "Simulator, procedure-validation environment, installed plant, and work-management system",
        "licensing_authorization": "Controlled authoring/data room with regulator, host, legal, and technical interfaces",
    }.get(domain, "Responsible engineering organization, qualified supplier/laboratory, and controlled project data environment")

    base_steps = [
        _common_step(
            "IMP-01", "Issue the implementation brief and delivery strategy.", task,
            location="Project engineering organization",
            inputs=["approved task scope", "schedule need date", "downstream decision", "budget authorization", "applicable QA and licensing classification"],
            tools=["work-package template", "requirements database", "integrated schedule", "cost account"],
            outputs=["implementation brief", "delivery-model decision", "responsibility matrix", "assumption and open-item register"],
            acceptance="The producer, reviewer, approver, work location, delivery model, budget, schedule, interfaces, and objective evidence are assigned and approved.",
            hold_point="HP-I1 implementation authorization",
        ),
        _common_step(
            "IMP-02", "Verify the input, configuration, authorization, and facility readiness package.", task,
            location=domain_location,
            inputs=["controlled inputs listed in the engineering work package", "facility and supplier qualifications", "software/equipment calibration status", "permits and work controls"],
            tools=["input register", "configuration baseline", "supplier/facility audit records", "readiness checklist"],
            outputs=["input-readiness record", "facility/supplier acceptance record", "approved exceptions with closure dates"],
            acceptance="All decision-significant inputs and work controls are released, applicable, traceable, and within the qualified range, or explicitly bounded by approved restrictions.",
            hold_point="HP-I2 input and facility readiness",
        ),
    ]

    pattern_steps: dict[str, list[dict[str, Any]]] = {
        "analysis_model": [
            _common_step("IMP-03", "Build or update the code-of-record model and verification cases.", task, location=domain_location,
                         inputs=["controlled geometry/system representation", "material/property data", "boundary and initial conditions", "software release"],
                         tools=["qualified code of record", "independent calculation or confirmatory code", "version control and automated regression"],
                         outputs=["controlled model/input deck", "verification cases", "model applicability statement"],
                         acceptance="Model equations, discretization, numerical controls, conservation checks, and reference cases satisfy the approved method and software QA plan."),
            _common_step("IMP-04", "Execute nominal, limiting, sensitivity, and uncertainty cases.", task, location=domain_location,
                         inputs=["approved analysis matrix", "parameter distributions and correlations", "acceptance limits"],
                         tools=["batch execution environment", "uncertainty/sensitivity tools", "machine-readable post-processing"],
                         outputs=["run log", "result database", "sensitivity and uncertainty results", "margin tables"],
                         acceptance="The complete approved case matrix is executed without unresolved solver, conservation, convergence, or configuration errors."),
            _common_step("IMP-05", "Perform independent verification, benchmark comparison, and discrepancy resolution.", task, location=domain_location,
                         inputs=["model results", "benchmark/validation data", "independent-review plan"],
                         tools=["alternate calculation", "benchmark scripts", "review checklist"],
                         outputs=["independent verification record", "benchmark comparison", "discrepancy dispositions"],
                         acceptance="Independent review confirms reproducibility and that bias, uncertainty, limitations, and conditions of use are explicit.", hold_point="HP-I3 result release"),
        ],
        "test_experiment": [
            _common_step("IMP-03", "Issue the test plan, test article/configuration definition, and measurement uncertainty budget.", task, location=domain_location,
                         inputs=["PIRT or test objective", "test article drawings/specifications", "pre-test model predictions", "measurement requirements"],
                         tools=["test matrix", "instrumentation plan", "calibration system", "data-acquisition architecture"],
                         outputs=["approved test plan", "test article baseline", "measurement uncertainty analysis", "pre-test prediction envelope"],
                         acceptance="Each test point has a purpose, prerequisites, controlled configuration, procedure, measurement range, acceptance criterion, and data-retention requirement."),
            _common_step("IMP-04", "Fabricate/configure the test article and complete dry, cold, and hot commissioning as applicable.", task, location=domain_location,
                         inputs=["released drawings and procedures", "qualified materials", "calibrated instruments", "work permits"],
                         tools=["fabrication travelers", "M&TE", "DAQ checkout", "leak/pressure/electrical test equipment"],
                         outputs=["as-built test article", "commissioning records", "punch-list and exception disposition"],
                         acceptance="The as-built configuration matches the test baseline and all prerequisites, interlocks, calibrations, and safety controls are verified.", hold_point="HP-I3 test readiness"),
            _common_step("IMP-05", "Execute the approved campaign, preserve raw data, and resolve exceptions before changing the configuration.", task, location=domain_location,
                         inputs=["approved test procedure", "released configuration", "pre-test predictions", "calibration certificates"],
                         tools=["test controls", "historian/DAQ", "sampling and analytical equipment", "event log"],
                         outputs=["raw and reduced data", "operator log", "samples and chain-of-custody", "test exception records"],
                         acceptance="All planned test points are completed or formally dispositioned; data quality, time synchronization, calibration, and configuration records are complete."),
            _common_step("IMP-06", "Validate the model or design claim and release the qualified test dataset.", task, location="Responsible analysis and test organizations",
                         inputs=["raw data", "measurement uncertainty", "model predictions", "test deviations"],
                         tools=["data reduction scripts", "validation metrics", "independent review"],
                         outputs=["test report", "qualified dataset", "model-validation assessment", "conditions of use"],
                         acceptance="The test conclusion is reproducible, uncertainty is quantified, deviations are resolved, and the receiving model/design team accepts the data.", hold_point="HP-I4 data release"),
        ],
        "design_engineering": [
            _common_step("IMP-03", "Develop the system/component requirements and select the preferred design concept.", task, location=domain_location,
                         inputs=["allocated requirements", "hazards and loads", "operating and maintenance concept", "supplier capabilities"],
                         tools=["requirements database", "trade-study model", "PFD/P&ID/CAD or discipline calculation tools"],
                         outputs=["requirements specification", "trade study", "selected concept", "interface control documents"],
                         acceptance="The preferred concept satisfies required functions and has explicit margins, interfaces, inspectability, maintainability, and procurement feasibility."),
            _common_step("IMP-04", "Complete calculations, drawings, specifications, and verification requirements for release.", task, location=domain_location,
                         inputs=["selected concept", "codes and standards", "vendor data", "site and system interfaces"],
                         tools=["discipline design tools", "CAD/PLM", "calculation templates", "requirements traceability"],
                         outputs=["design calculations", "drawings and specifications", "equipment list/BOM", "verification and acceptance plan"],
                         acceptance="The design package is complete to the stated maturity, all requirements are traced, margins are documented, and open items are bounded."),
            _common_step("IMP-05", "Perform independent design verification and release the package for procurement, construction, test, or licensing use.", task, location="Design Authority and responsible engineering organization",
                         inputs=["complete design package", "independent verification plan", "interface closure status"],
                         tools=["design review checklist", "alternate calculation", "model/drawing review", "configuration management workflow"],
                         outputs=["verified design package", "comment-resolution log", "release notice", "downstream restrictions"],
                         acceptance="Independent verification and Design Authority approval are complete; no unresolved issue invalidates the intended downstream use.", hold_point="HP-I3 design release"),
        ],
        "procurement_fabrication": [
            _common_step("IMP-03", "Issue the procurement specification, bidder list, and source-surveillance plan.", task, location="Project procurement organization and qualified suppliers",
                         inputs=["released technical specification", "QA classification", "codes/standards", "delivery need date", "acceptance methods"],
                         tools=["supplier qualification system", "commercial evaluation", "technical bid evaluation", "inspection and test plan"],
                         outputs=["request for proposal", "technical/quality clauses", "bid evaluation", "purchase order", "supplier data requirements list"],
                         acceptance="The selected supplier demonstrates technical capability, capacity, quality controls, schedule, records, and acceptance-test commitments."),
            _common_step("IMP-04", "Execute supplier engineering, fabrication, in-process inspections, and factory acceptance testing.", task, location="Qualified supplier facility",
                         inputs=["approved supplier drawings", "material certifications", "manufacturing plan", "hold/witness points"],
                         tools=["fabrication travelers", "NDE and dimensional inspection", "factory test equipment", "source surveillance"],
                         outputs=["as-built supplier records", "material/NDE certificates", "factory test report", "nonconformance dispositions"],
                         acceptance="All required characteristics and tests meet the specification; deviations are approved before shipment.", hold_point="HP-I3 shipment release"),
            _common_step("IMP-05", "Ship, receive, inspect, preserve, and turn over the item with complete records.", task, location="Supplier, carrier, receiving warehouse, and installation site",
                         inputs=["shipment release", "approved packaging and transport plan", "receiving inspection plan"],
                         tools=["chain-of-custody", "receiving inspection", "preservation controls", "asset/records system"],
                         outputs=["shipping and receipt records", "receiving inspection report", "preservation status", "turnover package"],
                         acceptance="Identity, condition, configuration, documentation, and storage requirements are verified and accepted by the receiving organization."),
        ],
        "construction_installation": [
            _common_step("IMP-03", "Release the construction work package and verify field prerequisites.", task, location="Authorized construction site",
                         inputs=["issued-for-construction drawings", "materials and equipment", "permits/clearances", "inspection and test plan"],
                         tools=["construction work package", "field quality plan", "survey/measurement tools", "work controls"],
                         outputs=["field-ready work package", "pre-job brief", "material and prerequisite verification"],
                         acceptance="The work location, configuration, materials, permits, personnel qualifications, and hold points are ready."),
            _common_step("IMP-04", "Perform installation with in-process inspections and as-built capture.", task, location="Authorized construction site",
                         inputs=["field-ready package", "approved materials and equipment", "qualified procedures"],
                         tools=["installation equipment", "inspection/NDE tools", "field change process", "digital as-built capture"],
                         outputs=["installed system/component", "inspection records", "as-built markups", "nonconformance records"],
                         acceptance="Installation meets released requirements and field changes are approved before concealment or turnover."),
            _common_step("IMP-05", "Complete system walkdown, punch-list disposition, and turnover to testing.", task, location="Installed system and turnover boundary",
                         inputs=["construction completion records", "as-built drawings", "inspection results", "open-item list"],
                         tools=["walkdown checklist", "turnover system", "clearance/tagging system"],
                         outputs=["turnover certificate", "accepted punch list", "as-built package", "test boundary definition"],
                         acceptance="The receiving test/operations organization accepts the system and no open item prevents the planned test or operation.", hold_point="HP-I4 turnover"),
        ],
        "licensing_product": [
            _common_step("IMP-03", "Establish the licensing-product outline, requirement crosswalk, source-owner matrix, and evidence index.", task, location="Controlled licensing authoring and data-room environment",
                         inputs=["selected licensing path", "regulatory requirements and guidance", "design/method/program inputs", "regulatory engagement record"],
                         tools=["controlled authoring", "requirements/commitments database", "evidence index", "review calendar"],
                         outputs=["content plan", "chapter/section owner matrix", "requirement crosswalk", "open-item and evidence index"],
                         acceptance="Every required topic has an accountable technical author, source product, maturity need date, acceptance basis, and review plan."),
            _common_step("IMP-04", "Draft and independently review the product using controlled technical sources.", task, location="Controlled licensing authoring and data-room environment",
                         inputs=["released calculations, designs, programs, test data, and topical reports", "regulator precedents and guidance"],
                         tools=["controlled authoring", "traceability database", "consistency checks", "legal and independent technical review"],
                         outputs=["reviewed draft", "comment log", "consistency report", "commitment and assumption register"],
                         acceptance="Technical conclusions are owned by the producing discipline, traceable to released evidence, and consistent across the application."),
            _common_step("IMP-05", "Submit, support audits/RAIs/hearings, and close conditions or commitments.", task, location="Applicant, regulator/DOE host, and controlled correspondence systems",
                         inputs=["approved submittal", "SME response plan", "audit/RAI tracker"],
                         tools=["submittal system", "RAI and commitment tracker", "secure evidence room", "hearing/audit preparation"],
                         outputs=["submitted product", "responses and audit records", "closed commitments or license conditions", "accepted/approved product"],
                         acceptance="The authority/host decision is issued or all review actions are closed to the agreed stage, with commitments implemented and configuration controlled.", hold_point="HP-I4 authorization/licensing release"),
        ],
        "operations_program": [
            _common_step("IMP-03", "Develop the operating program, procedures, staffing, qualification, surveillance, and records model.", task, location="Operations organization, simulator, laboratory, and work-management system",
                         inputs=["licensed/authorized design basis", "technical specifications/operating limits", "equipment and program requirements", "staffing concept"],
                         tools=["procedure templates", "LMS", "CMMS", "simulator/testbed", "records system"],
                         outputs=["program manual", "implementing procedures", "training and qualification matrix", "surveillance/work-order load"],
                         acceptance="The program has accountable owners, executable procedures, qualified personnel, controlled tools, and scheduled requirements."),
            _common_step("IMP-04", "Perform dry runs, simulator/field demonstrations, and readiness assessments.", task, location="Simulator, installed plant/test facility, and operations work environment",
                         inputs=["approved procedures", "qualified staff", "configured systems", "readiness criteria"],
                         tools=["simulator", "walkdowns", "drill/exercise tools", "readiness checklist"],
                         outputs=["dry-run records", "readiness findings", "corrective actions", "revised procedures/training"],
                         acceptance="Critical tasks and abnormal conditions are demonstrated within performance criteria and findings are closed or formally controlled."),
            _common_step("IMP-05", "Place the program in service and monitor early performance.", task, location="Operating facility and program systems",
                         inputs=["readiness approval", "operating authorization", "baseline KPIs and action levels"],
                         tools=["CMMS/LIMS/historian", "performance dashboard", "corrective action system"],
                         outputs=["operating records", "trend reports", "first-cycle feedback", "program revisions"],
                         acceptance="The program is producing required records, meeting action levels, and controlling deviations and changes.", hold_point="HP-I4 program activation"),
        ],
        "management_control": [
            _common_step("IMP-03", "Establish the controlled plan, data sources, thresholds, cadence, and decision rights.", task, location="Program controls and technical governance environment",
                         inputs=["approved scope", "WBS/deliverables", "schedule and cost data", "risk and decision thresholds"],
                         tools=["integrated schedule", "cost system", "risk register", "decision log", "dashboard"],
                         outputs=["controlled management plan", "baseline", "reporting calendar", "escalation thresholds"],
                         acceptance="The control process has one authoritative data source, named decision owners, measurable thresholds, and no duplicate reporting layer."),
            _common_step("IMP-04", "Operate the control cycle and resolve variances through accountable actions.", task, location="Program controls and technical governance environment",
                         inputs=["current status and forecast", "technical deliverable acceptance", "risk and change records"],
                         tools=["variance analysis", "forecasting", "change control", "action tracker"],
                         outputs=["decision-ready status", "approved corrective actions", "baseline changes", "forecast and risk updates"],
                         acceptance="Decisions are based on accepted technical outputs and documented evidence; variances have owners, dates, and closure criteria."),
            _common_step("IMP-05", "Audit effectiveness and retire controls that do not support a decision or compliance need.", task, location="Program and independent assurance organization",
                         inputs=["control records", "audit findings", "user feedback", "performance metrics"],
                         tools=["process audit", "metrics review", "lessons-learned register"],
                         outputs=["effectiveness assessment", "streamlined process", "closed findings"],
                         acceptance="The process demonstrates useful decisions, timely closure, and no unnecessary duplicate reports or meetings."),
        ],
    }
    steps = base_steps + pattern_steps.get(pattern, pattern_steps["design_engineering"])

    linked = _linked_playbooks(task)
    return {
        "implementation_readiness": "Execution definition complete; task-specific facility, supplier, and final design inputs remain subject to the listed hold points.",
        "implementation_summary": (
            f"Deliver {task_name} between {start or 'the approved start'} and {finish or 'the approved finish'} through a controlled sequence of implementation authorization, input/facility readiness, technical execution, independent verification, and downstream handoff. "
            f"The producing lead is {responsible}; temporary laboratory, supplier, construction, or regulatory support is purchased only for defined products and acceptance evidence."
        ),
        "delivery_strategy": {
            "owner_scope": "Retain requirements ownership, technical integration, safety/licensing conclusions, acceptance authority, configuration control, and knowledge needed for operation.",
            "external_scope": "Use qualified laboratories, national laboratories, specialist consultants, suppliers, constructors, and vendors for bounded work packages with explicit deliverables, data rights, quality requirements, and acceptance criteria.",
            "preferred_contract_form": _contract_form(pattern),
            "work_location_strategy": domain_location,
        },
        "make_buy_partner_decision": {
            "default": "Owner-integrated execution with specialist surge support; do not create a permanent internal capability for short-duration work unless it is needed to operate or maintain the plant.",
            "retain_in_house": ["requirements and interfaces", "technical-basis ownership", "acceptance and change control", "regulatory commitments", "operating knowledge"],
            "candidate_external_scope": _external_scope(domain, pattern),
            "selection_criteria": ["relevant molten-salt/nuclear experience", "qualified staff and facilities", "ability to meet QA/records requirements", "data and IP rights", "schedule capacity", "transparent cost and acceptance basis"],
        },
        "authorizations_and_prerequisites": _authorizations(task, domain, pattern),
        "implementation_steps": steps,
        "procurement_and_contracting_actions": _procurement_actions(task, pattern),
        "long_lead_items": _long_lead_items(task, domain, pattern),
        "decision_points": _decision_points(task, pattern),
        "field_lab_or_vendor_activities": _field_activities(task, domain, pattern),
        "fallbacks_and_contingencies": _fallbacks(task, domain, pattern),
        "implementation_records": [
            "Approved implementation brief and delivery-model decision.",
            "Facility, supplier, software, equipment, personnel, and authorization readiness evidence.",
            "Native calculations, models, drawings, specifications, procedures, raw data, supplier files, and as-built/as-tested records as applicable.",
            "Independent verification, comment resolution, nonconformance/discrepancy disposition, approval, and handoff acceptance.",
            "Cost, schedule, procurement, interface, assumption, risk, and change-control records linked to the WBS identifier.",
        ],
        "linked_playbooks": linked,
        "implementation_source_basis": _source_basis(task, domain, linked),
        "open_decisions": _open_decisions(task, domain, linked),
        "implementation_quality_score": 100,
    }


def _contract_form(pattern: str) -> str:
    return {
        "analysis_model": "Fixed-scope technical work order with native files, benchmark cases, reproducibility, and independent-review deliverables.",
        "test_experiment": "Milestone-based laboratory or test-facility work order with test plan, readiness review, raw data, uncertainty, sample custody, and qualified dataset deliverables.",
        "design_engineering": "Fixed-price or target-cost design package with staged 30/60/90/final releases and interface/change-control obligations.",
        "procurement_fabrication": "Purchase order or fabrication subcontract with supplier data requirements, source surveillance, hold/witness points, and factory acceptance testing.",
        "construction_installation": "Construction work package or subcontract with inspection/test plan, field change control, as-built capture, and system turnover.",
        "licensing_product": "Applicant-controlled technical authoring package with discipline ownership, independent review, audit/RAI support, and commitment closure.",
        "operations_program": "Owner-led program development with specialist procedure, simulator, training, and software support where needed.",
        "management_control": "Owner-led control function; procure only independent cost/schedule/risk review or specialized tool configuration.",
    }.get(pattern, "Milestone-based technical work package with explicit acceptance evidence.")


def _external_scope(domain: str, pattern: str) -> list[str]:
    items = {
        "chemistry": ["salt synthesis/purification", "specialized chemical analysis", "hot-cell or irradiated-salt work", "surrogate processing tests"],
        "materials": ["long-duration corrosion loops", "irradiation and post-irradiation examination", "specialized microscopy/mechanical testing", "welding/NDE qualification"],
        "neutronics": ["critical experiments", "nuclear data and benchmark support", "independent Monte Carlo reference calculations"],
        "thermal_hydraulics": ["facility operation", "CFD/experimental specialist support", "pump/valve/heat-exchanger vendor tests"],
        "instrumentation_controls": ["sensor development and calibration", "vendor platform engineering", "EMI/RFI/EQ testing", "hardware-in-the-loop testing"],
        "site_environmental": ["field investigations", "laboratory analyses", "specialty hazard modeling", "permitting support"],
        "licensing_authorization": ["independent licensing review", "legal/hearing support", "specialized topical/regulatory precedents"],
        "procurement_fabrication": ["supplier design", "fabrication", "NDE", "factory testing"],
        "construction_installation": ["site craft labor", "specialty installation", "field testing", "rigging and temporary works"],
    }.get(domain, ["specialized calculations or testing", "qualified supplier engineering", "independent review"])
    if pattern == "management_control":
        return ["independent cost/schedule risk review", "tool configuration", "external benchmarking"]
    return items


def _authorizations(task: dict[str, Any], domain: str, pattern: str) -> list[dict[str, str]]:
    items = [
        {"authorization": "Project work authorization", "evidence": "approved scope, budget, schedule, responsible producer, reviewer, approver, and records location"},
        {"authorization": "Configuration and quality release", "evidence": "current requirements, input baseline, QA classification, approved methods/tools, and change-control status"},
    ]
    concept = str(task.get("concept") or "")
    text = f"{task.get('name','')} {task.get('description','')} {task.get('regulatory_basis','')}".lower()
    if concept == "Demonstrator" or "launch pad" in text or "doe" in text:
        items.append({"authorization": "DOE/host work and nuclear-safety authorization as applicable", "evidence": "host agreement, hazard controls, work permits, material authorization, and readiness decision"})
    if concept == "Power Reactor" or any(p in text for p in ["part 50", "part 52", "part 53", "nrc"]):
        items.append({"authorization": "NRC licensing-basis and construction/operation controls as applicable", "evidence": "applicable license/permit, commitments, inspections, and approved procedures"})
    if domain in {"chemistry", "materials"} or any(p in text for p in ["fuel", "salt", "radioactive", "fission"]):
        items.append({"authorization": "Material possession, handling, transport, and laboratory authorization", "evidence": "DOE authorization or applicable NRC/Agreement State license, MC&A/security plan, approved package/transport route, and waste disposition"})
    if pattern in {"test_experiment", "construction_installation"}:
        items.append({"authorization": "Test/construction readiness release", "evidence": "approved procedure/work package, calibrated equipment, qualified personnel, permits/clearances, and accepted prerequisites"})
    return items


def _procurement_actions(task: dict[str, Any], pattern: str) -> list[str]:
    if pattern in {"procurement_fabrication", "construction_installation", "test_experiment", "design_engineering"}:
        return [
            "Issue a market survey or RFI early enough to identify qualified facilities, suppliers, long-lead components, and data-rights constraints.",
            "Translate technical and QA requirements into a supplier data requirements list, inspection/test plan, records index, and acceptance matrix.",
            "Perform technical, commercial, schedule, quality, security, and data-rights evaluation before award; reserve capacity where the need date is schedule critical.",
            "Use source surveillance and staged design/fabrication reviews; do not wait until final delivery to discover interface or qualification gaps.",
            "Tie invoice milestones to accepted technical products, raw/native data, records, and closure of supplier deviations rather than elapsed time.",
        ]
    if pattern == "analysis_model":
        return [
            "Acquire software licenses, computing capacity, benchmark data, and specialist support only after the method and conditions of use are approved.",
            "Require native models, scripts, inputs, outputs, software versions, and reproducibility rights in every external analysis purchase.",
        ]
    if pattern == "licensing_product":
        return [
            "Procure independent review, legal/hearing support, and specialty topical expertise under applicant-controlled scope and records requirements.",
            "Do not outsource ownership of technical conclusions; the producing discipline remains responsible for the basis and RAI/audit defense.",
        ]
    return ["Procure only the specialist capability or tool needed to produce an accepted deliverable; retain owner integration and acceptance responsibility."]


def _long_lead_items(task: dict[str, Any], domain: str, pattern: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    if domain == "chemistry":
        items += [
            {"item": "qualified salt/feed material and reference standards", "action": "freeze specification and reserve production/analytical capacity before the test or fuel campaign"},
            {"item": "high-temperature sampling, electrochemical, spectroscopy, and analytical equipment", "action": "select, qualify, calibrate, and procure spares before hot commissioning"},
        ]
    if domain == "materials":
        items += [
            {"item": "candidate alloy heats, weldments, coatings, and witness coupons", "action": "procure traceable heats and fabricate specimens before loop/irradiation slots"},
            {"item": "irradiation/hot-cell capacity", "action": "reserve national-laboratory slots and define PIE shipment/records requirements early"},
        ]
    if domain == "instrumentation_controls":
        items.append({"item": "high-temperature sensors, feedthroughs, DAQ, and vendor control hardware", "action": "prototype and qualify before final design release; stock critical spares"})
    if pattern == "procurement_fabrication":
        items.append({"item": "supplier engineering and fabrication slot", "action": "reserve capacity at preliminary design maturity and manage through staged releases"})
    if pattern == "construction_installation":
        items.append({"item": "site access, craft labor, rigging, temporary power/heat, and turnover resources", "action": "integrate into the construction readiness plan before mobilization"})
    if not items:
        items.append({"item": "specialized personnel, facility, software, data, or supplier capacity", "action": "identify and reserve before the task latest-start date"})
    return items


def _decision_points(task: dict[str, Any], pattern: str) -> list[dict[str, str]]:
    name = str(task.get("name") or "activity")
    start = str((task.get("schedule") or {}).get("start") or "")
    finish = str((task.get("schedule") or {}).get("finish") or "")
    return [
        {
            "decision": f"Authorize implementation of {name}",
            "owner": _role(task),
            "required_by": start,
            "evidence": "Approved scope, budget, schedule, delivery model, facility/supplier readiness, responsible producer/reviewer/approver, and objective acceptance criteria.",
        },
        {
            "decision": "Release the intermediate method/design/test/procurement baseline",
            "owner": "Technical authority and receiving organization",
            "required_by": "Before downstream irreversible commitment",
            "evidence": "Controlled inputs and assumptions, verification results, open-item restrictions, and documented adequacy for the identified downstream use.",
        },
        {
            "decision": "Accept the final technical product and handoff",
            "owner": "Technical authority and receiving organization",
            "required_by": finish,
            "evidence": "Independent verification, requirements traceability, records index, discrepancy closure, configuration release, and receiving-organization acceptance.",
        },
    ]


def _field_activities(task: dict[str, Any], domain: str, pattern: str) -> list[dict[str, str]]:
    location = {
        "chemistry": "Qualified chemistry laboratory, salt loop, hot cell, or authorized fuel-salt facility",
        "materials": "Qualified materials laboratory, corrosion loop, irradiation facility, hot cell, or fabrication supplier",
        "neutronics": "Controlled analysis environment and authorized critical-experiment facility where required",
        "thermal_hydraulics": "Separate-effects rig, integral thermal-hydraulics facility, vendor test stand, or installed plant",
        "instrumentation_controls": "Vendor factory, calibration laboratory, hardware-in-the-loop testbed, and installed plant",
        "site_environmental": "Selected site, qualified field contractor, analytical laboratory, and controlled GIS/data environment",
        "procurement_fabrication": "Qualified supplier facility and receiving location",
        "construction_installation": "Authorized construction site and turnover boundary",
    }.get(domain, "Responsible engineering organization, qualified supplier/laboratory, and controlled project environment")
    mapping = {
        "analysis_model": [
            ("Acquire benchmark or validation evidence", location, "Controlled source data, applicability assessment, uncertainty, and custody/traceability record"),
            ("Perform an independent rerun or confirmatory calculation", "Independent qualified analyst or alternate tool environment", "Independent input deck, result comparison, discrepancy log, and reviewer approval"),
            ("Reconcile model results with the receiving design or licensing team", "Structured technical review", "Agreed conditions of use, margin table, open-item disposition, and handoff record"),
        ],
        "test_experiment": [
            ("Configure and commission the test article", location, "As-built configuration, leak/functional checks, calibration status, and commissioning record"),
            ("Execute the measurement-system analysis and readiness review", location, "Uncertainty budget, data-acquisition configuration, sample plan, readiness checklist, and authorization to test"),
            ("Run the approved campaign and preserve sample/data custody", location, "Raw time-synchronized data, operating log, samples, anomalies, configuration changes, and operator signoffs"),
            ("Perform post-test examination and independent data qualification", "Qualified laboratory and independent data review", "Qualified dataset, uncertainty, material balance, discrepancy dispositions, and data-release approval"),
        ],
        "procurement_fabrication": [
            ("Conduct supplier design review", location, "Approved drawings/calculations, interface closure, and supplier data index"),
            ("Perform source inspection and witness/hold points", location, "Inspection records, material traceability, weld/NDE records, nonconformance dispositions, and release notes"),
            ("Execute factory acceptance testing", location, "Approved FAT procedure, calibrated results, exceptions, and shipment release"),
            ("Complete receiving inspection", "Project receiving location", "Package condition, identity, preservation, certificates, inventory, and acceptance record"),
        ],
        "construction_installation": [
            ("Verify field prerequisites", location, "Released work package, permits/clearances, materials, survey/control points, and predecessor turnover"),
            ("Install and inspect the configured system", location, "In-process inspection, weld/NDE/torque/alignment records, field changes, and punch items"),
            ("Perform walkdown and as-built capture", location, "Accepted walkdown, redlines, tag/label verification, cleanliness status, and as-built package"),
            ("Turn over the system for testing", location, "Turnover certificate, accepted punchlist, calibration/energization status, and test prerequisites"),
        ],
        "operations_program": [
            ("Validate procedures and program controls", "Simulator, mockup, or installed plant", "Validated procedure, discrepancy log, and approved revision"),
            ("Conduct simulator or field dry runs", "Representative operating environment", "Scenario records, timing/workload results, operator feedback, and corrective actions"),
            ("Qualify personnel and tools", "Training facility and point of work", "Qualification records, examinations/JPMs, tool/calibration status, and authorization roster"),
            ("Execute the program initially and review performance", "Installed plant and work-management system", "Initial execution records, KPIs, lessons learned, and program acceptance"),
        ],
    }
    rows = mapping.get(pattern)
    if rows is None:
        rows = [
            ("Conduct the required laboratory, field, vendor, or technical review activity", location, "Native technical evidence, independent review, discrepancy closure, and accepted handoff"),
        ]
    return [{"activity": a, "where": w, "evidence": e} for a, w, e in rows]


def _fallbacks(task: dict[str, Any], domain: str, pattern: str) -> list[dict[str, str]]:
    items = [
        {"trigger": "Required input or design decision is late", "response": "Proceed only on an approved bounded envelope; protect rework hold points and delay irreversible procurement/construction if the bound cannot protect the decision."},
        {"trigger": "Preferred supplier, laboratory, facility, or software is unavailable", "response": "Use the prequalified alternate or divide the work into an owner-controlled integration package and smaller specialist work orders; revalidate schedule, data rights, and acceptance."},
        {"trigger": "Verification or test result falls outside acceptance", "response": "Stop release, preserve the configuration and evidence, enter the discrepancy/CAP process, perform root-cause and extent-of-condition review, and repeat only after an approved disposition."},
    ]
    if domain == "chemistry":
        items.append({"trigger": "Fuel/salt composition or process route changes", "response": "Freeze affected use, update the property/redox/corrosion/source-term applicability matrix, repeat the minimum qualification set, and reissue conditions of use."})
    if pattern == "procurement_fabrication":
        items.append({"trigger": "Supplier delivery is forecast late", "response": "Activate second-source or owner-furnished-material strategy, resequence off-site work, and protect field interfaces with temporary or mockup hardware only where technically acceptable."})
    return items


def _linked_playbooks(task: dict[str, Any]) -> list[str]:
    text = " ".join(str(task.get(k) or "") for k in ["id", "name", "description", "phase", "execution_stream", "regulatory_basis"]).lower()
    linked: list[str] = []
    rules = [
        ("PB-FUEL-01", ["fuel", "haleu", "uranium", "criticality", "material control", "receipt", "load readiness"]),
        ("PB-CHEM-01", ["chem", "salt", "redox", "purification", "sampling", "thermophysical"]),
        ("PB-FP-01", ["fission product", "off-gas", "offgas", "source term", "plate-out", "plateout", "radwaste", "processing"]),
        ("PB-MAT-01", ["material", "corrosion", "welding", "joining", "aging", "irradiation", "inspection"]),
        ("PB-MCA-01", ["material control", "accounting", "safeguard", "security", "inventory", "part 74"]),
        ("PB-WASTE-01", ["waste", "decommission", "end-state", "end state", "disposition", "radwaste"]),
        ("PB-TEST-01", ["test", "experiment", "validation", "facility", "ithf", "commissioning", "data qualification"]),
        ("PB-SUPPLY-01", ["procure", "supplier", "fabrication", "purchase", "long-lead", "long lead", "vendor", "transport"]),
    ]
    for playbook, keywords in rules:
        if any(keyword in text for keyword in keywords):
            linked.append(playbook)
    if not linked:
        domain = str((task.get("engineering_work_package") or {}).get("primary_domain") or "")
        domain_default = {
            "chemistry": ["PB-CHEM-01"], "materials": ["PB-MAT-01"], "test_commissioning": ["PB-TEST-01"],
            "procurement_fabrication": ["PB-SUPPLY-01"], "construction_installation": ["PB-SUPPLY-01"],
        }
        linked.extend(domain_default.get(domain, []))
    return sorted(set(linked))


def _source_basis(task: dict[str, Any], domain: str, linked: list[str]) -> list[dict[str, str]]:
    source_ids: list[str] = []
    if "PB-FUEL-01" in linked:
        source_ids += ["DOE_HALEU_PROGRAM", "DOE_HALEU_ALLOCATION", "DOE_HALEU_ENRICHMENT", "DOE_HALEU_DECONVERSION", "DOE_HALEU_TRANSPORT", "INL_MCRE_FUEL", "NRC_PART70", "NRC_PART71", "NRC_PART74"]
    if "PB-CHEM-01" in linked:
        source_ids += ["ORNL_LSTL", "ORNL_FASTR", "ORNL_PURIFICATION", "ORNL_REDOX", "ORNL_FP_CORROSION"]
    if "PB-FP-01" in linked:
        source_ids += ["ORNL_OFFGAS_MONITORING", "ORNL_XE_CAPTURE", "ORNL_MASS_ACCOUNTANCY", "ORNL_MSRE_FP"]
    if "PB-MCA-01" in linked:
        source_ids += ["NRC_PART70", "NRC_PART74", "ORNL_MASS_ACCOUNTANCY"]
    if "PB-TEST-01" in linked:
        source_ids += ["ORNL_LSTL", "ORNL_FASTR", "NRIC_LOTUS", "INL_MCRE_PROGRAM"]
    if domain == "licensing_authorization":
        source_ids += ["NRIC_LAUNCHPAD_USA", "NRIC_LAUNCHPAD_INL"]
    seen = set()
    return [
        {"source_id": sid, "url": SOURCES[sid], "use": "Implementation precedent, regulatory/authorization basis, or experimental method reference; not a supplier quotation or project commitment."}
        for sid in source_ids if not (sid in seen or seen.add(sid))
    ]


def _open_decisions(task: dict[str, Any], domain: str, linked: list[str]) -> list[dict[str, str]]:
    decisions = [
        {"decision": "Final work location and delivery organization", "owner": _role(task), "required_by": str((task.get("schedule") or {}).get("start") or ""), "closure_evidence": "approved implementation brief and contract/facility commitment"},
        {"decision": "Final acceptance thresholds and evidence class", "owner": "Technical authority and receiving organization", "required_by": "before method/design/test readiness release", "closure_evidence": "approved requirement and acceptance matrix"},
    ]
    if "PB-FUEL-01" in linked:
        decisions += [
            {"decision": "Fuel chemistry family, fissile assay/form, quantity, ownership, and disposition route", "owner": "Reactor physics, fuel/materials, chemistry, safeguards, licensing, and host", "required_by": "2027-03-31 for demonstrator design use", "closure_evidence": "fuel requirements and ownership strategy decision record"},
            {"decision": "DOE allocation versus commercial supply route and backup", "owner": "Program, procurement, licensing, and host", "required_by": "2027-06-30", "closure_evidence": "conditional allocation/contract and commercial capacity plan"},
        ]
    if "PB-CHEM-01" in linked or "PB-FP-01" in linked:
        decisions.append({"decision": "Processing architecture: no routine cleanup, off-gas only, targeted removal, or broader processing", "owner": "Chemistry, reactor physics, safety analysis, safeguards, waste, operations, and economics", "required_by": "2027-12-31 for demonstrator configuration freeze", "closure_evidence": "trade study supported by surrogate experiments, mass balance, safety, safeguards, waste, and cost"})
    if domain == "materials":
        decisions.append({"decision": "Reference alloy/joining/coating and surveillance strategy", "owner": "Materials and Design Authority", "required_by": "before procurement specification release", "closure_evidence": "materials down-select and qualification matrix"})
    return decisions


def _fuel_playbook() -> dict[str, Any]:
    tasks = ["S-INL-05", "S-MSR-06", "D-DEMO-04", "D-3.4.g", "D-3.14.f", "P-PKG-02", "P-3.4.g", "P-3.14.f", "P-OPT-06"]
    phases = [
        {
            "phase_id": "FUEL-01",
            "phase": "Requirements and supply strategy",
            "window": "2026-10-01 to 2027-03-31",
            "actions": [
                "Freeze the demonstrator and commercial fuel demand by isotopic assay range, chemical family, fissile-feed form, total mass, batch size, makeup/contingency inventory, required delivery dates, impurity limits, physical-property envelope, ownership, and end-state disposition.",
                "Issue a Fuel Material Requirements Specification and a separate Fuel Supply and Ownership Strategy covering DOE-furnished and commercially procured alternatives.",
                "Determine whether the carrier/fuel salt is fluoride- or chloride-based and whether the fissile precursor is received as metal, oxide, or another supplier-qualified feed form; do not release synthesis equipment until this gate is closed.",
            ],
            "deliverables": ["fuel demand forecast", "fuel material requirements specification", "ownership/disposition strategy", "supply-route decision matrix"],
            "gate": "Fuel requirements and ownership strategy approved",
        },
        {
            "phase_id": "FUEL-02",
            "phase": "DOE allocation and commercial backup",
            "window": "2026-11-01 to 2027-09-30",
            "actions": [
                "Join and actively participate in the DOE HALEU Consortium and submit an allocation request for demonstrator/critical-experiment material with the required quantity, form, schedule, end use, host, cost share, and readiness evidence.",
                "Negotiate conditional allocation, title/ownership, use restrictions, security, reporting, return/disposition, liability, schedule, and transformation responsibilities with DOE and the host.",
                "In parallel, issue a commercial RFI to DOE framework enrichment and deconversion vendors and reserve a backup path; for the commercial reactor, convert the RFI into capacity-reservation and option agreements rather than waiting for final licensing.",
            ],
            "deliverables": ["DOE allocation request", "conditional allocation/ownership agreement", "commercial RFI and bidder matrix", "capacity reservation strategy"],
            "gate": "Primary and backup source routes contractually credible",
        },
        {
            "phase_id": "FUEL-03",
            "phase": "Enrichment, deconversion, and fissile-feed contracting",
            "window": "2027-04-01 to 2028-06-30 for demonstrator; 2028-2033 for commercial",
            "actions": [
                "Select the enrichment and deconversion/form-conversion chain compatible with the final fuel specification; Project-MSR does not plan to build or operate its own enrichment capability.",
                "Flow down assay, quantity, chemical form, impurity, criticality-safety, packaging, schedule, data, quality, security, and acceptance requirements through the DOE allocation or commercial contracts.",
                "Require batch genealogy, isotopic assay, mass/accountability records, certificates, samples/reference standards, and rights to perform independent confirmatory analysis.",
            ],
            "deliverables": ["enrichment/deconversion task orders or purchase agreements", "supplier quality plan", "batch genealogy and acceptance-data requirements"],
            "gate": "Fissile feed form and delivery schedule accepted",
        },
        {
            "phase_id": "FUEL-04",
            "phase": "Fuel-salt synthesis and analytical qualification",
            "window": "2027-01-01 to 2028-09-30",
            "actions": [
                "Select an authorized synthesis partner, with INL/national-laboratory execution as the demonstrator reference precedent and a qualified Part 70/DOE-authorized alternative maintained where practical.",
                "Qualify the synthesis route in sequence using carrier-salt and non-fissile surrogates, then depleted/natural-uranium or other authorized low-consequence material where useful, before the production fissile batch.",
                "Demonstrate batch homogeneity, chemical stoichiometry, total and isotopic uranium, moisture/oxygen and metallic impurities, redox condition, melt/freeze behavior, key thermophysical properties, sampling representativeness, repeatability, recovery, and off-specification disposition.",
                "Perform an independent laboratory cross-check for decision-significant measurements and establish retained reference samples and chain-of-custody.",
            ],
            "deliverables": ["qualified synthesis procedure", "analytical method qualification", "qualification-batch report", "production traveler and sampling plan"],
            "gate": "Qualification batch accepted and production authorized",
        },
        {
            "phase_id": "FUEL-05",
            "phase": "Production, packaging, transport, receipt, and storage",
            "window": "2028-04-01 to 2029-03-31 for demonstrator; 2033-2035 for commercial",
            "actions": [
                "Produce the required batches under the approved traveler and MC&A plan, reconcile starting material, product, samples, residues, scrap, and waste, and resolve every inventory or analytical anomaly before shipment.",
                "Select an NRC-certified or DOE-approved package/transport configuration compatible with the material form; complete criticality, heat, shielding, containment, security, route, carrier, and notification planning.",
                "At receipt, verify package condition, seals, identity, quantity, isotopic and chemical certificates, independent samples as required, storage configuration, heat tracing/temperature limits, criticality controls, MC&A entry, and host authorization before use.",
            ],
            "deliverables": ["accepted production batch records", "package and transportation plan", "shipping and receipt records", "storage and material-accountability baseline"],
            "gate": "Fuel accepted for loading/use by the host and technical authority",
        },
        {
            "phase_id": "FUEL-06",
            "phase": "Commercial supply continuity and disposition",
            "window": "2028-2038",
            "actions": [
                "Reserve commercial enrichment, deconversion, salt-synthesis, packaging, and analytical capacity for the initial core and makeup inventory; qualify at least one alternate for the most schedule-critical step.",
                "Define the operating inventory, makeup cadence, contingency stock, sampling/acceptance, transfer, and return/disposition model before commercial fuel production starts.",
                "Maintain a full material genealogy and end-state plan for residual salt, samples, filters/sorbents, residues, scrap, and deactivated equipment; DOE-owned material follows the governing return/disposition agreement.",
            ],
            "deliverables": ["commercial fuel supply agreements", "qualified production facility/vendor", "initial-core and makeup production plan", "end-state disposition plan"],
            "gate": "Commercial initial-core fuel and continuing supply are available before fuel-load readiness",
        },
    ]
    return {
        "playbook_id": "PB-FUEL-01",
        "title": "Fuel supply, ownership, fuel-salt production, transport, receipt, and disposition",
        "objective": "Obtain the authorized fissile material and convert it into accepted fuel salt on the schedule needed for the INL experiment, demonstrator, and commercial plant without relying on a single uncontracted source.",
        "recommended_baseline": "For the demonstrator and INL critical experiment, pursue DOE HALEU allocation and DOE/national-laboratory fuel-salt synthesis as the primary route while maintaining a commercial enrichment/deconversion backup. For the commercial reactor, reserve commercial enrichment, deconversion, fuel-salt synthesis, packaging, and analytical capacity early. The $30 million direct demonstrator cap assumes the fissile material value and major national-laboratory synthesis services are DOE-furnished or separately funded; otherwise the cap must be rebaselined.",
        "technology_branching": [
            "Final fuel-salt family and fissile precursor form remain a design decision. The implementation sequence is common, but chemical specifications, synthesis equipment, analytical methods, corrosion controls, packaging, and waste streams must be branch-specific.",
            "No processing or fuel-cycle facility may be assumed to operate under the reactor authorization alone; verify DOE host authority or applicable NRC/Agreement State material and fuel-cycle licenses before committing the route.",
        ],
        "execution_phases": phases,
        "candidate_supply_routes": [
            {"route": "DOE HALEU allocation", "use": "Demonstrator and critical experiment primary planning route", "actions": "allocation request, readiness evidence, contracting, ownership/use/return terms, transformation and delivery plan", "status": "planning basis; allocation is not assumed until contractually committed"},
            {"route": "Commercial domestic enrichment and deconversion", "use": "backup for demonstration and primary commercial scaling route", "actions": "RFI, supplier qualification, capacity reservation, form-conversion qualification, purchase options and final orders", "status": "capacity and delivery dates require supplier commitments"},
            {"route": "DOE-owned recovered material or other government material", "use": "possible allocation source", "actions": "DOE selection, title and use agreement, form conversion, analytical qualification, transport and disposition", "status": "available only if offered through DOE allocation"},
        ],
        "required_acceptance_data": [
            "total mass and isotopic assay with uncertainty and material-accountability identifiers",
            "chemical composition and stoichiometry; moisture/oxygen, corrosion-active impurities, metallic contaminants, and redox condition",
            "homogeneity and sampling representativeness across the batch",
            "melt/freeze behavior and selected thermophysical properties needed for safe handling and model input",
            "container/package compatibility, cleanliness, seals, contamination survey, and transport records",
            "retained reference samples, analytical standards, laboratory qualification, and independent confirmatory results",
            "complete genealogy for feed, product, samples, residues, scrap, and waste",
        ],
        "linked_task_ids": tasks,
        "source_ids": ["DOE_HALEU_PROGRAM", "DOE_HALEU_ALLOCATION", "DOE_HALEU_ENRICHMENT", "DOE_HALEU_DECONVERSION", "DOE_HALEU_TRANSPORT", "INL_MCRE_FUEL", "NRC_PART70", "NRC_PART71", "NRC_PART74"],
        "source_urls": [SOURCES[s] for s in ["DOE_HALEU_PROGRAM", "DOE_HALEU_ALLOCATION", "DOE_HALEU_ENRICHMENT", "DOE_HALEU_DECONVERSION", "DOE_HALEU_TRANSPORT", "INL_MCRE_FUEL", "NRC_PART70", "NRC_PART71", "NRC_PART74"]],
        "cost_accounting": {
            "accounting_tasks": tasks,
            "rule": "Use existing task costs and the commercial fuel/material qualification package; the playbook is a non-additive execution crosswalk. Rebaseline the demonstrator cap if fissile material or major synthesis services are not government-furnished/separately funded.",
        },
    }


def _chemistry_tests() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    def add(test_id: str, campaign: str, objective: str, configuration: str, material_stage: str, measurements: list[str], methods: list[str], acceptance: str, supports: list[str], tasks: list[str], window: str, facility: str) -> None:
        rows.append({
            "test_id": test_id,
            "campaign": campaign,
            "objective": objective,
            "configuration": configuration,
            "material_stage": material_stage,
            "primary_measurements": measurements,
            "analytical_methods": methods,
            "acceptance_basis": acceptance,
            "model_or_decision_supported": supports,
            "linked_task_ids": tasks,
            "planned_window": window,
            "facility_strategy": facility,
            "required_records": ["approved procedure and configuration", "material genealogy and sample custody", "raw data and calibration", "uncertainty and replicate analysis", "independent review and qualified dataset"],
        })
    common = ["D-RD-01", "S-MTH-04", "S-MSR-02", "S-MSR-04", "S-MSR-05"]
    add("CHEM-01", "Incoming salt/feed qualification", "Verify supplier certificates and establish an independent baseline for carrier salt and fissile/feed precursor before synthesis or loop loading.", "Representative samples from each supplier lot and container; duplicate samples retained.", "nonradioactive carrier salt first; authorized fissile feed for production acceptance", ["identity and composition", "moisture/oxygen and corrosion-active impurities", "metallic impurities", "particle/foreign material", "batch uniformity"], ["ICP-MS/OES or equivalent", "ion chromatography or equivalent", "oxygen/moisture analysis", "XRD/Raman as applicable", "independent laboratory cross-check"], "All required constituents and impurity limits meet the controlled procurement specification; any discrepancy is resolved before use.", ["fuel-salt acceptance specification", "corrosion and redox basis"], common + ["S-INL-05"], "Q4 2026-Q2 2027", "Qualified commercial or national-laboratory analytical laboratory")
    add("CHEM-02", "Carrier-salt purification scale-up", "Demonstrate the selected purification route from bench to engineering batch and quantify impurity removal, salt recovery, repeatability, and waste generation.", "Bench batches followed by an engineering-scale batch in the selected preparation system.", "nonradioactive carrier salt", ["before/after impurity concentrations", "salt mass recovery", "process time", "secondary waste quantity", "equipment fouling and cleanability"], ["qualified chemical analysis", "mass balance", "process instrumentation", "repeat batches"], "Project impurity targets are met in repeated batches with closed mass balance, controlled waste, and no unacceptable equipment degradation.", ["salt preparation design", "fuel-salt synthesis readiness", "corrosion control"], common + ["S-ITHF-18", "S-ITHF-28"], "Q1-Q4 2027", "ORNL/INL or equivalent qualified molten-salt preparation facility")
    add("CHEM-03", "Fuel-salt synthesis batch repeatability", "Qualify the synthesis and blending route and demonstrate chemical/isotopic homogeneity and repeatability before production fuel.", "Sequential qualification batches using surrogate or authorized low-consequence feed, followed by the production-process qualification batch.", "surrogate/non-fissile, then authorized uranium-bearing qualification batch", ["composition and homogeneity", "material balance", "yield/recovery", "impurity pickup", "sampling variability", "off-specification disposition"], ["multi-location sampling", "independent chemical and isotopic analysis", "mass-accountancy reconciliation"], "Repeated batches meet specification and sampling uncertainty is small enough to support acceptance and MC&A conclusions.", ["fuel production authorization", "batch acceptance", "material accountancy"], common + ["S-INL-05", "D-DEMO-04"], "Q2 2027-Q2 2028", "Authorized national-laboratory or licensed fuel-salt synthesis facility")
    add("CHEM-04", "Phase and freeze-thaw behavior", "Measure solidus/liquidus or transition behavior and identify segregation, precipitation, or remelting concerns across the operating composition envelope.", "Small sealed specimens spanning nominal composition, manufacturing tolerance, impurity, and burnup-surrogate states.", "nonradioactive and authorized uranium-bearing samples as needed", ["transition temperatures", "latent heat", "phase identification", "segregation after freeze/thaw", "repeat-cycle stability"], ["DSC/DTA", "XRD", "microscopy", "controlled freeze-thaw cycles"], "Measured behavior supports heat-trace, drain, recovery, sampling, and storage margins with quantified uncertainty.", ["freeze/drain models", "storage and transfer design", "operating limits"], common + ["S-MSR-07", "S-ITHF-39"], "Q1 2027-Q4 2028", "Qualified chemistry/materials laboratory")
    add("CHEM-05", "Thermophysical property matrix", "Generate the density, viscosity, heat capacity, thermal conductivity, and vapor/volatility data required by system and accident models.", "Controlled composition and temperature matrix including nominal, tolerance, impurity, and selected fission-product-surrogate states.", "nonradioactive and authorized uranium-bearing specimens", ["density", "viscosity", "heat capacity", "thermal conductivity", "vapor pressure or volatility indicators", "measurement covariance"], ["qualified property methods", "reference materials", "replicate measurements", "inter-laboratory comparison"], "Correlations cover the approved analysis domain and meet the uncertainty targets in the methods plan; gaps are bounded and flagged.", ["system TH", "heat transfer", "freeze/drain", "source term"], common + ["S-MSR-02"], "Q4 2026-Q2 2029", "National-laboratory or qualified university/commercial property laboratory")
    add("CHEM-06", "Redox sensor calibration and reference-electrode qualification", "Select and calibrate the online/electrochemical redox measurement method and establish drift, fouling, and maintenance requirements.", "Controlled salt pots with known reference states and representative sensor materials/feedthroughs.", "nonradioactive salt; later authorized fuel salt confirmation", ["sensor response", "accuracy and repeatability", "temperature dependence", "drift", "response time", "fouling/cleaning"], ["electrochemical measurement", "independent wet chemistry/spectroscopy", "reference standards"], "Sensor uncertainty and drift remain within the chemistry control budget over the required maintenance interval.", ["chemistry action levels", "corrosion protection", "process control"], common + ["S-MSR-05"], "Q1 2027-Q2 2029", "Qualified high-temperature chemistry laboratory and ITHF")
    add("CHEM-07", "Impurity perturbation and recovery", "Demonstrate detection and recovery from controlled oxygen/moisture or corrosion-product perturbations without damaging the loop or losing material accountability.", "Small salt pot and then representative loop with approved nonradioactive perturbations; no fissile separation operation.", "nonradioactive representative salt", ["online sensor response", "laboratory confirmation", "corrosion-product release", "purification/recovery time", "salt loss"], ["online electrochemistry/spectroscopy", "chemical analysis", "mass balance", "coupon examination"], "The perturbation is detected, action limits trigger correctly, the approved recovery process restores the chemistry envelope, and resulting corrosion/waste remains acceptable.", ["abnormal operating procedure", "chemistry limits", "cleanup system sizing"], common + ["S-ITHF-45"], "Q2 2027-Q4 2028", "Non-nuclear salt loop with containment and cleanup capability")
    add("CHEM-08", "Static corrosion matrix", "Establish alloy, weld, coating, and graphite/ceramic compatibility across temperature, redox, impurity, and surrogate-fission-product conditions.", "Sealed or controlled-atmosphere capsules with traceable material heats, weldments, and witness coupons.", "nonradioactive representative salt and surrogates", ["mass change", "attack depth", "elemental depletion", "mechanical property change", "deposit chemistry"], ["gravimetry", "SEM/EDS", "XRD", "metallography", "mechanical testing"], "Corrosion/degradation data support the design allowance and life model with reproducible trends and quantified scatter.", ["materials down-select", "corrosion model", "surveillance plan"], ["D-RD-02", "S-MTH-05", "S-MSR-09"], "Q4 2026-Q4 2029", "Qualified materials laboratory")
    add("CHEM-09", "Flow-assisted corrosion and mass transfer", "Measure corrosion and deposition under representative flow, thermal gradients, and chemistry control, including hot-to-cold mass transfer.", "Forced-circulation loop with removable coupons/spools and controlled chemistry.", "nonradioactive representative salt", ["corrosion rate and location", "mass transfer/deposition", "chemistry evolution", "pressure drop", "component fouling"], ["loop sampling", "online chemistry", "coupon/spool examination", "mass balance"], "Observed degradation and deposition remain within the design/inspection envelope and are predictable by the released model.", ["loop material selection", "inspection locations", "maintenance intervals"], ["D-RD-02", "S-MSR-09", "S-ITHF-45"], "Q2 2027-Q4 2029", "ITHF or dedicated materials loop")
    add("CHEM-10", "Weld, joint, seal, and heat-affected-zone qualification", "Demonstrate that production joining and sealing details do not create localized chemistry, corrosion, leakage, or embrittlement weaknesses.", "Production-representative welds, brazes, seals, coatings, and dissimilar-material joints exposed in static and flow conditions.", "nonradioactive representative salt", ["leak tightness", "localized attack", "mechanical properties", "NDE detectability", "repairability"], ["pressure/leak testing", "NDE", "metallography", "mechanical testing"], "Production details meet design, inspection, repair, and lifetime acceptance criteria after exposure.", ["fabrication specifications", "repair procedures", "ISI basis"], ["D-RD-02", "S-MSR-09", "D-DEMO-03", "P-PKG-02"], "Q2 2027-Q4 2032", "Qualified fabrication supplier and materials laboratory")
    add("CHEM-11", "Fission-product surrogate solubility and speciation", "Determine where representative soluble, semi-soluble, and precipitating fission-product groups reside as chemistry and temperature change.", "Salt pots with a controlled matrix of stable surrogates selected by chemical group; later compare with irradiated samples.", "stable nonradioactive surrogates first", ["dissolved concentration", "precipitation threshold", "species/oxidation state", "distribution between salt, gas, deposit, and filter"], ["ICP-MS/OES", "spectroscopy", "electrochemistry", "solid phase characterization", "mass balance"], "Group behavior and uncertainty are sufficient to parameterize source-term, plate-out, processing, and safeguards models.", ["fission-product transport", "processing architecture", "source term"], ["D-RD-01", "S-MTH-04", "S-MSR-04"], "Q2 2027-Q2 2029", "Qualified chemistry laboratory")
    add("CHEM-12", "Noble-metal surrogate plate-out", "Measure deposition locations, rates, resuspension, and decontamination behavior for representative noble-metal species.", "Thermal-gradient flow loop with removable coupons, filters, and controlled surface materials.", "stable surrogates", ["surface inventory", "bulk concentration", "deposition rate", "resuspension", "decontamination effectiveness"], ["surface analysis", "bulk chemical analysis", "removable spool/coupon examination", "mass balance"], "Mass balance closes within the project uncertainty target and the transport model predicts dominant deposition zones and inventories.", ["plate-out model", "shielding/maintenance", "sampling and cleanup locations"], ["S-MSR-04", "D-RD-01", "S-ITHF-45"], "Q3 2027-Q4 2029", "Representative flow loop with removable test sections")
    add("CHEM-13", "Stable noble-gas stripping and residence time", "Quantify gas transfer from salt to cover gas and the effects of flow, free surface, bubbles, and gas contactor design.", "Representative salt loop with stable noble gases and controlled cover-gas flow; no radioactive gas required for initial qualification.", "stable noble-gas tracers", ["transfer coefficient", "residence time", "gas holdup", "carryover", "off-gas concentration response"], ["mass-flow control", "gas chromatography or spectroscopy", "high-speed/void instrumentation as applicable"], "Measured transfer and residence-time behavior validates the off-gas/source-term model over the intended operating range.", ["off-gas sizing", "xenon/precursor models", "source term"], ["S-MSR-04", "S-ITHF-40"], "Q2 2028-Q2 2029", "ITHF/off-gas analog loop")
    add("CHEM-14", "Aerosol generation, transport, and capture", "Measure aerosol formation, size distribution, deposition, and removal across demisters/filters under representative gas and salt conditions.", "Heated cover-gas test train with controlled salt aerosol or stable surrogate aerosol generation.", "nonradioactive surrogates", ["aerosol size and mass", "capture efficiency", "pressure drop", "re-entrainment", "sensor response"], ["particle sizing", "filter gravimetry", "LIBS or equivalent spectroscopy", "surface sampling"], "Treatment stages meet project removal and pressure-drop targets, and monitoring detects breakthrough within the required response time.", ["off-gas train design", "source term", "filter replacement/waste"], ["D-RD-01", "S-MSR-04", "S-MSR-05"], "Q3 2027-Q3 2029", "Qualified off-gas test stand")
    add("CHEM-15", "Volatile-halogen surrogate capture", "Down-select and qualify the capture sequence for volatile halogen species using nonradioactive surrogates before any radioactive confirmation.", "Bench columns followed by an integrated heated off-gas train with representative humidity, aerosol, and flow transients.", "stable surrogates", ["breakthrough curve", "capacity", "decontamination factor", "temperature sensitivity", "regeneration/disposal behavior", "secondary waste"], ["online spectroscopy", "sorbent analysis", "mass balance", "pressure-drop monitoring"], "Selected media/train achieves the project-defined retention and monitoring performance with acceptable waste, heat, and replacement interval.", ["off-gas design", "source term", "waste classification"], ["D-RD-01", "S-MSR-04", "D-3.9.f", "P-3.11.b"], "Q3 2027-Q4 2029", "Qualified off-gas laboratory")
    add("CHEM-16", "Alkali/cesium surrogate capture", "Evaluate aerosol and vapor-phase capture of representative alkali species and identify deposition/fouling risks.", "Heated off-gas train with stable alkali surrogates and representative aerosols.", "stable surrogates", ["capture efficiency", "breakthrough", "deposit location", "fouling", "sensor calibration"], ["LIBS or equivalent", "filter/sorbent analysis", "mass balance"], "The selected train and monitoring method achieve the project retention and operability targets across representative transients.", ["off-gas/source-term model", "maintenance and waste"], ["D-RD-01", "S-MSR-04", "S-MSR-05"], "Q4 2027-Q4 2029", "Qualified off-gas laboratory")
    add("CHEM-17", "Particulate filtration and cleanup", "Demonstrate removal of precipitates/corrosion products without unacceptable fuel/salt loss, plugging, or maintenance burden.", "Bench filters followed by a bypass cleanup skid with controlled surrogate particulates.", "nonradioactive salt and surrogates", ["removal efficiency", "pressure drop", "salt hold-up", "filter life", "backflush/replacement behavior", "waste quantity"], ["particle sizing", "differential pressure", "chemical analysis", "mass balance"], "Selected filtration concept meets removal, pressure-drop, salt-recovery, maintainability, and waste targets.", ["cleanup system design", "operating action levels", "waste handling"], ["D-RD-01", "D-DEMO-04", "S-ITHF-18"], "Q2 2027-Q3 2028", "Representative salt cleanup skid")
    add("CHEM-18", "Targeted rare-earth/lanthanide removal down-select", "Determine whether targeted removal is technically and economically justified and screen candidate separation principles with stable surrogates.", "Small controlled batch tests comparing candidate physical/chemical/electrochemical separation principles; no production-scale fissile separation.", "stable nonradioactive surrogates; authorized uranium-bearing confirmation only if needed", ["decontamination factor", "actinide/fuel retention", "salt recovery", "selectivity", "waste generation", "fouling", "cycle time", "safeguards measurement impact"], ["chemical analysis", "mass balance", "equipment inspection", "process monitoring"], "A documented trade study selects no routine removal, off-gas-only, targeted removal, or broader processing based on safety, reactivity, corrosion, source term, safeguards, waste, operability, and lifecycle cost; any selected method meets project-defined recovery and retention criteria.", ["processing architecture decision", "fuel utilization", "safeguards and waste"], ["D-RD-01", "S-MSR-04", "S-MSR-06", "P-OPT-06"], "Q2 2027-Q4 2027", "Qualified chemistry laboratory; radioactive confirmation only in an authorized facility")
    add("CHEM-19", "Integrated salt-processing skid repeated-cycle demonstration", "Demonstrate the selected minimal processing train as an integrated, maintainable system and quantify performance degradation over repeated cycles.", "Engineering-scale bypass skid including the selected purification, filtration, gas contact, sampling, and monitoring functions; separation scope limited to the approved architecture.", "nonradioactive representative salt; authorized fuel-salt confirmation as required", ["mass balance closure", "salt/fuel retention", "removal/capture performance", "throughput", "availability", "sensor performance", "maintenance dose/work proxy", "waste and consumables"], ["online instruments", "laboratory analysis", "mass/accountancy model", "inspection and maintenance records"], "Repeated cycles meet performance, retention, mass-balance, maintainability, and waste targets without unacceptable accumulation or uncontrolled inventory transfer.", ["demonstrator processing equipment", "operating procedures", "commercial scale-up"], ["D-RD-01", "D-DEMO-04", "S-MSR-06", "P-PKG-02"], "Q1-Q3 2028", "Engineering-scale non-nuclear loop followed by authorized fuel-salt commissioning")
    add("CHEM-20", "Sampling representativeness and hot-sampling qualification", "Prove that routine and confirmatory samples represent the system inventory and can be obtained without contamination, plugging, excessive hold-up, or loss of accountability.", "Representative sampling points, lines, valves, sample containers, and freeze/thaw cycles under controlled flow and chemistry.", "nonradioactive first; authorized fuel-salt confirmation", ["sample bias and variability", "hold-up", "cross-contamination", "plugging/freezing", "operator cycle time", "inventory reconciliation"], ["paired samples", "online-versus-lab comparison", "tracer/mass balance", "repeatability study"], "Sampling bias and repeatability meet the data/MC&A uncertainty budget and the procedure is executable under operating constraints.", ["chemistry program", "MC&A", "model validation", "source term"], ["S-MSR-05", "S-MSR-06", "D-DEMO-04", "P-7.i"], "Q2 2027-Q2 2029", "ITHF and authorized fuel-salt system")
    add("CHEM-21", "Online sensor drift, fouling, and cross-calibration", "Establish calibration, drift, fouling, failure detection, maintenance, and replacement intervals for online chemistry/off-gas sensors.", "Long-duration salt and off-gas test with deliberate normal operating changes and removable sensors.", "nonradioactive and later authorized confirmation", ["accuracy", "drift", "response time", "fouling", "failure modes", "calibration recovery"], ["online electrochemistry/spectroscopy", "laboratory reference analysis", "calibration checks"], "Sensor performance remains within the approved uncertainty and detection budget over the maintenance interval or a validated compensation/maintenance method is defined.", ["instrument specification", "surveillance interval", "alarm/action levels"], ["S-MSR-05", "S-ITHF-45", "P-7.i"], "Q3 2027-Q4 2029", "ITHF/off-gas test stand and qualified lab")
    add("CHEM-22", "Radiation-environment compatibility", "Identify radiation-induced changes in salt chemistry, sensors, sorbents, seals, and sampling materials before relying on non-irradiated tests for reactor service.", "Gamma exposure and, where justified, irradiation capsule or irradiated-salt sample program with matched controls.", "non-fissile or surrogate materials; licensed irradiation/hot-cell work", ["chemical/speciation change", "gas generation", "sensor drift", "sorbent capacity change", "material degradation"], ["gamma facility", "post-exposure chemical/material analysis", "control specimens"], "Radiation effects are bounded in the chemistry, off-gas, sensor, and materials models or qualified component limits are established.", ["source term", "instrument qualification", "off-gas media life", "materials life"], ["S-MTH-04", "S-MTH-05", "S-MSR-04", "S-MSR-05"], "2028-2031", "National-laboratory irradiation and hot-cell facilities")
    add("CHEM-23", "Irradiated-salt confirmatory characterization", "Confirm surrogate-based speciation, partitioning, source-term, corrosion, and mass-accountancy models with samples from the INL critical experiment.", "Controlled samples and deposits from defined experiment states, analyzed in hot cells with matched pre-irradiation baselines.", "irradiated fuel salt and deposits", ["isotopic/elemental inventory", "speciation indicators", "gas/salt/deposit partitioning", "corrosion products", "sample and inventory reconciliation"], ["hot-cell sample preparation", "radiochemical analysis", "spectroscopy/microscopy", "mass-accountancy reconciliation"], "Results are traceable to operating history and close or bound the key surrogate-to-radioactive extrapolations needed for demonstrator/commercial design use.", ["mechanistic source term", "fission-product transport", "MC&A", "chemistry model validation"], ["S-INL-19", "S-MSR-04", "S-MSR-06", "S-MTH-04"], "Q4 2028-Q3 2029", "INL or equivalent authorized hot-cell facility")
    add("CHEM-24", "Demonstrator chemistry and processing performance", "Validate chemistry control, sampling, off-gas/cleanup performance, inventory tracking, and operating procedures under coupled nuclear and thermal conditions.", "Approved demonstrator operating campaigns with staged power/chemistry conditions and predefined hold points.", "operating fuel salt", ["chemistry trends and action-level response", "gas/salt/deposit inventory", "processing performance", "corrosion/sensor trends", "mass balance", "waste and consumables"], ["online sensors", "laboratory samples", "off-gas monitoring", "inventory/accountancy model", "post-operation examination"], "The integrated system remains within chemistry and material limits; measured partitioning and processing performance support the commercial safety case and operating program with quantified uncertainty.", ["commercial design and licensing", "operating limits", "processing system sizing", "maintenance and waste"], ["D-EXP-09", "D-EXP-10", "D-EXP-12", "D-EXP-14", "P-OPT-04", "P-OPT-06"], "2029", "DOE-authorized demonstrator and qualified laboratories")
    add("CHEM-25", "Processing waste and residual-salt characterization", "Characterize every filter, sorbent, residue, sample, heel, contaminated component, and secondary waste stream created by chemistry and processing operations.", "Representative waste generated by bench, engineering-scale, critical-experiment, and demonstrator campaigns.", "nonradioactive and radioactive as generated", ["chemical and radionuclide inventory", "physical form", "leachability/stability as applicable", "heat/dose", "packaging compatibility", "material-accountability closure"], ["qualified chemical/radiochemical analysis", "dose/heat calculation", "waste acceptance testing", "mass balance"], "Each stream has an approved characterization, classification, packaging, storage, transport, treatment, and final disposition path before routine processing begins.", ["waste system design", "DOE return/disposition", "commercial decommissioning and lifecycle cost"], ["D-DEMO-09", "P-3.11.g", "P-OPT-06"], "2027-2038", "Qualified waste laboratory and authorized storage/disposition organizations")
    return rows


def _chem_playbook() -> dict[str, Any]:
    matrix = _chemistry_tests()
    linked = sorted({task for row in matrix for task in row["linked_task_ids"]})
    return {
        "playbook_id": "PB-CHEM-01",
        "title": "Fuel-salt chemistry, processing, fission-product management, and analytical validation",
        "objective": "Establish the chemistry operating envelope and qualify the minimum practical salt preparation, sampling, monitoring, off-gas, cleanup, and processing functions using a staged progression from nonradioactive surrogates to authorized fuel salt and irradiated confirmation.",
        "architecture_decision": {
            "question": "How much online or batch fuel-salt processing is actually required?",
            "alternatives": ["no routine salt processing beyond initial purification", "off-gas and particulate control only", "targeted removal of selected chemical groups", "broader fuel-salt processing"],
            "decision_criteria": ["reactivity and fuel utilization", "corrosion and chemistry control", "mechanistic source term and dose", "safeguards and material accountancy", "waste and secondary streams", "operability and maintainability", "capital and lifecycle cost", "licensing and proliferation-resistance implications"],
            "required_date": "2027-12-31 for demonstrator configuration freeze",
            "rule": "Do not assume continuous fission-product extraction. Select the least complex architecture that meets safety, chemistry, reactivity, source-term, safeguards, and economic needs. Radioactive confirmation is performed only in authorized facilities after surrogate down-selection.",
        },
        "campaign_sequence": [
            "supplier/feed qualification and carrier-salt purification",
            "property, phase, redox, and sensor method qualification",
            "static and flowing corrosion/mass-transfer tests",
            "fission-product surrogate speciation, plate-out, off-gas, filtration, and capture tests",
            "processing architecture down-select and integrated skid repeated-cycle demonstration",
            "sampling, online monitoring, MC&A, waste, and maintainability qualification",
            "irradiated-salt confirmation using the INL experiment",
            "coupled validation in the 2029 demonstrator campaign",
        ],
        "experiment_matrix": matrix,
        "linked_task_ids": linked,
        "source_ids": ["ORNL_LSTL", "ORNL_FASTR", "ORNL_PURIFICATION", "ORNL_REDOX", "ORNL_OFFGAS_MONITORING", "ORNL_XE_CAPTURE", "ORNL_FP_CORROSION", "ORNL_MASS_ACCOUNTANCY", "ORNL_MSRE_FP"],
        "source_urls": [SOURCES[s] for s in ["ORNL_LSTL", "ORNL_FASTR", "ORNL_PURIFICATION", "ORNL_REDOX", "ORNL_OFFGAS_MONITORING", "ORNL_XE_CAPTURE", "ORNL_FP_CORROSION", "ORNL_MASS_ACCOUNTANCY", "ORNL_MSRE_FP"]],
        "cost_accounting": {
            "accounting_tasks": ["D-RD-01", "D-RD-02", "S-MTH-04", "S-MTH-05", "S-MSR-02", "S-MSR-04", "S-MSR-05", "S-MSR-09", "S-ITHF-45", "P-PKG-02"],
            "rule": "The experiment matrix is an execution breakdown of existing chemistry, materials, methods, ITHF, INL, demonstrator, and commercial qualification tasks. Do not add its rows to the program total a second time.",
        },
    }


def _simple_playbooks() -> dict[str, dict[str, Any]]:
    return {
        "PB-FP-01": {
            "playbook_id": "PB-FP-01", "title": "Fission-product transport, off-gas, plate-out, capture, and source-term execution",
            "objective": "Quantify where fission products reside, how they move, and which treatment functions are required, using surrogate flow/off-gas campaigns followed by irradiated-salt and demonstrator confirmation.",
            "execution_sequence": ["group species by chemical/physical behavior", "build gas/salt/deposit/filter mass balance", "validate noble-gas transfer and residence time", "validate aerosol and volatile-species capture", "validate noble-metal plate-out and resuspension", "confirm with irradiated samples", "release mechanistic source-term parameters and uncertainty"],
            "linked_task_ids": ["S-MSR-04", "S-MTH-04", "D-RD-01", "S-ITHF-40", "S-INL-19", "D-EXP-10", "P-3.11.b"],
            "source_ids": ["ORNL_OFFGAS_MONITORING", "ORNL_XE_CAPTURE", "ORNL_MASS_ACCOUNTANCY", "ORNL_MSRE_FP"],
            "source_urls": [SOURCES[s] for s in ["ORNL_OFFGAS_MONITORING", "ORNL_XE_CAPTURE", "ORNL_MASS_ACCOUNTANCY", "ORNL_MSRE_FP"]],
        },
        "PB-MAT-01": {
            "playbook_id": "PB-MAT-01", "title": "Salt-wetted materials, corrosion, joining, irradiation, and surveillance execution",
            "objective": "Qualify alloys, weldments, coatings, seals, graphite/ceramics, and inspection methods across chemistry, temperature, flow, radiation, and fission-product conditions.",
            "execution_sequence": ["traceable material heat and joining matrix", "static capsule screening", "flowing thermal-gradient exposure", "fission-product/impurity perturbation", "mechanical/NDE/repair qualification", "irradiation and PIE where required", "life model and surveillance-coupon program", "commercial ISI/repair implementation"],
            "linked_task_ids": ["D-RD-02", "S-MTH-05", "S-MSR-09", "S-ITHF-17", "S-ITHF-45", "P-PKG-02", "P-OPT-04"],
            "source_ids": ["ORNL_REDOX", "ORNL_FP_CORROSION", "ORNL_FASTR"],
            "source_urls": [SOURCES[s] for s in ["ORNL_REDOX", "ORNL_FP_CORROSION", "ORNL_FASTR"]],
        },
        "PB-MCA-01": {
            "playbook_id": "PB-MCA-01", "title": "Liquid-fuel material control, accounting, safeguards, and inventory reconciliation",
            "objective": "Establish measurement points, material balance areas, sampling, uncertainty, transfer records, anomaly resolution, physical inventory, and dynamic accountancy for fuel distributed among salt, gas, deposits, samples, processing equipment, waste, and storage.",
            "execution_sequence": ["define material balance areas and key measurement points", "qualify mass/volume/composition measurements", "validate dynamic inventory model with surrogate and qualification batches", "integrate off-gas/deposit/sample/process inventories", "perform anomaly and loss-detection exercises", "qualify receipt/transfer/physical inventory procedures", "confirm with critical-experiment and demonstrator data"],
            "linked_task_ids": ["S-MSR-06", "S-INL-05", "D-DEMO-04", "D-3.14.f", "P-3.14.f"],
            "source_ids": ["NRC_PART70", "NRC_PART74", "ORNL_MASS_ACCOUNTANCY"],
            "source_urls": [SOURCES[s] for s in ["NRC_PART70", "NRC_PART74", "ORNL_MASS_ACCOUNTANCY"]],
            "security_note": "The database specifies engineering and records requirements but excludes facility-specific alarm thresholds, adversary-useful layouts, or detailed protective strategies.",
        },
        "PB-WASTE-01": {
            "playbook_id": "PB-WASTE-01", "title": "Salt-processing waste, used salt, deactivation, and final disposition",
            "objective": "Provide an authorized path for every residual salt, sample, filter, sorbent, deposit, corrosion product, contaminated component, and decommissioning waste stream before the activity that creates it begins.",
            "execution_sequence": ["waste stream forecast", "characterization and material-accountability interface", "treatment/conditioning and package selection", "storage and transport authorization", "DOE return or licensed disposal route", "deactivation/decontamination plan", "cost and records closeout"],
            "linked_task_ids": ["D-DEMO-09", "D-3.9.f", "P-3.11.g", "P-OPT-06", "S-ITHF-46", "S-INL-20"],
            "source_ids": ["NRC_PART71", "NRC_PART70"],
            "source_urls": [SOURCES[s] for s in ["NRC_PART71", "NRC_PART70"]],
        },
        "PB-TEST-01": {
            "playbook_id": "PB-TEST-01", "title": "Experimental facility, test campaign, data qualification, and model-validation execution",
            "objective": "Use a staged evidence ladder: bench/separate-effects, ITHF, INL critical experiment, demonstrator, and commercial startup, with blind predictions and qualified datasets at each step.",
            "execution_sequence": ["PIRT and validation requirements", "facility/test article definition", "measurement uncertainty and pre-test predictions", "commissioning and readiness review", "campaign execution and exception control", "independent data qualification", "model validation and discrepancy closure", "topical/application evidence release"],
            "linked_task_ids": ["S-ITHF-02", "S-ITHF-34", "S-ITHF-41", "S-ITHF-42", "S-ITHF-43", "S-INL-18", "S-INL-19", "D-EXP-14"],
            "source_ids": ["ORNL_LSTL", "ORNL_FASTR", "NRIC_LOTUS", "INL_MCRE_PROGRAM"],
            "source_urls": [SOURCES[s] for s in ["ORNL_LSTL", "ORNL_FASTR", "NRIC_LOTUS", "INL_MCRE_PROGRAM"]],
        },
        "PB-SUPPLY-01": {
            "playbook_id": "PB-SUPPLY-01", "title": "Supplier qualification, long-lead procurement, manufacturing, and turnover",
            "objective": "Translate design requirements into executable supplier packages, reserve capacity early, verify manufacturing at source, and receive complete hardware and records without relying on final inspection alone.",
            "execution_sequence": ["market survey and RFI", "make/buy/partner decision", "supplier qualification and capacity reservation", "technical bid evaluation", "staged supplier design reviews", "source surveillance and FAT", "shipping/receiving/preservation", "installation and turnover", "second-source and obsolescence plan"],
            "linked_task_ids": ["S-0.2.d", "S-ITHF-24", "S-ITHF-25", "S-INL-13", "D-DEMO-07", "P-PKG-01", "P-PKG-03"],
            "source_ids": ["ORNL_FASTR", "INL_MCRE_PROGRAM"],
            "source_urls": [SOURCES[s] for s in ["ORNL_FASTR", "INL_MCRE_PROGRAM"]],
        },
    }


def _append_source_register(database: dict[str, Any]) -> None:
    existing_urls = {str(row.get("URL") or row.get("url") or "") for row in database.get("sources") or []}
    for source_id, url in SOURCES.items():
        if url in existing_urls:
            continue
        database.setdefault("sources", []).append({
            "Source ID": f"IMPL-{source_id}",
            "Type": "Official implementation reference",
            "Title / Description": source_id.replace("_", " ").title(),
            "Organization": "DOE / NRC / INL / ORNL as identified by URL",
            "URL": url,
            "Use in Plan": "Fuel supply, chemistry, processing, experiment, material-accountancy, transport, facility, or authorization implementation precedent; not a supplier quotation or commitment.",
            "Source Status": "External public source, accessed for v4.3 implementation planning",
        })
        existing_urls.add(url)


def _update_key_tasks(database: dict[str, Any]) -> None:
    by_id = {task["id"]: task for task in database["tasks"]}
    overrides: dict[str, dict[str, Any]] = {
        "D-RD-01": {
            "implementation_readiness": "Detailed 25-test chemistry and processing campaign defined; final salt family, host laboratory, radioactive confirmation scope, and processing architecture remain gated decisions.",
            "implementation_summary": "Execute a staged chemistry program beginning with feed qualification, carrier-salt purification, property/redox methods, and surrogate fission-product tests; down-select the minimum required processing architecture; qualify an integrated cleanup/off-gas/sampling skid; then confirm with INL irradiated salt and the 2029 demonstrator.",
            "linked_playbooks": ["PB-CHEM-01", "PB-FP-01", "PB-MCA-01", "PB-WASTE-01"],
        },
        "S-INL-05": {
            "implementation_readiness": "Fuel supply and synthesis pathway is now explicitly defined as DOE allocation plus commercial backup, with qualification batches, analytical acceptance, MC&A, packaging, transport, receipt, and disposition gates.",
            "implementation_summary": "Freeze fuel requirements in Q1 2027, pursue DOE HALEU allocation and an INL/national-laboratory synthesis route, maintain a commercial enrichment/deconversion backup, qualify the synthesis and analytical methods, produce accepted batches, reconcile material balances, and deliver under the host transport and MC&A plan.",
            "linked_playbooks": ["PB-FUEL-01", "PB-MCA-01", "PB-SUPPLY-01"],
        },
        "D-DEMO-04": {
            "implementation_readiness": "Demonstrator fuel-salt and processing equipment execution is tied to the fuel-supply and chemistry playbooks; the $30M cap assumes DOE-furnished or separately funded fissile material and major synthesis support.",
            "implementation_summary": "Design and procure only the processing functions selected by the 2027 architecture decision. Provide fuel receipt/storage, controlled heating/transfer, sampling, chemistry monitoring, particulate/off-gas interfaces, inventory measurement, drain/recovery, and maintainable waste handling; avoid unproven broad online reprocessing in the demonstrator.",
            "linked_playbooks": ["PB-FUEL-01", "PB-CHEM-01", "PB-FP-01", "PB-MCA-01", "PB-WASTE-01"],
        },
        "P-PKG-02": {
            "implementation_readiness": "Commercial fuel/material qualification package is decomposed through the fuel, chemistry, materials, safeguards, waste, and supply-chain playbooks with capacity reservation and supplier qualification starting before commercial construction.",
            "implementation_summary": "Reserve commercial enrichment/deconversion and salt-synthesis capacity, qualify the production facility and analytical methods, complete materials/irradiation qualification, establish packaging and transport, and produce the initial core and makeup inventory before 2035 fuel-load readiness.",
            "linked_playbooks": ["PB-FUEL-01", "PB-CHEM-01", "PB-MAT-01", "PB-MCA-01", "PB-SUPPLY-01", "PB-WASTE-01"],
        },
        "S-MSR-04": {
            "implementation_summary": "Build a species-group mass-balance model for salt, gas, deposits, filters, samples, and processing equipment; validate noble-gas transfer, aerosol/volatile capture, noble-metal plate-out, and irradiated-salt partitioning; then issue mechanistic source-term parameters with uncertainty and conditions of use.",
            "linked_playbooks": ["PB-FP-01", "PB-CHEM-01", "PB-MCA-01"],
        },
        "S-MSR-06": {
            "implementation_summary": "Define material balance areas and measurement points for receipt, storage, salt inventory, cover gas, deposits, samples, processing equipment, waste, and transfers; qualify measurement uncertainty and anomaly-resolution exercises before fuel receipt.",
            "linked_playbooks": ["PB-MCA-01", "PB-FUEL-01", "PB-CHEM-01"],
        },
        "S-MSR-05": {
            "implementation_summary": "Qualify online redox/chemistry and off-gas sensors, hot sampling, calibration, drift/fouling detection, and laboratory cross-checks in nonradioactive loops, then confirm under authorized fuel-salt and irradiated conditions.",
            "linked_playbooks": ["PB-CHEM-01", "PB-FP-01", "PB-TEST-01"],
        },
    }
    for tid, changes in overrides.items():
        task = by_id.get(tid)
        if not task:
            continue
        plan = task.setdefault("implementation_plan", {})
        plan.update(changes)
        task["description"] = task["description"].rstrip() + " Implementation baseline: " + changes["implementation_summary"]
        task.setdefault("change_control", {}).setdefault("residual_decisions_assumptions", []).append(
            "Version 4.3 implementation details identify the recommended execution route and evidence ladder; final salt chemistry, fuel ownership, supplier/facility commitments, and radioactive work authorization remain controlled decisions."
        )


def _update_cost_notes(database: dict[str, Any]) -> None:
    by_id = {task["id"]: task for task in database["tasks"]}
    for tid in ["D-RD-01", "S-MTH-04", "S-MSR-02", "S-MSR-04", "S-MSR-05", "S-MSR-06", "S-MSR-09", "S-INL-05", "D-DEMO-04", "P-PKG-02"]:
        task = by_id.get(tid)
        if not task:
            continue
        task["cost"].setdefault("implementation_cost_basis_v4_3", {})
        task["cost"]["implementation_cost_basis_v4_3"] = {
            "basis": "The task cost now maps to the detailed implementation playbooks and experiment/fuel-supply matrices. The playbook rows are non-additive execution detail, not additional program cost.",
            "included_scope": task.get("implementation_plan", {}).get("linked_playbooks", []),
            "reestimate_triggers": [
                "final salt family or fissile-feed form changes",
                "DOE-furnished material or national-laboratory services are not available on the assumed terms",
                "radioactive confirmation or processing scope expands beyond the defined surrogate/authorized program",
                "supplier, laboratory, transport-package, or hot-cell quotations differ materially from the planning allowance",
                "processing architecture changes from minimal/off-gas-only to broader online removal",
            ],
        }
    demo = by_id.get("D-DEMO-04")
    if demo:
        demo["cost"]["demonstrator_cap_assumption"] = (
            "The $3.0M direct non-labor line covers installed handling/processing equipment and project-paid consumables. It does not include the economic value of DOE-furnished fissile material or major national-laboratory synthesis services. If those are not furnished or separately funded, the $30M demonstrator cap requires an explicit rebaseline."
        )


def migrate(database: dict[str, Any]) -> dict[str, Any]:
    db = copy.deepcopy(database)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    db["meta"]["version"] = VERSION
    db["meta"]["application_version"] = VERSION
    db["meta"]["generated"] = now
    db["meta"]["data_date"] = now[:10]
    db["meta"]["engineering_work_package_schema"] = EWP_VERSION
    db["meta"]["implementation_plan_schema"] = "1.0"
    db["meta"]["source_baseline"] = db["meta"].get("source_baseline", "") + " Version 4.3 adds execution-level fuel-supply, chemistry, processing, experiments, procurement, facility, acceptance, and handoff detail for every task."
    db["project"]["description"] = "Internal integrated molten-salt-reactor methods, fuel supply, chemistry and materials validation, experiments, DOE-authorized demonstrator, and commercial power-reactor engineering and licensing program."
    db["project"]["implementation_principles"] = [
        "Use staged evidence: supplier/feed qualification, bench and separate-effects tests, ITHF, INL critical experiment, demonstrator, and commercial startup.",
        "Use stable nonradioactive surrogates for process down-selection and perform uranium-bearing or irradiated confirmation only in authorized facilities.",
        "Do not assume broad online fuel-salt reprocessing. Select the minimum processing architecture justified by safety, chemistry, reactivity, source term, safeguards, waste, operability, and lifecycle economics.",
        "Pursue DOE HALEU allocation for the demonstrator and critical experiment while developing a commercial enrichment/deconversion and fuel-salt synthesis backup and commercial scaling route.",
        "Retain owner control of requirements, technical basis, acceptance, configuration, regulatory commitments, and operating knowledge; purchase bounded specialist capability and facility time.",
    ]

    all_tasks = list(db.get("tasks") or [])
    for module in (db.get("pathway_modules") or {}).values():
        for key in ("demonstrator", "power_reactor"):
            all_tasks.extend(module.get(key) or [])
    for task in all_tasks:
        task["implementation_plan"] = _generic_plan(task)
        task.setdefault("execution", {})["implementation_ready"] = True
        task["execution"]["detail_level"] = "engineering_ready_v4_3"
        task["engineering_work_package"]["implementation_plan_version"] = "1.0"
        task["engineering_work_package"]["implementation_summary"] = task["implementation_plan"]["implementation_summary"]

    db["implementation_playbooks"] = {"PB-FUEL-01": _fuel_playbook(), "PB-CHEM-01": _chem_playbook(), **_simple_playbooks()}
    db.setdefault("test_matrices", {})["fuel_salt_chemistry_and_processing"] = db["implementation_playbooks"]["PB-CHEM-01"]["experiment_matrix"]
    db["fuel_supply_plan"] = db["implementation_playbooks"]["PB-FUEL-01"]
    db["chemistry_processing_plan"] = db["implementation_playbooks"]["PB-CHEM-01"]

    _update_key_tasks(db)
    _update_cost_notes(db)
    _append_source_register(db)

    new_risks = [
        {"Risk ID": "R-IMPL-01", "Concept": "Shared", "Category": "Fuel supply", "Risk Statement": "DOE allocation, enrichment/deconversion capacity, or fuel-salt synthesis commitment is not secured in time for the 2029 demonstrator campaign.", "Likelihood": "Medium", "Impact": "High", "Score": 15, "Level": "High", "Owner": "Program / Procurement / Fuel Lead", "Mitigation / Preventive Action": "Submit DOE allocation request in the first program year, execute commercial backup RFI/capacity options, qualify synthesis and analytical routes early, and protect non-fuel commissioning as a schedule fallback.", "Trigger": "No conditional source and synthesis commitment by 2027-06-30", "Status": "Open"},
        {"Risk ID": "R-IMPL-02", "Concept": "Shared", "Category": "Chemistry", "Risk Statement": "The selected fuel-salt processing architecture is not demonstrated at engineering scale or creates unacceptable fuel loss, waste, safeguards, or maintenance burden.", "Likelihood": "Medium", "Impact": "High", "Score": 15, "Level": "High", "Owner": "Chemistry / Fuel / Safeguards / Operations", "Mitigation / Preventive Action": "Down-select the minimum processing scope using surrogate tests, repeated-cycle skid operation, closed mass balance, actinide retention, waste characterization, and maintainability criteria before demonstrator freeze.", "Trigger": "No processing architecture decision by 2027-12-31", "Status": "Open"},
        {"Risk ID": "R-IMPL-03", "Concept": "Shared", "Category": "Chemistry data", "Risk Statement": "Surrogate chemistry and off-gas tests do not adequately predict irradiated fuel-salt behavior.", "Likelihood": "Medium", "Impact": "High", "Score": 15, "Level": "High", "Owner": "Chemistry / Source Term / INL Experiment", "Mitigation / Preventive Action": "Design matched surrogate and irradiated-salt sample matrices, preserve operating histories and mass balances, and use INL critical-experiment and demonstrator samples to close extrapolation uncertainty.", "Trigger": "Irradiated confirmation differs from surrogate model outside the acceptance band", "Status": "Open"},
        {"Risk ID": "R-IMPL-04", "Concept": "Demonstrator", "Category": "Cost", "Risk Statement": "The $30M direct demonstrator cap is invalid if fissile material value or major fuel-salt synthesis services are not DOE-furnished or separately funded.", "Likelihood": "Medium", "Impact": "High", "Score": 15, "Level": "High", "Owner": "Program / Finance / Fuel Supply", "Mitigation / Preventive Action": "Make the funding/ownership assumption explicit in DOE/host negotiations and establish an early rebaseline gate rather than absorbing fuel cost into hardware contingency.", "Trigger": "DOE/host agreement requires Project-MSR to pay unbudgeted fissile material or synthesis costs", "Status": "Open"},
        {"Risk ID": "R-IMPL-05", "Concept": "Power Reactor", "Category": "Commercial fuel", "Risk Statement": "Commercial initial-core and makeup supply capacity is not reserved early enough to support 2035 operation.", "Likelihood": "Medium", "Impact": "High", "Score": 15, "Level": "High", "Owner": "Commercial Program / Procurement / Fuel Lead", "Mitigation / Preventive Action": "Execute capacity reservation and option agreements before commercial construction, qualify the synthesis/analytical facility by 2032, and maintain an alternate supplier for the schedule-critical step.", "Trigger": "No credible commercial supply schedule by 2029 construction authorization", "Status": "Open"},
    ]
    existing_risk_ids = {r.get("Risk ID") or r.get("risk_id") for r in db.get("risks") or []}
    db.setdefault("risks", []).extend(r for r in new_risks if r["Risk ID"] not in existing_risk_ids)

    new_milestones = [
        {"Milestone ID": "M-IMPL-01", "Concept": "Shared", "Milestone": "Fuel requirements, chemistry family, ownership and supply strategy approved", "Baseline Date": "2027-03-31", "Responsible Organization": "Fuel / Physics / Chemistry / Program", "Acceptance Basis": "Approved fuel requirements specification and supply/ownership decision record"},
        {"Milestone ID": "M-IMPL-02", "Concept": "Demonstrator", "Milestone": "DOE allocation/primary source and commercial backup route conditionally committed", "Baseline Date": "2027-06-30", "Responsible Organization": "Program / Procurement / DOE Host", "Acceptance Basis": "Conditional allocation or source agreement plus commercial backup plan"},
        {"Milestone ID": "M-IMPL-03", "Concept": "Shared", "Milestone": "Fuel-salt processing architecture down-selected", "Baseline Date": "2027-12-31", "Responsible Organization": "Chemistry / Fuel / Safety / Safeguards / Waste / Operations", "Acceptance Basis": "Trade study and surrogate experiment evidence select the minimum justified processing scope"},
        {"Milestone ID": "M-IMPL-04", "Concept": "Demonstrator", "Milestone": "Fuel-salt synthesis and analytical qualification batch accepted", "Baseline Date": "2028-06-30", "Responsible Organization": "Fuel / Chemistry / Host / QA", "Acceptance Basis": "Qualification batch, independent analysis, mass balance, and production authorization complete"},
        {"Milestone ID": "M-IMPL-05", "Concept": "Demonstrator", "Milestone": "Integrated salt processing, sampling and off-gas skid qualified", "Baseline Date": "2028-09-30", "Responsible Organization": "Chemistry / Test / Mechanical / I&C", "Acceptance Basis": "Repeated-cycle campaign meets performance, retention, mass-balance, maintainability, and waste criteria"},
        {"Milestone ID": "M-IMPL-06", "Concept": "Demonstrator", "Milestone": "Demonstrator fuel production batch accepted for shipment/use", "Baseline Date": "2028-12-31", "Responsible Organization": "Fuel / Host / MC&A / QA", "Acceptance Basis": "Production records, certificates, independent checks, package/transport readiness, and disposition plan accepted"},
        {"Milestone ID": "M-IMPL-07", "Concept": "Shared", "Milestone": "INL irradiated-salt chemistry and source-term confirmation released", "Baseline Date": "2029-09-30", "Responsible Organization": "INL / Chemistry / Source Term / Safeguards", "Acceptance Basis": "Qualified hot-cell/radiochemical dataset linked to operating history and mass balance"},
        {"Milestone ID": "M-IMPL-08", "Concept": "Power Reactor", "Milestone": "Commercial fuel supply capacity reserved and production facility qualification plan approved", "Baseline Date": "2029-12-31", "Responsible Organization": "Commercial Program / Procurement / Fuel", "Acceptance Basis": "Capacity agreements, supplier qualification plan, and initial-core schedule support 2035 fuel load"},
        {"Milestone ID": "M-IMPL-09", "Concept": "Power Reactor", "Milestone": "Commercial fuel-salt production and analytical facility qualified", "Baseline Date": "2032-12-31", "Responsible Organization": "Fuel / Chemistry / Supplier / QA", "Acceptance Basis": "Production-scale qualification batches and quality/MC&A/transport systems accepted"},
    ]
    existing_mid = {m.get("Milestone ID") for m in db.get("milestones") or []}
    db.setdefault("milestones", []).extend(m for m in new_milestones if m["Milestone ID"] not in existing_mid)

    dq = db.setdefault("data_quality", {})
    dq["implementation_ready_task_count"] = len(all_tasks)
    dq["implementation_playbook_count"] = len(db["implementation_playbooks"])
    dq["chemistry_processing_test_count"] = len(db["test_matrices"]["fuel_salt_chemistry_and_processing"])
    dq["application_tabs"] = 13
    dq["automated_test_count"] = 52
    dq["implementation_detail_version"] = VERSION
    db["planning_profile"]["version"] = VERSION
    db["financials"]["implementation_detail_v4_3"] = {
        "basis": "Implementation playbooks and experiment matrices are crosswalks into existing accounting tasks and are not additive to program totals.",
        "demonstrator_fuel_cap_assumption": "DOE-furnished or separately funded fissile material and major national-laboratory synthesis services; otherwise rebaseline the $30M direct package.",
        "cost_reestimate_trigger": "Obtain laboratory work orders, DOE/host agreements, fuel allocation terms, supplier quotations, transport-package plan, and commercial capacity reservations before the next cost baseline.",
    }
    return db


def main() -> int:
    parser = argparse.ArgumentParser(description="Expand Project-MSR v4.2.2 to execution-focused v4.3.0.")
    parser.add_argument("--input", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "data" / "project_msr_database.full.json")
    args = parser.parse_args()
    database = load_sharded_database(args.input, verify_semantic_hash=True)
    migrated = migrate(database)
    args.output.write_text(json.dumps(migrated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.output} ({args.output.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
