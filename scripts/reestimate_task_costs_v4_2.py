from __future__ import annotations

import calendar
import csv
import json
import math
import re
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data_loader import load_database
from src.database_sharding import write_sharded_database
DB_PATH = ROOT / "data" / "project_msr_database.manifest.json"
SCHEMA_PATH = ROOT / "data" / "project_msr_database.schema.json"
AUDIT_CSV = ROOT / "data" / "task_cost_audit_v4_2.csv"

VERSION = "4.2.0"
PRODUCTIVE_HOURS_PER_FTE_YEAR = 1_680
NRC_REDUCED_RATE_PER_HOUR = 148.0
NRC_FULL_RATE_PER_HOUR = 318.0

# Fully burdened 2026 planning rates. These are owner/contractor blended rates,
# not salaries. They include salary, benefits, payroll burden, facilities,
# ordinary software, indirect labor, and corporate overhead but exclude task-
# specific subcontracts, laboratory services, major software, equipment, travel,
# regulatory review fees, and risk allowance.
ROLE_RATES_KUSD_PER_FTE_YEAR: dict[str, float] = {
    "CS": 225.0,
    "CM": 240.0,
    "DATA": 230.0,
    "EE": 220.0,
    "MAT": 250.0,
    "IC": 245.0,
    "ME": 225.0,
    "OPS": 210.0,
    "PRA": 255.0,
    "PROC": 210.0,
    "RAD": 220.0,
    "RPX": 255.0,
    "SA": 260.0,
    "SE": 245.0,
    "TEST": 215.0,
    "TH": 250.0,
    "CE": 315.0,
    "CNO": 385.0,
    "CTO": 365.0,
    "COST": 220.0,
    "DC": 165.0,
    "PD": 335.0,
    "PC": 210.0,
    "PM": 290.0,
    "CYB": 250.0,
    "ENV": 225.0,
    "HFE": 230.0,
    "LIC": 260.0,
    "QA": 215.0,
    "LAW": 365.0,
}

PATTERN_BASE_FTE = {
    "design_engineering": 0.30,
    "analysis_model": 0.38,
    "test_experiment": 0.45,
    "management_control": 0.18,
    "licensing_product": 0.32,
    "operations_program": 0.28,
    "procurement_fabrication": 0.38,
    "construction_installation": 0.55,
    None: 0.25,
}

SCOPE_EFFORT_FACTOR = {
    "program_backbone": 0.25,
    "methods_and_topicals": 0.55,
    "demonstrator_engineering": 0.14,
    "integral_test_facility": 0.35,
    "critical_experiment": 0.40,
    "demonstrator_experiments": 0.40,
    "demonstrator_licensing": 0.50,
    "power_reactor_engineering": 0.30,
    "power_reactor_licensing": 0.70,
    "power_reactor_construction": 0.60,
    None: 0.50,
}

DOMAIN_EFFORT_FACTOR = {
    "licensing_authorization": 1.00,
    "systems_engineering": 1.10,
    "quality_configuration": 0.90,
    "instrumentation_controls": 1.20,
    "site_environmental": 1.10,
    "thermal_hydraulics": 1.25,
    "materials": 1.25,
    "safety_analysis": 1.25,
    "test_commissioning": 1.15,
    "operations_maintenance": 1.00,
    "chemistry": 1.20,
    "risk_pra": 1.30,
    "project_controls": 0.80,
    "human_factors": 1.00,
    "civil_structural": 1.20,
    "neutronics": 1.35,
    "electrical": 1.15,
    "procurement_fabrication": 1.00,
    "construction_installation": 1.00,
    None: 1.00,
}

SCOPE_MINIMUM_FTE = {
    "program_backbone": 0.10,
    "methods_and_topicals": 0.30,
    "demonstrator_engineering": 0.10,
    "integral_test_facility": 0.20,
    "critical_experiment": 0.25,
    "demonstrator_experiments": 0.25,
    "demonstrator_licensing": 0.30,
    "power_reactor_engineering": 0.25,
    "power_reactor_licensing": 0.40,
    "power_reactor_construction": 0.40,
}

PRIOR_EFFORT_MULTIPLIER = {
    "program_backbone": 1.15,
    "methods_and_topicals": 1.25,
    "demonstrator_engineering": 1.40,
    "integral_test_facility": 1.25,
    "critical_experiment": 1.40,
    "demonstrator_experiments": 1.40,
    "demonstrator_licensing": 1.50,
    "power_reactor_engineering": 1.35,
    "power_reactor_licensing": 1.50,
    "power_reactor_construction": 1.20,
}

# Task-specific floors are used only where the work package clearly represents
# a major integrated engineering product whose cost would be understated by a
# generic per-document estimate. The remaining tasks are estimated from their
# own inputs, steps, outputs, requirements, tools, hold points, duration, domain,
# scope, and criticality.
MAJOR_TASK_FTE_FLOORS: dict[str, float] = {
    "D-3.4.c": 2.5,
    "P-3.4.c": 10.0,
    "D-3.4.d": 2.2,
    "P-3.4.d": 8.0,
    "D-3.15.b": 2.0,
    "P-3.15.b": 7.0,
    "D-3.15.d": 1.8,
    "P-3.15.d": 7.0,
    "D-3.15.e": 2.0,
    "P-3.15.e": 8.0,
    "S-MTH-02": 8.0,
    "S-MTH-03": 10.0,
    "S-MTH-04": 8.0,
    "S-MTH-05": 8.0,
    "S-MTH-06": 10.0,
    "S-MTH-08": 7.0,
    "S-MSR-02": 5.0,
    "S-MSR-03": 7.0,
    "S-MSR-04": 6.0,
    "S-MSR-05": 5.0,
    "S-MSR-07": 5.0,
    "S-MSR-09": 7.0,
    "P-PKG-01": 18.0,
    "P-PKG-02": 25.0,
    "P-PKG-03": 15.0,
    "P-PKG-04": 12.0,
    "P-PKG-05": 20.0,
    "P-PKG-06": 70.0,
    "P-PKG-07": 35.0,
    "P-PKG-08": 10.0,
    "S-PKG-01": 4.0,
    "S-PKG-02": 4.0,
    "S-PKG-03": 3.0,
    "S-PKG-04": 3.0,
    "S-PKG-05": 3.0,
    "P-3.14.a": 5.0,
    "P-3.14.b": 5.0,
    "P-3.14.c": 6.0,
    "P-3.14.d": 5.0,
    "P-3.14.e": 6.0,
    "P-3.14.f": 4.0,
    "P-3.14.g": 6.0,
    "P-3.14.h": 8.0,
    "P-3.14.i": 5.0,
    "P-3.14.j": 4.0,
    "P-3.14.k": 4.0,
    "P-3.14.n": 4.0,
    "P-3.14.o": 3.0,
    "P-3.14.p": 4.0,
    "P-13.a": 3.0,
    "P-13.b": 3.0,
    "P-13.c": 2.5,
    "P-13.d": 3.0,
    "P-13.e": 3.0,
    "P-13.f": 3.0,
    "P-13.g": 3.0,
    "P-13.h": 3.0,
    "P-13.i": 2.5,
}

ROUTE_FTE_FLOORS: dict[str, float] = {
    # DOE Launch Pad demonstrator authorization.
    "D-LP2-01": 2.0,
    "D-LP2-02": 3.0,
    "D-LP2-03U": 4.0,
    "D-LP2-03I": 3.5,
    "D-LP2-04": 2.0,
    "D-LP2-05": 4.0,
    "D-LP2-06": 10.0,
    "D-LP2-07": 4.0,
    "D-LP2-08": 3.0,
    "D-LP2-09": 4.0,
    "D-LP2-10": 5.0,
    "D-LP2-11": 6.0,
    "D-LP2-12": 6.0,
    "D-LP2-13": 8.0,
    "D-LP2-14": 3.0,
    "D-LP2-15": 6.0,
    "D-LP2-16": 7.0,
    "D-LP2-17": 4.0,
    # Part 50.
    "P50-01": 4.0,
    "P50-02": 10.0,
    "P50-03": 10.0,
    "P50-04": 20.0,
    "P50-05": 4.0,
    "P50-06": 14.0,
    "P50-07": 8.0,
    "P50-08": 4.0,
    "P50-09": 3.0,
    "P50-10": 16.0,
    "P50-11": 10.0,
    "P50-12": 24.0,
    "P50-13": 14.0,
    "P50-14": 5.0,
    "P50-15": 10.0,
    "P50-16": 14.0,
    "P50-17": 8.0,
    "P50-18": 4.0,
    "P50-19": 5.0,
    # Part 52.
    "P52-01": 5.0,
    "P52-02": 12.0,
    "P52-E01": 14.0,
    "P52-E02": 10.0,
    "P52-03": 28.0,
    "P52-D01": 18.0,
    "P52-D02": 16.0,
    "P52-D03": 8.0,
    "P52-04": 14.0,
    "P52-05": 10.0,
    "P52-06": 24.0,
    "P52-07": 18.0,
    "P52-08": 8.0,
    "P52-09": 4.0,
    "P52-10": 8.0,
    "P52-11": 12.0,
    "P52-12": 18.0,
    "P52-13": 10.0,
    "P52-14": 8.0,
    "P52-15": 4.0,
    "P52-16": 5.0,
    # Part 53.
    "P53-01": 5.0,
    "P53-02": 10.0,
    "P53-03": 14.0,
    "P53-04": 18.0,
    "P53-05": 12.0,
    "P53-06": 12.0,
    "P53-07": 6.0,
    "P53-08": 10.0,
    "P53-09": 12.0,
    "P53-10": 22.0,
    "P53-11": 5.0,
    "P53-C01": 4.0,
    "P53-C02": 16.0,
    "P53-P01": 12.0,
    "P53-P02": 12.0,
    "P53-P03": 24.0,
    "P53-12": 8.0,
    "P53-13": 16.0,
    "P53-14": 10.0,
    "P53-15": 5.0,
    "P53-16": 8.0,
}

PATTERN_NONLABOR_BASE_KUSD = {
    "management_control": 15.0,
    "design_engineering": 35.0,
    "analysis_model": 50.0,
    "licensing_product": 45.0,
    "test_experiment": 75.0,
    "operations_program": 25.0,
    "procurement_fabrication": 60.0,
    "construction_installation": 100.0,
    None: 30.0,
}

SCOPE_NONLABOR_FACTOR = {
    "program_backbone": 0.60,
    "methods_and_topicals": 2.40,
    "demonstrator_engineering": 0.80,
    "integral_test_facility": 1.80,
    "critical_experiment": 2.40,
    "demonstrator_experiments": 1.80,
    "demonstrator_licensing": 1.50,
    "power_reactor_engineering": 2.00,
    "power_reactor_licensing": 2.50,
    "power_reactor_construction": 3.00,
    None: 1.00,
}

DOMAIN_NONLABOR_FACTOR = {
    "neutronics": 1.40,
    "thermal_hydraulics": 1.40,
    "materials": 1.50,
    "chemistry": 1.35,
    "risk_pra": 1.35,
    "safety_analysis": 1.30,
    "instrumentation_controls": 1.25,
    "civil_structural": 1.25,
    "site_environmental": 1.25,
    "test_commissioning": 1.25,
    "construction_installation": 1.20,
    "procurement_fabrication": 1.15,
    "licensing_authorization": 1.15,
}

MAJOR_TASK_DIRECT_NONLABOR_FLOORS_KUSD = {
    "D-3.4.c": 250.0,
    "P-3.4.c": 850.0,
    "D-3.4.d": 200.0,
    "P-3.4.d": 700.0,
    "D-3.15.b": 200.0,
    "P-3.15.b": 700.0,
    "D-3.15.d": 150.0,
    "P-3.15.d": 500.0,
    "D-3.15.e": 200.0,
    "P-3.15.e": 600.0,
    "S-MTH-02": 900.0,
    "S-MTH-03": 1_200.0,
    "S-MTH-04": 900.0,
    "S-MTH-05": 1_100.0,
    "S-MTH-06": 1_200.0,
    "S-MTH-08": 700.0,
    "S-MSR-02": 700.0,
    "S-MSR-03": 900.0,
    "S-MSR-04": 1_000.0,
    "S-MSR-05": 800.0,
    "S-MSR-07": 700.0,
    "S-MSR-09": 1_200.0,
}

COMPONENT_KEYS = [
    "external_engineering_and_lab_services_kusd",
    "software_compute_and_data_kusd",
    "equipment_materials_and_fabrication_kusd",
    "facility_test_and_field_operations_kusd",
    "regulatory_review_fees_kusd",
    "legal_hearing_and_advisory_kusd",
    "travel_and_field_support_kusd",
    "other_direct_kusd",
]


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def duration_years(start: str, finish: str) -> float:
    return max(((parse_date(finish) - parse_date(start)).days + 1) / 365.25, 1 / 12)


def annual_fractions(start: str, finish: str, weights: dict[str, float] | None = None) -> dict[str, float]:
    start_date = parse_date(start)
    finish_date = parse_date(finish)
    raw: dict[str, float] = {}
    for year in range(start_date.year, finish_date.year + 1):
        low = max(start_date, date(year, 1, 1))
        high = min(finish_date, date(year, 12, 31))
        if high >= low:
            raw[str(year)] = float((high - low).days + 1) * float((weights or {}).get(str(year), 1.0))
    total = sum(raw.values()) or 1.0
    return {year: value / total for year, value in raw.items()}


def task_year_weights(task: dict[str, Any], portfolio_weights: dict[str, float]) -> dict[str, float]:
    start = parse_date(task["schedule"]["start"])
    finish = parse_date(task["schedule"]["finish"])
    years = list(range(start.year, finish.year + 1))
    denominator = max(len(years) - 1, 1)
    shape = str(task.get("schedule", {}).get("loading_shape") or "flat").lower()
    override = task.get("schedule", {}).get("year_weight_multipliers") or {}
    result: dict[str, float] = {}
    for index, year in enumerate(years):
        position = index / denominator
        if shape == "back_loaded":
            shape_factor = 0.42 + 1.38 * (position**1.35)
        elif shape == "front_loaded":
            shape_factor = 1.75 - 1.05 * (position**0.8)
        elif shape == "bell":
            shape_factor = 0.62 + 1.05 * (1.0 - abs(2.0 * position - 1.0))
        elif shape == "milestone_backloaded":
            shape_factor = 0.30 + 1.70 * (position**1.7)
        else:
            shape_factor = 1.0
        result[str(year)] = float(portfolio_weights.get(str(year), 1.0)) * shape_factor * float(override.get(str(year), 1.0))
    return result


def package_list_count(task: dict[str, Any], key: str) -> int:
    value = (task.get("engineering_work_package") or {}).get(key) or []
    return len(value) if isinstance(value, list) else 0


def keyword_multiplier(name: str) -> float:
    text = name.lower()
    multiplier = 1.0
    groups = [
        (
            1.45,
            [
                "core nuclear",
                "reactivity control",
                "mechanistic source term",
                "integrated safety case",
                "combined license application",
                "design certification application",
                "preliminary safety analysis report",
                "final safety analysis report",
                "critical experiment",
                "initial criticality",
                "power ascension",
            ],
        ),
        (
            1.35,
            [
                "system thermal-hydraulics",
                "thermal-hydraulics methods",
                "neutronics",
                "multiphysics",
                "severe accident",
                "containment",
                "pra/sre",
                "probabilistic risk",
                "safety architecture",
                "reactor coolant system",
                "primary system",
                "fuel-salt",
                "fuel salt",
                "materials qualification",
                "design-by-analysis",
                "seismic/ssi",
                "digital i&c",
                "software lifecycle",
            ],
        ),
        (
            1.25,
            [
                "topical report",
                "source term",
                "safety analysis",
                "accident analysis",
                "integral thermal",
                "freeze-drain",
                "corrosion",
                "criticality",
                "environmental report",
                "technical specifications",
                "itaac",
                "operating license",
                "construction permit",
            ],
        ),
        (
            1.15,
            [
                "detailed design",
                "engineering design",
                "validation",
                "verification",
                "qualification",
                "commissioning",
                "construction readiness",
                "procurement specification",
                "factory acceptance",
                "site acceptance",
            ],
        ),
    ]
    for candidate, terms in groups:
        if any(term in text for term in terms):
            multiplier = max(multiplier, candidate)
    if any(term in text for term in ["status reporting", "meeting cadence", "dashboard", "administrative calendar", "index maintenance"]):
        multiplier *= 0.80
    return multiplier


def concept_floor(task: dict[str, Any], demonstrator: float, power: float, shared: float | None = None) -> float:
    concept = str(task.get("concept") or "")
    if concept == "Demonstrator":
        # Demonstrator engineering uses a lean owner team and bounded specialist work packages.
        # The task total remains realistic because the external work is represented separately
        # in direct non-labor rather than being disguised as permanent owner FTE.
        return demonstrator * 0.25
    if concept == "Power Reactor":
        return power * 0.55
    return (shared * 0.65) if shared is not None else max(demonstrator, power) * 0.50


def concept_cost_floor(task: dict[str, Any], demonstrator: float, power: float, shared: float | None = None) -> float:
    concept = str(task.get("concept") or "")
    if concept == "Demonstrator":
        return demonstrator
    if concept == "Power Reactor":
        return power
    return shared if shared is not None else max(demonstrator, power) * 0.75


def keyword_fte_floor(task: dict[str, Any]) -> float:
    name = str(task.get("name") or "").lower()
    package = task.get("engineering_work_package") or {}
    pattern = package.get("work_pattern")
    floor = 0.0
    rules: list[tuple[list[str], tuple[float, float, float | None]]] = [
        (["psha", "gmrs", "safe shutdown earthquake", "seismic hazard analysis"], (1.75, 4.50, 3.00)),
        (["soil-structure interaction", "ssi models", "in-structure response spectra", "isrs generation"], (1.50, 4.00, 2.50)),
        (["asme section iii pressure boundary", "design-by-analysis", "pressure boundary design"], (1.75, 5.50, 3.50)),
        (["asme section iii piping", "piping stress", "support design"], (1.50, 4.50, 3.00)),
        (["safety i&c functional requirements", "safety i&c architecture", "digital safety architecture"], (2.00, 5.50, 3.50)),
        (["software lifecycle", "software v&v", "software verification"], (1.75, 5.00, 3.00)),
        (["diversity & defense-in-depth", "d3 assessment"], (1.25, 3.50, 2.25)),
        (["cybersecurity program", "critical digital asset", "cyber architecture"], (1.25, 3.50, 2.25)),
        (["internal events", "fire pra", "seismic pra", "low power & shutdown", "lpsd pra"], (2.00, 6.00, 4.00)),
        (["pra peer review", "peer review & f&o", "technical adequacy"], (1.25, 3.50, 2.50)),
        (["integrated system validation", "isv - execution", "isv execution"], (2.00, 5.00, 3.50)),
        (["environmental report", "nepa", "environmental impact statement"], (1.50, 4.00, 3.00)),
        (["hydrology & flooding", "probable maximum flood", "pmf/pmss"], (1.00, 3.00, 2.00)),
        (["meteorology & atmospheric", "atmospheric dispersion"], (0.80, 2.25, 1.50)),
        (["nuclear concrete design", "nuclear steel design", "foundation design"], (1.25, 4.00, 2.75)),
        (["equipment qualification", "environmental & seismic qualification"], (1.00, 3.00, 2.00)),
        (["containment pressure-temperature", "containment thermal-hydraulics"], (1.50, 4.50, 3.00)),
        (["radiological consequence", "mechanistic source term", "source term definition"], (1.25, 3.50, 2.50)),
        (["fuel handling", "criticality", "material accountancy"], (1.25, 3.50, 2.50)),
        (["materials, chemistry", "corrosion", "welding, nde", "irradiation qualification"], (1.00, 3.00, 2.00)),
        (["hvac & air cleaning", "cooling water systems", "electric power", "onsite ac power"], (1.00, 3.00, 2.00)),
        (["initial criticality", "power ascension", "hot functional testing", "preoperational tests"], (1.50, 4.00, 2.75)),
        (["technical specifications", "setpoint methodology"], (1.25, 3.50, 2.50)),
        (["operator licensing", "simulator program"], (1.25, 3.50, 2.50)),
        (["security plan", "physical security design", "vital area"], (1.25, 3.50, 2.50)),
    ]
    for terms, values in rules:
        if any(term in name for term in terms):
            floor = max(floor, concept_floor(task, *values))
    if "fsar chapter" in name and any(term in name for term in ["draft", "author", "final", "records"]):
        floor = max(floor, concept_floor(task, 1.00, 3.00, 2.00))
    if pattern == "licensing_product" and task.get("task_scope") not in {"program_backbone"}:
        floor = max(floor, concept_floor(task, 0.80, 2.00, 1.50))
    return floor


def keyword_nonlabor_floor_kusd(task: dict[str, Any]) -> float:
    name = str(task.get("name") or "").lower()
    floor = 0.0
    rules: list[tuple[list[str], tuple[float, float, float | None]]] = [
        (["psha", "gmrs", "seismic hazard analysis"], (350.0, 1_000.0, 700.0)),
        (["soil-structure interaction", "ssi models", "isrs generation"], (300.0, 900.0, 600.0)),
        (["asme section iii pressure boundary", "design-by-analysis", "pressure boundary design"], (300.0, 900.0, 600.0)),
        (["asme section iii piping", "piping stress"], (250.0, 750.0, 500.0)),
        (["safety i&c functional requirements", "safety i&c architecture"], (200.0, 600.0, 400.0)),
        (["software lifecycle", "software v&v"], (200.0, 600.0, 400.0)),
        (["internal events", "fire pra", "seismic pra", "low power & shutdown"], (250.0, 800.0, 550.0)),
        (["integrated system validation", "isv execution"], (350.0, 1_000.0, 700.0)),
        (["environmental report", "nepa", "environmental impact statement"], (300.0, 900.0, 650.0)),
        (["hydrology & flooding", "pmf/pmss"], (200.0, 600.0, 400.0)),
        (["meteorology & atmospheric", "atmospheric dispersion"], (150.0, 450.0, 300.0)),
        (["nuclear concrete design", "nuclear steel design"], (250.0, 750.0, 500.0)),
        (["equipment qualification", "environmental & seismic qualification"], (200.0, 600.0, 400.0)),
        (["containment pressure-temperature", "containment thermal-hydraulics"], (250.0, 750.0, 500.0)),
        (["radiological consequence", "mechanistic source term"], (200.0, 600.0, 400.0)),
        (["initial criticality", "power ascension", "hot functional testing"], (300.0, 900.0, 600.0)),
        (["simulator program", "operator licensing"], (250.0, 750.0, 500.0)),
        (["physical security design", "vital area"], (250.0, 750.0, 500.0)),
    ]
    for terms, values in rules:
        if any(term in name for term in terms):
            floor = max(floor, concept_cost_floor(task, *values))
    return floor


def base_target_fte(task: dict[str, Any]) -> float:
    package = task.get("engineering_work_package") or {}
    pattern = package.get("work_pattern")
    scope = task.get("task_scope")
    domain = package.get("primary_domain")
    complexity = (
        PATTERN_BASE_FTE.get(pattern, 0.25)
        + 0.038 * package_list_count(task, "execution_procedure")
        + 0.015 * package_list_count(task, "controlled_inputs")
        + 0.055 * package_list_count(task, "deliverable_register")
        + 0.022 * package_list_count(task, "requirements_and_guidance")
        + 0.012 * package_list_count(task, "toolchain")
        + 0.035 * package_list_count(task, "required_reviews_and_hold_points")
        + 0.018 * package_list_count(task, "engineering_questions_to_close")
    )
    target = (
        complexity
        * SCOPE_EFFORT_FACTOR.get(scope, 0.50)
        * DOMAIN_EFFORT_FACTOR.get(domain, 1.00)
        * keyword_multiplier(str(task.get("name") or ""))
    )
    if task.get("schedule", {}).get("critical"):
        target *= 1.10
    months = float(task.get("schedule", {}).get("duration_months") or 12.0)
    target *= max(0.85, min(1.25, (months / 12.0) ** 0.16))
    target = max(target, SCOPE_MINIMUM_FTE.get(scope, 0.25))
    current = float(task.get("resources", {}).get("fte_years") or 0.0)
    target = max(target, current * PRIOR_EFFORT_MULTIPLIER.get(scope, 1.50))
    if "reserve" in str(task.get("name") or "").lower() and current == 0:
        target = 0.0
    keyword_floor = keyword_fte_floor(task)
    major_floor = MAJOR_TASK_FTE_FLOORS.get(str(task.get("id")), 0.0)
    target = max(target, keyword_floor)
    target = max(target, major_floor)
    if scope == "demonstrator_engineering" and major_floor <= 0.0:
        # Most demonstrator detail packages are produced through bounded specialist
        # subcontracts. Limit the permanent owner-team demand while preserving the
        # task's external engineering and verification cost.
        target = min(target, max(0.25, current * 1.20, keyword_floor))
    return round(target, 3)


def route_target_fte(task: dict[str, Any]) -> float:
    # Licensing-route task totals include substantial regulator, legal, specialist,
    # and application-support cost. Keep the accountable applicant team lean and
    # avoid converting those external costs into a front-loaded permanent staff peak.
    prior = float(task.get("resources", {}).get("fte_years") or 0.0)
    task_id = str(task.get("id") or "")
    if task_id.startswith("D-LP2-"):
        route_floor = ROUTE_FTE_FLOORS.get(task_id, 0.0) * 0.30
        return round(max(route_floor, prior * 1.20, 0.40), 3)
    route_floor = ROUTE_FTE_FLOORS.get(task_id, 0.0) * 0.35
    return round(max(route_floor, prior * 1.40, 0.50), 3)


def direct_demo_task(task: dict[str, Any]) -> bool:
    cost = task.get("cost") or {}
    return str(task.get("id") or "").startswith("D-DEMO-") or cost.get("category") == "Demonstrator Direct"


def modeled_direct_nonlabor(task: dict[str, Any]) -> tuple[float, str]:
    cost = task.get("cost") or {}
    existing = float(cost.get("non_labor_kusd") or 0.0)
    task_id = str(task.get("id"))
    if task_id == "P-PKG-08":
        return 2_500.0, (
            "Independent licensing assurance, application consistency review, and specialist advisory allowance. "
            "NRC review fees, route-specific hearing support, and application-stage regulatory response costs are carried in the selected licensing-path module and are not duplicated here."
        )
    if direct_demo_task(task):
        return existing, "Controlled direct-demonstrator package; the $30 million non-labor cap is retained without escalation."
    if "reserve" in str(task.get("name") or "").lower():
        return 0.0, "No separate reserve is retained because task-level uncertainty allowance is included in the revised estimate."
    if existing >= 10_000.0:
        value = existing * 1.06
        basis = "Existing supplier/EPC/capital allowance retained and updated by 6% for estimate maturity and 2026 execution conditions."
    elif existing >= 1_000.0:
        value = existing * 1.10
        basis = "Existing external-service, test, licensing, or equipment allowance retained and updated by 10%."
    elif existing >= 100.0:
        value = existing * 1.15
        basis = "Existing direct non-labor allowance retained and updated by 15% for scope definition and supplier uncertainty."
    else:
        package = task.get("engineering_work_package") or {}
        pattern = package.get("work_pattern")
        scope = task.get("task_scope")
        domain = package.get("primary_domain")
        complexity = (
            1.0
            + 0.025 * package_list_count(task, "execution_procedure")
            + 0.015 * package_list_count(task, "deliverable_register")
            + 0.010 * package_list_count(task, "toolchain")
        )
        value = (
            PATTERN_NONLABOR_BASE_KUSD.get(pattern, 30.0)
            * SCOPE_NONLABOR_FACTOR.get(scope, 1.0)
            * DOMAIN_NONLABOR_FACTOR.get(domain, 1.0)
            * keyword_multiplier(str(task.get("name") or ""))
            * complexity
        )
        value = max(existing * 1.15, value)
        basis = "Activity-based allowance for task-specific specialist services, software/compute, data, independent review, and field support."
    value = max(value, keyword_nonlabor_floor_kusd(task))
    value = max(value, MAJOR_TASK_DIRECT_NONLABOR_FLOORS_KUSD.get(task_id, 0.0))
    return round(value, 6), basis


def risk_allowance_percent(task: dict[str, Any]) -> float:
    if direct_demo_task(task) or "reserve" in str(task.get("name") or "").lower():
        return 0.0
    scope = task.get("task_scope")
    if scope in {"methods_and_topicals", "integral_test_facility", "critical_experiment", "demonstrator_experiments"}:
        return 0.20
    if scope in {"demonstrator_engineering", "power_reactor_engineering"}:
        return 0.15
    if scope == "power_reactor_construction":
        return 0.12
    if scope in {"power_reactor_licensing", "demonstrator_licensing"}:
        return 0.18
    if scope == "program_backbone":
        return 0.12
    return 0.15


def component_fractions(task: dict[str, Any], route_path: str | None = None) -> dict[str, float]:
    name = str(task.get("name") or "").lower()
    cost = task.get("cost") or {}
    category = str(cost.get("category") or "").lower()
    subcategory = str(cost.get("subcategory") or "").lower()
    package = task.get("engineering_work_package") or {}
    pattern = package.get("work_pattern")

    if direct_demo_task(task):
        if "contingency" in name:
            return {"other_direct_kusd": 0.0}
        if any(token in name for token in ["commission", "startup", "acceptance test"]):
            return {
                "facility_test_and_field_operations_kusd": 0.75,
                "travel_and_field_support_kusd": 0.10,
                "other_direct_kusd": 0.15,
            }
        if any(token in name for token in ["fuel salt", "inventory", "consumable", "spares"]):
            return {
                "equipment_materials_and_fabrication_kusd": 0.80,
                "facility_test_and_field_operations_kusd": 0.15,
                "other_direct_kusd": 0.05,
            }
        return {
            "equipment_materials_and_fabrication_kusd": 0.80,
            "facility_test_and_field_operations_kusd": 0.15,
            "other_direct_kusd": 0.05,
        }

    if str(task.get("id") or "") == "S-PKG-03":
        return {
            "regulatory_review_fees_kusd": 0.55,
            "external_engineering_and_lab_services_kusd": 0.25,
            "legal_hearing_and_advisory_kusd": 0.10,
            "travel_and_field_support_kusd": 0.05,
            "other_direct_kusd": 0.05,
        }

    if str(task.get("id") or "") == "P-PKG-08":
        return {
            "external_engineering_and_lab_services_kusd": 0.65,
            "legal_hearing_and_advisory_kusd": 0.20,
            "software_compute_and_data_kusd": 0.05,
            "travel_and_field_support_kusd": 0.05,
            "other_direct_kusd": 0.05,
        }

    if route_path == "doe_launchpad":
        return {
            "external_engineering_and_lab_services_kusd": 0.45,
            "legal_hearing_and_advisory_kusd": 0.20,
            "facility_test_and_field_operations_kusd": 0.20,
            "travel_and_field_support_kusd": 0.10,
            "software_compute_and_data_kusd": 0.05,
        }
    if route_path in {"part50", "part52", "part53", "part57"}:
        if any(token in name for token in ["review", "rai", "acrs", "hearing", "issuance", "docket", "rulemaking", "finding"]):
            return {
                "regulatory_review_fees_kusd": 0.45,
                "external_engineering_and_lab_services_kusd": 0.30,
                "legal_hearing_and_advisory_kusd": 0.15,
                "travel_and_field_support_kusd": 0.05,
                "software_compute_and_data_kusd": 0.05,
            }
        if any(token in name for token in ["site", "environmental", "permit", "esp"]):
            return {
                "external_engineering_and_lab_services_kusd": 0.45,
                "regulatory_review_fees_kusd": 0.20,
                "legal_hearing_and_advisory_kusd": 0.10,
                "travel_and_field_support_kusd": 0.10,
                "other_direct_kusd": 0.15,
            }
        return {
            "external_engineering_and_lab_services_kusd": 0.40,
            "regulatory_review_fees_kusd": 0.30,
            "legal_hearing_and_advisory_kusd": 0.10,
            "software_compute_and_data_kusd": 0.10,
            "travel_and_field_support_kusd": 0.05,
            "other_direct_kusd": 0.05,
        }

    if "facilities" in category or "construction" in category or "capital test facility" in category or "manufacturing" in category:
        return {
            "equipment_materials_and_fabrication_kusd": 0.72,
            "facility_test_and_field_operations_kusd": 0.20,
            "external_engineering_and_lab_services_kusd": 0.05,
            "travel_and_field_support_kusd": 0.03,
        }
    if "external engineering" in category:
        return {
            "external_engineering_and_lab_services_kusd": 0.75,
            "software_compute_and_data_kusd": 0.10,
            "travel_and_field_support_kusd": 0.05,
            "other_direct_kusd": 0.10,
        }
    if "materials/fuel/test" in category or "r&d / testing" in subcategory:
        return {
            "external_engineering_and_lab_services_kusd": 0.30,
            "equipment_materials_and_fabrication_kusd": 0.30,
            "facility_test_and_field_operations_kusd": 0.30,
            "software_compute_and_data_kusd": 0.05,
            "travel_and_field_support_kusd": 0.05,
        }
    if task.get("task_scope") in {"power_reactor_licensing", "demonstrator_licensing"}:
        return {
            "external_engineering_and_lab_services_kusd": 0.45,
            "legal_hearing_and_advisory_kusd": 0.20,
            "software_compute_and_data_kusd": 0.10,
            "travel_and_field_support_kusd": 0.10,
            "other_direct_kusd": 0.15,
        }
    if "commissioning" in category or pattern == "test_experiment":
        return {
            "external_engineering_and_lab_services_kusd": 0.25,
            "equipment_materials_and_fabrication_kusd": 0.20,
            "facility_test_and_field_operations_kusd": 0.40,
            "software_compute_and_data_kusd": 0.05,
            "travel_and_field_support_kusd": 0.08,
            "other_direct_kusd": 0.02,
        }
    if pattern == "analysis_model":
        return {
            "external_engineering_and_lab_services_kusd": 0.45,
            "software_compute_and_data_kusd": 0.40,
            "travel_and_field_support_kusd": 0.05,
            "other_direct_kusd": 0.10,
        }
    if pattern == "design_engineering":
        return {
            "external_engineering_and_lab_services_kusd": 0.55,
            "software_compute_and_data_kusd": 0.25,
            "travel_and_field_support_kusd": 0.08,
            "other_direct_kusd": 0.12,
        }
    if pattern == "licensing_product":
        return {
            "external_engineering_and_lab_services_kusd": 0.50,
            "legal_hearing_and_advisory_kusd": 0.20,
            "software_compute_and_data_kusd": 0.10,
            "travel_and_field_support_kusd": 0.08,
            "other_direct_kusd": 0.12,
        }
    return {
        "external_engineering_and_lab_services_kusd": 0.45,
        "software_compute_and_data_kusd": 0.20,
        "travel_and_field_support_kusd": 0.10,
        "other_direct_kusd": 0.25,
    }


def split_direct_nonlabor(task: dict[str, Any], direct_nonlabor: float, route_path: str | None = None) -> dict[str, float]:
    components = {key: 0.0 for key in COMPONENT_KEYS}
    name = str(task.get("name") or "").lower()
    if direct_demo_task(task) and "contingency" in name:
        # The existing direct contingency is explicitly represented as a risk
        # component rather than hardware or services.
        return components
    fractions = component_fractions(task, route_path)
    total_fraction = sum(fractions.values()) or 1.0
    for key, fraction in fractions.items():
        if key in components:
            components[key] = round(direct_nonlabor * fraction / total_fraction, 6)
    # Correct rounding to exactly match the direct amount without creating a
    # negative residual line when the rounded components exceed the source by
    # a few millionths of a thousand dollars.
    delta = round(direct_nonlabor - sum(components.values()), 6)
    target_key = "other_direct_kusd" if delta >= 0 else max(components, key=components.get)
    components[target_key] = round(max(0.0, components[target_key] + delta), 6)
    final_delta = round(direct_nonlabor - sum(components.values()), 6)
    if final_delta:
        target_key = max(components, key=components.get)
        components[target_key] = round(components[target_key] + final_delta, 6)
    return components


def estimate_class(task: dict[str, Any], route_path: str | None = None) -> tuple[str, float, float, str]:
    task_id = str(task.get("id") or "")
    scope = task.get("task_scope")
    if direct_demo_task(task):
        return "Controlled direct-package allowance", 0.10, 0.25, "The $30 million direct non-labor package is a management target with supplier quotations still required."
    if route_path == "part57" and task_id.startswith("P57-H"):
        return "Concept sensitivity estimate", 0.30, 0.60, "Future-rule content and review process are not sufficiently mature for a control estimate."
    if route_path or scope in {"power_reactor_licensing", "demonstrator_licensing"}:
        return "Licensing planning estimate", 0.20, 0.45, "Applicant effort, review hours, hearing activity, and issue complexity vary materially by regulator feedback."
    if scope in {"methods_and_topicals", "integral_test_facility", "critical_experiment", "demonstrator_experiments"}:
        return "R&D planning estimate", 0.25, 0.50, "Test scope, host terms, fabrication quotations, and validation outcomes remain material uncertainties."
    if scope == "power_reactor_construction" or float(task.get("cost", {}).get("non_labor_kusd") or 0.0) >= 10_000:
        return "Preliminary capital estimate", 0.20, 0.40, "Major supplier and construction allowances require design maturity, procurement strategy, and quotations."
    return "Engineering planning estimate", 0.20, 0.40, "The activity is defined sufficiently for budget planning but not for a fixed-price commitment."


def find_role_id(text: str, role_by_id: dict[str, dict[str, Any]]) -> str | None:
    normalized = re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
    if not normalized:
        return None
    aliases = {
        "reactor physics": "RPX",
        "thermal hydraulics": "TH",
        "safety analysis": "SA",
        "systems engineer": "SE",
        "mechanical engineer": "ME",
        "electrical engineer": "EE",
        "civil structural": "CS",
        "instrumentation controls": "IC",
        "i c digital": "IC",
        "materials": "MAT",
        "chemistry": "RAD",
        "radiation protection": "RAD",
        "operations": "OPS",
        "test commissioning": "TEST",
        "quality assurance": "QA",
        "licensing": "LIC",
        "project controls": "PC",
        "project manager": "PM",
        "procurement": "PROC",
        "construction manager": "CM",
        "environmental": "ENV",
        "human factors": "HFE",
        "pra": "PRA",
        "risk": "PRA",
        "data software": "DATA",
        "cyber": "CYB",
        "security engineer": "CYB",
        "chief engineer": "CE",
        "regulatory counsel": "LAW",
        "document control": "DC",
        "cost estimator": "COST",
    }
    for key, value in aliases.items():
        if key in normalized:
            return value
    for role_id, row in role_by_id.items():
        role_text = re.sub(r"[^a-z0-9]+", " ", str(row.get("role") or "").lower()).strip()
        if normalized in role_text or role_text in normalized:
            return role_id
    return None


def ensure_assignments(
    task: dict[str, Any],
    rows: list[dict[str, Any]],
    role_by_id: dict[str, dict[str, Any]],
    next_assignment_id: list[int],
    *,
    route_specific: bool,
) -> list[dict[str, Any]]:
    if rows:
        return rows
    target_roles: list[str] = []
    package = task.get("engineering_work_package") or {}
    plan = package.get("resource_plan") or {}
    for role_name in plan.get("core_producing_team") or []:
        role_id = find_role_id(str(role_name), role_by_id)
        if role_id and role_id not in target_roles:
            target_roles.append(role_id)
    responsible = find_role_id(str(task.get("responsible_role") or plan.get("responsible_role") or ""), role_by_id)
    if responsible and responsible not in target_roles:
        target_roles.insert(0, responsible)
    if not target_roles:
        target_roles = ["SE"]
    target_roles = target_roles[:4]
    created: list[dict[str, Any]] = []
    for role_id in target_roles:
        role = role_by_id[role_id]
        assignment_id = f"A-{next_assignment_id[0]:05d}" if not route_specific else f"{task['id']}-{role_id}"
        next_assignment_id[0] += 1
        created.append(
            {
                "assignment_id": assignment_id,
                "task_id": task["id"],
                "concept": task.get("concept"),
                "task_name": task.get("name"),
                "role_id": role_id,
                "role": role["role"],
                "start": task["schedule"]["start"],
                "finish": task["schedule"]["finish"],
                "avg_fte": 0.0,
                "loaded_rate_kusd_per_fte_year": ROLE_RATES_KUSD_PER_FTE_YEAR[role_id],
                "fte_years": 0.0,
                "labor_cost_kusd": 0.0,
                "execution_stream": task.get("execution_stream"),
                "work_type": role.get("work_type"),
                "loading_basis": "v4.2 activity-based cost estimate; producing team derived from the engineering work package.",
                "route_specific": route_specific,
            }
        )
    return created


def scale_assignment_rows(
    task: dict[str, Any],
    rows: list[dict[str, Any]],
    target_fte: float,
    portfolio_weights: dict[str, float],
) -> tuple[list[dict[str, Any]], float]:
    prior_total = sum(float(row.get("fte_years") or 0.0) for row in rows)
    if target_fte <= 0.0:
        shares = [0.0 for _ in rows]
    elif prior_total > 0.0:
        shares = [float(row.get("fte_years") or 0.0) / prior_total for row in rows]
    elif rows:
        # Weight the responsible/first producing role more heavily and retain a
        # meaningful independent/support contribution.
        raw = [0.55] + ([0.30] if len(rows) >= 2 else []) + ([0.15] if len(rows) >= 3 else [])
        while len(raw) < len(rows):
            raw.append(0.08)
        total = sum(raw[: len(rows)])
        shares = [value / total for value in raw[: len(rows)]]
    else:
        shares = []

    fractions = annual_fractions(
        task["schedule"]["start"],
        task["schedule"]["finish"],
        task_year_weights(task, portfolio_weights),
    )
    labor_total = 0.0
    for index, row in enumerate(rows):
        role_id = str(row.get("role_id"))
        rate = ROLE_RATES_KUSD_PER_FTE_YEAR.get(role_id, float(row.get("loaded_rate_kusd_per_fte_year") or 235.0))
        fte_years = target_fte * shares[index] if index < len(shares) else 0.0
        labor = fte_years * rate
        row["start"] = task["schedule"]["start"]
        row["finish"] = task["schedule"]["finish"]
        row["loaded_rate_kusd_per_fte_year"] = round(rate, 3)
        row["fte_years"] = round(fte_years, 6)
        row["avg_fte"] = round(fte_years / duration_years(row["start"], row["finish"]), 6)
        row["labor_cost_kusd"] = round(labor, 6)
        row["annual_fte_years"] = {year: round(fte_years * fraction, 6) for year, fraction in fractions.items()}
        row["annual_labor_kusd"] = {year: round(labor * fraction, 6) for year, fraction in fractions.items()}
        row["cost_reestimate_v4_2"] = {
            "prior_fte_years": round(prior_total * shares[index], 6) if prior_total > 0 else 0.0,
            "revised_fte_years": round(fte_years, 6),
            "loaded_rate_kusd_per_fte_year": round(rate, 3),
            "basis": "Activity-based effort allocated across the existing producing/review team in proportion to the prior assignment mix.",
        }
        labor_total += labor
    return rows, round(labor_total, 6)


def labor_effort_breakdown(task: dict[str, Any], planned_hours: float) -> dict[str, float]:
    pattern = (task.get("engineering_work_package") or {}).get("work_pattern")
    shares_by_pattern = {
        "design_engineering": (0.62, 0.16, 0.12, 0.06, 0.04),
        "analysis_model": (0.58, 0.20, 0.12, 0.06, 0.04),
        "test_experiment": (0.52, 0.15, 0.15, 0.10, 0.08),
        "licensing_product": (0.50, 0.18, 0.16, 0.10, 0.06),
        "operations_program": (0.55, 0.14, 0.14, 0.10, 0.07),
        "procurement_fabrication": (0.50, 0.15, 0.18, 0.10, 0.07),
        "construction_installation": (0.48, 0.14, 0.18, 0.12, 0.08),
        "management_control": (0.40, 0.12, 0.24, 0.14, 0.10),
    }
    production, verification, integration, records_qa, controls = shares_by_pattern.get(pattern, (0.55, 0.16, 0.15, 0.08, 0.06))
    labels = [
        ("engineering_production_hours", production),
        ("independent_verification_and_review_hours", verification),
        ("interface_integration_and_comment_resolution_hours", integration),
        ("quality_records_and_configuration_hours", records_qa),
        ("task_management_and_cost_schedule_control_hours", controls),
    ]
    result = {name: round(planned_hours * share, 1) for name, share in labels}
    delta = round(planned_hours - sum(result.values()), 1)
    result["engineering_production_hours"] = round(result["engineering_production_hours"] + delta, 1)
    return result


def estimate_costs(
    task: dict[str, Any],
    target_fte: float,
    labor_kusd: float,
    *,
    route_path: str | None,
) -> dict[str, Any]:
    prior = task.get("cost") or {}
    prior_total = float(prior.get("total_kusd") or 0.0)
    prior_labor = float(prior.get("labor_kusd") or 0.0)
    prior_nonlabor = float(prior.get("non_labor_kusd") or 0.0)
    direct_nonlabor, direct_basis = modeled_direct_nonlabor(task)
    components = split_direct_nonlabor(task, direct_nonlabor, route_path)
    risk_pct = risk_allowance_percent(task)
    if direct_demo_task(task) and "contingency" in str(task.get("name") or "").lower():
        risk_allowance = direct_nonlabor
        components = {key: 0.0 for key in COMPONENT_KEYS}
        direct_nonlabor_excluding_risk = 0.0
    else:
        direct_nonlabor_excluding_risk = sum(components.values())
        risk_allowance = (labor_kusd + direct_nonlabor_excluding_risk) * risk_pct
    nonlabor_total = direct_nonlabor_excluding_risk + risk_allowance
    total = labor_kusd + nonlabor_total
    estimate_label, low_pct, high_pct, range_basis = estimate_class(task, route_path)
    low = total * (1.0 - low_pct)
    high = total * (1.0 + high_pct)
    blended_rate = labor_kusd / target_fte if target_fte > 0 else 0.0
    fee_component = float(components.get("regulatory_review_fees_kusd") or 0.0)
    assumed_rate = NRC_REDUCED_RATE_PER_HOUR if route_path in {"part50", "part52", "part53"} else NRC_FULL_RATE_PER_HOUR
    regulatory_hours = fee_component * 1_000.0 / assumed_rate if fee_component > 0 else 0.0

    cost = dict(prior)
    cost.update(
        {
            "labor_kusd": round(labor_kusd, 6),
            "non_labor_kusd": round(nonlabor_total, 6),
            "total_kusd": round(total, 6),
            "direct_cost_before_risk_kusd": round(labor_kusd + direct_nonlabor_excluding_risk, 6),
            "direct_non_labor_before_risk_kusd": round(direct_nonlabor_excluding_risk, 6),
            "risk_allowance_pct": round(risk_pct, 4),
            "risk_allowance_kusd": round(risk_allowance, 6),
            "low_kusd": round(low, 6),
            "high_kusd": round(high, 6),
            "estimate_class": estimate_label,
            "estimate_currency_year": 2026,
            "estimate_method": "Bottom-up activity-based estimate by work package",
            "productive_hours_per_fte_year": PRODUCTIVE_HOURS_PER_FTE_YEAR,
            "planned_fte_years": round(target_fte, 6),
            "planned_labor_hours": round(target_fte * PRODUCTIVE_HOURS_PER_FTE_YEAR, 1),
            "labor_effort_breakdown": labor_effort_breakdown(task, target_fte * PRODUCTIVE_HOURS_PER_FTE_YEAR),
            "blended_loaded_rate_kusd_per_fte_year": round(blended_rate, 3),
            "basis_of_estimate_id": f"BOE-{task.get('id')}-4.2",
            "estimate_status": "Planning baseline - quotation and design-maturity updates required",
            "reestimate_triggers": [
                "Approved change to scope, deliverables, acceptance criteria, schedule, or licensing pathway.",
                "Supplier, laboratory, host, EPC, or regulator estimate differing by more than 10 percent from the current allowance.",
                "Design-review or test result that changes model qualification, equipment count, material quantity, or required rework.",
                "Annual escalation update or change in the constant-dollar currency basis."
            ],
            "estimate_basis": (
                "2026 constant-dollar bottom-up planning estimate. Labor is derived from the engineering work package's controlled inputs, "
                "execution steps, deliverables, requirements, tools, hold points, technical domain, schedule criticality, and concept scope. "
                "Task-specific non-labor covers specialist services, software/compute, data, independent review, laboratory/field support, "
                "equipment or materials where not already included in a parent package, regulatory review fees where applicable, and an explicit risk allowance."
            ),
            "direct_non_labor_basis": direct_basis,
            "uncertainty_range_basis": range_basis,
            "regulatory_review_rate_basis_usd_per_hour": round(assumed_rate, 2) if regulatory_hours > 0 else 0.0,
            "regulatory_review_staff_hours_assumed": round(regulatory_hours, 1),
            "cost_components": {
                **{key: round(float(value), 6) for key, value in components.items()},
                "risk_allowance_kusd": round(risk_allowance, 6),
            },
            "prior_estimate": {
                "version": "4.1.0",
                "labor_kusd": round(prior_labor, 6),
                "non_labor_kusd": round(prior_nonlabor, 6),
                "total_kusd": round(prior_total, 6),
                "fte_years": round(float(task.get("resources", {}).get("fte_years") or 0.0), 6),
            },
            "estimate_change": {
                "labor_delta_kusd": round(labor_kusd - prior_labor, 6),
                "non_labor_delta_kusd": round(nonlabor_total - prior_nonlabor, 6),
                "total_delta_kusd": round(total - prior_total, 6),
                "total_change_pct": round(((total / prior_total) - 1.0) * 100.0, 2) if prior_total > 0 else None,
                "reason": "Replaced highly compressed fractional-FTE placeholders with activity-based production, review, external-service, tool, fee, and uncertainty estimates.",
            },
            "cost_drivers": [
                f"Work pattern: {(task.get('engineering_work_package') or {}).get('work_pattern') or 'not classified'}",
                f"Primary engineering domain: {(task.get('engineering_work_package') or {}).get('primary_domain') or 'not classified'}",
                f"Controlled inputs: {package_list_count(task, 'controlled_inputs')}",
                f"Execution steps: {package_list_count(task, 'execution_procedure')}",
                f"Controlled deliverables: {package_list_count(task, 'deliverable_register')}",
                f"Requirements/guidance records: {package_list_count(task, 'requirements_and_guidance')}",
                f"Required tools/methods: {package_list_count(task, 'toolchain')}",
                f"Review/hold points: {package_list_count(task, 'required_reviews_and_hold_points')}",
                "Critical-path or major integrated-product floor applied." if str(task.get("id")) in MAJOR_TASK_FTE_FLOORS or str(task.get("id")) in ROUTE_FTE_FLOORS else "No task-specific minimum above the activity-based result was required.",
            ],
            "exclusions_and_double_counting_controls": [
                "Major reactor hardware, bulk construction, and supplier fabrication are charged only to the designated procurement/construction or direct-demonstrator package tasks.",
                "Routine corporate overhead is included in loaded labor rates and is not added again as a task-specific non-labor line.",
                "The $30 million demonstrator direct non-labor package remains a separate controlled cap; owner engineering and authorization costs are outside that cap.",
                "Financing, escalation beyond constant 2026 dollars, taxes, insurance, and owner contingency above the stated task risk allowance are excluded unless explicitly identified in a capital package.",
            ],
        }
    )
    return cost


def refresh_task_profiles(task: dict[str, Any], rows: list[dict[str, Any]], portfolio_weights: dict[str, float]) -> None:
    resources = task.setdefault("resources", {})
    fte = sum(float(row.get("fte_years") or 0.0) for row in rows)
    resources["fte_years"] = round(fte, 6)
    resources["avg_fte"] = round(fte / duration_years(task["schedule"]["start"], task["schedule"]["finish"]), 6) if fte else 0.0
    resources["assignment_ids"] = [str(row.get("assignment_id")) for row in rows]
    annual_fte: dict[str, float] = defaultdict(float)
    for row in rows:
        for year, value in (row.get("annual_fte_years") or {}).items():
            annual_fte[year] += float(value)
    resources["annual_fte_years"] = {year: round(value, 6) for year, value in sorted(annual_fte.items())}

    fractions = annual_fractions(
        task["schedule"]["start"],
        task["schedule"]["finish"],
        task_year_weights(task, portfolio_weights),
    )
    cost = task["cost"]
    labor = float(cost.get("labor_kusd") or 0.0)
    nonlabor = float(cost.get("non_labor_kusd") or 0.0)
    total = float(cost.get("total_kusd") or 0.0)
    cost["annual_labor_kusd"] = {year: round(labor * fraction, 6) for year, fraction in fractions.items()}
    cost["annual_non_labor_kusd"] = {year: round(nonlabor * fraction, 6) for year, fraction in fractions.items()}
    cost["annual_kusd"] = {year: round(total * fraction, 6) for year, fraction in fractions.items()}

    package = task.get("engineering_work_package") or {}
    plan = package.get("resource_plan") or {}
    plan["planned_fte_years"] = resources["fte_years"]
    plan["planned_average_fte"] = resources["avg_fte"]
    plan["costed_labor_hours"] = round(resources["fte_years"] * PRODUCTIVE_HOURS_PER_FTE_YEAR, 1)
    plan["cost_estimate_version"] = VERSION
    plan["staffing_strategy"] = (
        "Budget the producing and independent-review effort required to release the defined engineering product. Use specialist suppliers and laboratories for bounded work packages, "
        "but retain owner capability for requirements, integration, acceptance, configuration control, safety basis, and regulatory commitments."
    )
    package["resource_plan"] = plan
    estimate_basis = package.get("estimating_and_schedule_basis") or {}
    estimate_basis["cost_estimate_version"] = VERSION
    estimate_basis["cost_method"] = "Bottom-up activity-based work-package estimate"
    estimate_basis["planned_fte_years"] = resources["fte_years"]
    estimate_basis["planned_labor_hours"] = round(resources["fte_years"] * PRODUCTIVE_HOURS_PER_FTE_YEAR, 1)
    estimate_basis["blended_loaded_rate_kusd_per_fte_year"] = task["cost"].get("blended_loaded_rate_kusd_per_fte_year")
    estimate_basis["direct_non_labor_before_risk_kusd"] = task["cost"].get("direct_non_labor_before_risk_kusd")
    estimate_basis["risk_allowance_kusd"] = task["cost"].get("risk_allowance_kusd")
    estimate_basis["estimate_range_kusd"] = [task["cost"].get("low_kusd"), task["cost"].get("high_kusd")]
    estimate_basis["basis_note"] = task["cost"].get("estimate_basis")
    package["estimating_and_schedule_basis"] = estimate_basis
    task["engineering_work_package"] = package


def recost_task(
    task: dict[str, Any],
    rows: list[dict[str, Any]],
    role_by_id: dict[str, dict[str, Any]],
    next_assignment_id: list[int],
    portfolio_weights: dict[str, float],
    *,
    route_path: str | None,
    route_specific: bool,
) -> list[dict[str, Any]]:
    prior_fte = float(task.get("resources", {}).get("fte_years") or 0.0)
    rows = ensure_assignments(task, rows, role_by_id, next_assignment_id, route_specific=route_specific)
    target = route_target_fte(task) if route_specific else base_target_fte(task)
    rows, labor = scale_assignment_rows(task, rows, target, portfolio_weights)
    task["cost"] = estimate_costs(task, target, labor, route_path=route_path)
    refresh_task_profiles(task, rows, portfolio_weights)
    task["resources"]["cost_reestimate_v4_2"] = {
        "prior_fte_years": round(prior_fte, 6),
        "revised_fte_years": round(target, 6),
        "delta_fte_years": round(target - prior_fte, 6),
        "method": "Activity-based task estimate with task-specific floor only for major integrated products.",
    }
    return rows


def allocate_package_cost_views(db: dict[str, Any]) -> None:
    """Create non-additive fully burdened task views without changing program totals.

    The prior model used broad external-contract packages. Engineers reviewing a detailed
    task therefore saw only owner labor. This allocation traces a controlled portion of
    those package costs to the detailed activities that consume the contract, while the
    accounting total remains on the source package task to prevent double counting.
    """
    tasks = db["tasks"]
    by_id = {str(task.get("id")): task for task in tasks}
    for task in tasks:
        cost = task.get("cost") or {}
        cost["allocated_program_package_kusd"] = 0.0
        cost["allocated_program_package_sources"] = []
        cost["fully_burdened_task_view_kusd"] = round(float(cost.get("total_kusd") or 0.0), 6)
        cost["fully_burdened_view_is_non_additive"] = True

    allocations = [
        {
            "source_task_id": "P-PKG-01",
            "allocation_fraction": 0.75,
            "eligible": lambda task: task.get("concept") == "Power Reactor"
            and task.get("task_scope") == "power_reactor_engineering"
            and not str(task.get("id") or "").startswith("P-PKG-")
            and "reserve" not in str(task.get("name") or "").lower(),
            "basis": "Allocated share of the EPC/vendor detailed-engineering contract, weighted by planned labor hours and engineering-domain complexity.",
        },
        {
            "source_task_id": "S-PKG-01",
            "allocation_fraction": 0.70,
            "eligible": lambda task: task.get("task_scope") == "methods_and_topicals"
            and not str(task.get("id") or "").startswith("S-PKG-")
            and "reserve" not in str(task.get("name") or "").lower(),
            "basis": "Allocated share of methods V&V data and independent-review contracts, weighted by each method task's planned labor hours.",
        },
        {
            "source_task_id": "S-PKG-05",
            "allocation_fraction": 0.70,
            "eligible": lambda task: task.get("task_scope") == "methods_and_topicals"
            and not str(task.get("id") or "").startswith("S-PKG-")
            and "reserve" not in str(task.get("name") or "").lower(),
            "basis": "Allocated share of external laboratory and vendor-validation packages, weighted by each method task's planned labor hours and test intensity.",
        },
    ]
    domain_weight = {
        "neutronics": 1.25,
        "thermal_hydraulics": 1.25,
        "materials": 1.20,
        "chemistry": 1.20,
        "safety_analysis": 1.20,
        "instrumentation_controls": 1.10,
        "risk_pra": 1.15,
        "civil_structural": 1.10,
        "electrical": 1.05,
    }
    for config in allocations:
        source = by_id.get(config["source_task_id"])
        if not source:
            continue
        source_cost = source.get("cost") or {}
        pool = float(source_cost.get("total_kusd") or 0.0) * float(config["allocation_fraction"])
        eligible = [task for task in tasks if config["eligible"](task)]
        weighted: list[tuple[dict[str, Any], float]] = []
        for task in eligible:
            package = task.get("engineering_work_package") or {}
            hours = float(task.get("cost", {}).get("planned_labor_hours") or 0.0)
            pattern = package.get("work_pattern")
            intensity = 1.20 if pattern in {"analysis_model", "test_experiment"} else 1.0
            weight = max(hours, 80.0) * domain_weight.get(package.get("primary_domain"), 1.0) * intensity
            weighted.append((task, weight))
        denominator = sum(weight for _, weight in weighted)
        if denominator <= 0:
            continue
        allocated_total = 0.0
        for index, (task, weight) in enumerate(weighted):
            if index == len(weighted) - 1:
                share = round(pool - allocated_total, 6)
            else:
                share = round(pool * weight / denominator, 6)
                allocated_total += share
            cost = task["cost"]
            cost["allocated_program_package_kusd"] = round(float(cost.get("allocated_program_package_kusd") or 0.0) + share, 6)
            cost["allocated_program_package_sources"].append(
                {
                    "source_task_id": config["source_task_id"],
                    "allocated_kusd": share,
                    "basis": config["basis"],
                }
            )
            cost["fully_burdened_task_view_kusd"] = round(float(cost.get("total_kusd") or 0.0) + float(cost.get("allocated_program_package_kusd") or 0.0), 6)
        source_cost["allocation_view"] = {
            "allocated_to_detailed_tasks_kusd": round(pool, 6),
            "unallocated_general_contract_kusd": round(float(source_cost.get("total_kusd") or 0.0) - pool, 6),
            "allocation_fraction": config["allocation_fraction"],
            "non_additive_display_allocation": True,
            "basis": config["basis"],
        }


def aggregate_financials(db: dict[str, Any]) -> None:
    tasks = db["tasks"]
    summary: dict[str, dict[str, float]] = defaultdict(lambda: {"labor_kusd": 0.0, "non_labor_kusd": 0.0, "total_kusd": 0.0, "fte_years": 0.0, "activities": 0.0})
    annual: dict[str, dict[str, float]] = defaultdict(lambda: {"labor_kusd": 0.0, "non_labor_kusd": 0.0, "total_kusd": 0.0})
    streams: dict[tuple[str, str], dict[str, float]] = defaultdict(lambda: {"labor_kusd": 0.0, "non_labor_kusd": 0.0, "total_kusd": 0.0, "fte_years": 0.0, "activities": 0.0})
    for task in tasks:
        concept = str(task.get("concept") or "Unassigned")
        cost = task.get("cost") or {}
        resources = task.get("resources") or {}
        row = summary[concept]
        row["activities"] += 1
        row["labor_kusd"] += float(cost.get("labor_kusd") or 0.0)
        row["non_labor_kusd"] += float(cost.get("non_labor_kusd") or 0.0)
        row["total_kusd"] += float(cost.get("total_kusd") or 0.0)
        row["fte_years"] += float(resources.get("fte_years") or 0.0)
        stream_key = (str(task.get("stream_id") or ""), str(task.get("execution_stream") or ""))
        stream = streams[stream_key]
        stream["activities"] += 1
        stream["labor_kusd"] += float(cost.get("labor_kusd") or 0.0)
        stream["non_labor_kusd"] += float(cost.get("non_labor_kusd") or 0.0)
        stream["total_kusd"] += float(cost.get("total_kusd") or 0.0)
        stream["fte_years"] += float(resources.get("fte_years") or 0.0)
        for year, value in (cost.get("annual_labor_kusd") or {}).items():
            annual[year]["labor_kusd"] += float(value)
        for year, value in (cost.get("annual_non_labor_kusd") or {}).items():
            annual[year]["non_labor_kusd"] += float(value)
        for year, value in (cost.get("annual_kusd") or {}).items():
            annual[year]["total_kusd"] += float(value)

    financials = db.setdefault("financials", {})
    financials["base_cost_summary"] = [
        {
            "Concept": concept,
            "Activities": int(values["activities"]),
            "FTE-years": round(values["fte_years"], 3),
            "Labor Cost ($000)": round(values["labor_kusd"], 3),
            "Non-Labor Cost ($000)": round(values["non_labor_kusd"], 3),
            "Total Cost ($000)": round(values["total_kusd"], 3),
        }
        for concept, values in sorted(summary.items())
    ]
    financials["base_cost_by_stream"] = [
        {
            "Stream ID": stream_id,
            "Execution Stream": execution_stream,
            "Activities": int(values["activities"]),
            "FTE-years": round(values["fte_years"], 3),
            "Labor Cost ($000)": round(values["labor_kusd"], 3),
            "Non-Labor Cost ($000)": round(values["non_labor_kusd"], 3),
            "Total Cost ($000)": round(values["total_kusd"], 3),
        }
        for (stream_id, execution_stream), values in sorted(streams.items())
    ]
    financials["base_annual_cash_flow"] = [
        {
            "Year": int(year),
            "Labor Cost ($000)": round(values["labor_kusd"], 3),
            "Non-Labor Cost ($000)": round(values["non_labor_kusd"], 3),
            "Total Cost ($000)": round(values["total_kusd"], 3),
        }
        for year, values in sorted(annual.items())
    ]
    financials["task_cost_reestimate_v4_2"] = {
        "costed_activity_count": len(tasks),
        "currency_year": 2026,
        "estimate_method": "Bottom-up activity-based estimate for every shared and route-specific work package",
        "productive_hours_per_fte_year": PRODUCTIVE_HOURS_PER_FTE_YEAR,
        "labor_rates": ROLE_RATES_KUSD_PER_FTE_YEAR,
        "risk_allowance_policy": {
            "program_backbone": 0.12,
            "engineering": 0.15,
            "licensing": 0.18,
            "methods_and_experiments": 0.20,
            "construction": 0.12,
            "direct_demonstrator_package": 0.0,
        },
        "direct_demonstrator_non_labor_cap_kusd": 30_000.0,
        "review_fee_reference": {
            "advanced_reactor_reduced_rate_usd_per_hour": NRC_REDUCED_RATE_PER_HOUR,
            "full_rate_usd_per_hour": NRC_FULL_RATE_PER_HOUR,
            "note": "The actual rate and eligible scope must be confirmed for the applicable fiscal year and licensing project plan.",
        },
        "basis_sources": [
            {
                "source": "U.S. Bureau of Labor Statistics - Nuclear Engineers",
                "url": "https://www.bls.gov/ooh/architecture-and-engineering/nuclear-engineers.htm",
                "use": "Salary reasonableness check before applying benefits, indirects, facilities, and contractor burden.",
            },
            {
                "source": "U.S. Bureau of Labor Statistics - Architectural and Engineering Managers",
                "url": "https://www.bls.gov/ooh/management/architectural-and-engineering-managers.htm",
                "use": "Management and technical-authority salary reasonableness check.",
            },
            {
                "source": "NRC 10 CFR 170.20 and Advanced Reactor Fees",
                "url": "https://www.nrc.gov/reading-rm/doc-collections/cfr/part170/part170-0020.html",
                "use": "Regulatory review fee-rate basis for advanced-reactor planning.",
            },
            {
                "source": "GAO Cost Estimating and Assessment Guide, GAO-20-195G",
                "url": "https://www.gao.gov/products/gao-20-195g",
                "use": "Bottom-up WBS, documented assumptions, uncertainty, and estimate reconciliation practices.",
            },
        ],
    }


def update_role_totals(db: dict[str, Any]) -> None:
    by_role: dict[str, dict[str, float]] = defaultdict(lambda: {"fte": 0.0, "labor": 0.0})
    for row in db["resources"]["assignments"]:
        role_id = str(row.get("role_id"))
        by_role[role_id]["fte"] += float(row.get("fte_years") or 0.0)
        by_role[role_id]["labor"] += float(row.get("labor_cost_kusd") or 0.0)
    for role in db["resources"]["roles"]:
        role_id = role["role_id"]
        role["loaded_rate_kusd_per_fte_year"] = ROLE_RATES_KUSD_PER_FTE_YEAR.get(role_id, role.get("loaded_rate_kusd_per_fte_year"))
        role["base_total_fte_years"] = round(by_role[role_id]["fte"], 6)
        role["base_labor_cost_kusd"] = round(by_role[role_id]["labor"], 6)


def build_audit_rows(db: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    all_tasks: list[tuple[dict[str, Any], str]] = [(task, "shared_program") for task in db["tasks"]]
    for path, modules in db["pathway_modules"].items():
        for module_tasks in modules.values():
            all_tasks.extend((task, path) for task in module_tasks)
    for task, route in all_tasks:
        cost = task.get("cost") or {}
        prior = cost.get("prior_estimate") or {}
        change = cost.get("estimate_change") or {}
        components = cost.get("cost_components") or {}
        rows.append(
            {
                "Task ID": task.get("id"),
                "Task": task.get("name"),
                "Concept": task.get("concept"),
                "Route": route,
                "Task Scope": task.get("task_scope"),
                "Engineering Domain": (task.get("engineering_work_package") or {}).get("primary_domain"),
                "Work Pattern": (task.get("engineering_work_package") or {}).get("work_pattern"),
                "Start": task.get("schedule", {}).get("start"),
                "Finish": task.get("schedule", {}).get("finish"),
                "Prior FTE-years": prior.get("fte_years", 0.0),
                "Revised FTE-years": cost.get("planned_fte_years", 0.0),
                "Planned Labor Hours": cost.get("planned_labor_hours", 0.0),
                "Blended Loaded Rate ($000/FTE-year)": cost.get("blended_loaded_rate_kusd_per_fte_year", 0.0),
                "Prior Labor Cost ($000)": prior.get("labor_kusd", 0.0),
                "Revised Labor Cost ($000)": cost.get("labor_kusd", 0.0),
                "External Engineering & Lab ($000)": components.get("external_engineering_and_lab_services_kusd", 0.0),
                "Software, Compute & Data ($000)": components.get("software_compute_and_data_kusd", 0.0),
                "Equipment, Materials & Fabrication ($000)": components.get("equipment_materials_and_fabrication_kusd", 0.0),
                "Facility, Test & Field Operations ($000)": components.get("facility_test_and_field_operations_kusd", 0.0),
                "Regulatory Review Fees ($000)": components.get("regulatory_review_fees_kusd", 0.0),
                "Legal, Hearing & Advisory ($000)": components.get("legal_hearing_and_advisory_kusd", 0.0),
                "Travel & Field Support ($000)": components.get("travel_and_field_support_kusd", 0.0),
                "Other Direct ($000)": components.get("other_direct_kusd", 0.0),
                "Risk Allowance ($000)": components.get("risk_allowance_kusd", 0.0),
                "Prior Total Cost ($000)": prior.get("total_kusd", 0.0),
                "Revised Total Cost ($000)": cost.get("total_kusd", 0.0),
                "Allocated Program Package Share ($000)": cost.get("allocated_program_package_kusd", 0.0),
                "Fully Burdened Task View ($000)": cost.get("fully_burdened_task_view_kusd", cost.get("total_kusd", 0.0)),
                "Low Estimate ($000)": cost.get("low_kusd", 0.0),
                "High Estimate ($000)": cost.get("high_kusd", 0.0),
                "Total Delta ($000)": change.get("total_delta_kusd", 0.0),
                "Total Change (%)": change.get("total_change_pct"),
                "Estimate Class": cost.get("estimate_class"),
                "Estimate Method": cost.get("estimate_method"),
            }
        )
    return sorted(rows, key=lambda row: (str(row["Route"]), str(row["Task ID"])))


def update_route_cost_model(db: dict[str, Any]) -> None:
    rows: list[dict[str, Any]] = []
    for path, modules in db["pathway_modules"].items():
        tasks = [task for task_list in modules.values() for task in task_list]
        rows.append(
            {
                "path": path,
                "task_count": len(tasks),
                "labor_kusd": round(sum(float(task.get("cost", {}).get("labor_kusd") or 0.0) for task in tasks), 3),
                "non_labor_kusd": round(sum(float(task.get("cost", {}).get("non_labor_kusd") or 0.0) for task in tasks), 3),
                "total_kusd": round(sum(float(task.get("cost", {}).get("total_kusd") or 0.0) for task in tasks), 3),
                "fte_years": round(sum(float(task.get("resources", {}).get("fte_years") or 0.0) for task in tasks), 3),
            }
        )
    model = db.setdefault("route_cost_model", {})
    model.update(
        {
            "units": "$000, constant 2026 dollars",
            "basis": "Task-by-task bottom-up applicant activity estimates with separate labor, external services, tools/data, equipment/field, regulator fees, legal support, and risk allowance.",
            "not_a_quote": "Planning estimate only; regulator, DOE/host, national laboratory, supplier, EPC, and test-facility quotations are not represented as commitments.",
            "rows": rows,
            "common_program_cost_kusd": round(sum(float(task.get("cost", {}).get("total_kusd") or 0.0) for task in db["tasks"]), 3),
            "version": VERSION,
        }
    )


def update_metadata(db: dict[str, Any], route_task_count: int, audit_count: int) -> None:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    db["meta"].update(
        {
            "version": VERSION,
            "application_version": VERSION,
            "generated": now,
            "data_date": now[:10],
            "source_baseline": (
                "Q4 2026 integrated baseline with v4.2 task-by-task bottom-up cost re-estimation. The schedule remains: demonstrator built and authorized by December 2028, "
                "demonstrator operations in 2029, commercial construction beginning in 2030, and licensed commercial operation by December 2035."
            ),
            "engineering_work_package_schema": "4.2",
            "cost_estimate_version": VERSION,
            "currency": "USD, constant 2026 dollars",
            "cost_units": "$000",
        }
    )
    db["planning_profile"]["version"] = VERSION
    quality = db.setdefault("data_quality", {})
    quality.update(
        {
            "engineering_ready_task_count": len(db["tasks"]) + route_task_count,
            "costed_task_count": audit_count,
            "cost_reestimate_release": VERSION,
            "route_model_version": VERSION,
            "base_assignment_count": len(db["resources"]["assignments"]),
            "automated_test_count": 39,
            "application_tabs": 12,
            "cost_estimate_currency_year": 2026,
            "cost_estimate_method": "Bottom-up activity-based task estimate",
        }
    )


def update_schema() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    schema["title"] = f"Project-MSR Integrated Planner Database Schema v{VERSION}"
    schema["$id"] = f"https://project-msr.local/schema/project_msr_database-{VERSION}.json"
    schema["properties"]["meta"]["properties"]["version"]["const"] = VERSION
    schema["properties"]["meta"]["properties"]["application_version"]["const"] = VERSION
    schema["properties"]["meta"]["properties"]["engineering_work_package_schema"]["const"] = "4.2"
    schema["properties"]["planning_profile"]["properties"]["version"]["const"] = VERSION
    schema["$defs"]["task"]["properties"]["cost"] = {
        "type": "object",
        "required": [
            "labor_kusd", "direct_non_labor_before_risk_kusd", "risk_allowance_kusd",
            "non_labor_kusd", "total_kusd", "low_kusd", "high_kusd",
            "estimate_class", "estimate_currency_year", "estimate_method",
            "productive_hours_per_fte_year", "planned_fte_years", "planned_labor_hours",
            "labor_effort_breakdown", "blended_loaded_rate_kusd_per_fte_year",
            "basis_of_estimate_id", "estimate_status", "reestimate_triggers",
            "cost_components", "prior_estimate", "estimate_change", "cost_drivers",
            "exclusions_and_double_counting_controls"
        ],
        "properties": {
            "labor_kusd": {"type": "number", "minimum": 0},
            "direct_non_labor_before_risk_kusd": {"type": "number", "minimum": 0},
            "risk_allowance_kusd": {"type": "number", "minimum": 0},
            "non_labor_kusd": {"type": "number", "minimum": 0},
            "total_kusd": {"type": "number", "minimum": 0},
            "low_kusd": {"type": "number", "minimum": 0},
            "high_kusd": {"type": "number", "minimum": 0},
            "estimate_class": {"type": "string", "minLength": 1},
            "estimate_currency_year": {"type": "integer", "const": 2026},
            "estimate_method": {"type": "string", "minLength": 1},
            "productive_hours_per_fte_year": {"type": "integer", "minimum": 1},
            "planned_fte_years": {"type": "number", "minimum": 0},
            "planned_labor_hours": {"type": "number", "minimum": 0},
            "labor_effort_breakdown": {
                "type": "object",
                "additionalProperties": {"type": "number", "minimum": 0}
            },
            "blended_loaded_rate_kusd_per_fte_year": {"type": "number", "minimum": 0},
            "basis_of_estimate_id": {"type": "string", "minLength": 1},
            "estimate_status": {"type": "string", "minLength": 1},
            "reestimate_triggers": {"type": "array", "minItems": 1, "items": {"type": "string"}},
            "cost_components": {
                "type": "object",
                "required": [
                    "external_engineering_and_lab_services_kusd",
                    "software_compute_and_data_kusd",
                    "equipment_materials_and_fabrication_kusd",
                    "facility_test_and_field_operations_kusd",
                    "regulatory_review_fees_kusd",
                    "legal_hearing_and_advisory_kusd",
                    "travel_and_field_support_kusd",
                    "other_direct_kusd",
                    "risk_allowance_kusd"
                ],
                "additionalProperties": {"type": "number", "minimum": 0}
            },
            "prior_estimate": {"type": "object", "required": ["version", "labor_kusd", "non_labor_kusd", "total_kusd", "fte_years"], "additionalProperties": True},
            "estimate_change": {"type": "object", "required": ["labor_delta_kusd", "non_labor_delta_kusd", "total_delta_kusd", "total_change_pct", "reason"], "additionalProperties": True},
            "cost_drivers": {"type": "array", "items": {"type": "string"}},
            "exclusions_and_double_counting_controls": {"type": "array", "items": {"type": "string"}},
            "allocated_program_package_kusd": {"type": "number", "minimum": 0},
            "allocated_program_package_sources": {"type": "array", "items": {"type": "object"}},
            "fully_burdened_task_view_kusd": {"type": "number", "minimum": 0},
            "fully_burdened_view_is_non_additive": {"type": "boolean"}
        },
        "additionalProperties": True
    }
    SCHEMA_PATH.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    db = load_database(DB_PATH)
    if db.get("meta", {}).get("version") == VERSION and db.get("data_quality", {}).get("cost_reestimate_release") == VERSION:
        print("v4.2 cost re-estimate already applied")
        return

    role_by_id = {role["role_id"]: role for role in db["resources"]["roles"]}
    assignment_map = {row["assignment_id"]: row for row in db["resources"]["assignments"]}
    next_assignment = [max([int(str(key).split("-")[-1]) for key in assignment_map if re.fullmatch(r"A-\d+", str(key))] or [0]) + 1]
    portfolio_weights = db.get("planning_profile", {}).get("year_weights") or {}

    # Update role rates before recalculating task labor.
    for role in db["resources"]["roles"]:
        if role["role_id"] in ROLE_RATES_KUSD_PER_FTE_YEAR:
            role["loaded_rate_kusd_per_fte_year"] = ROLE_RATES_KUSD_PER_FTE_YEAR[role["role_id"]]

    # Remove the prior route-fee double count. Route-specific NRC review fees and hearing support
    # are carried in the selected Part 50/52/53/57 module; this base task is limited to independent
    # application assurance and consistency review.
    for task in db["tasks"]:
        if task.get("id") == "P-PKG-08":
            task["name"] = "Independent Licensing Review and Application Assurance"
            task["description"] = (
                "Provide independent technical and licensing assurance across the commercial application, including cross-chapter consistency, "
                "challenge reviews, readiness assessments, and specialist advice. Route-specific NRC review fees, hearings, RAIs, and issuance support are costed in the selected licensing-path module."
            )

    # Shared/base tasks use the global assignment collection.
    new_assignments: list[dict[str, Any]] = []
    for task in db["tasks"]:
        rows = [assignment_map[aid] for aid in task.get("resources", {}).get("assignment_ids") or [] if aid in assignment_map]
        rows = recost_task(
            task,
            rows,
            role_by_id,
            next_assignment,
            portfolio_weights,
            route_path=None,
            route_specific=False,
        )
        new_assignments.extend(rows)
    db["resources"]["assignments"] = new_assignments

    # Route tasks keep inline assignments because only the selected route is
    # instantiated in a scenario.
    route_task_count = 0
    for route_path, modules in db["pathway_modules"].items():
        for route_tasks in modules.values():
            for task in route_tasks:
                route_task_count += 1
                rows = list(task.get("resources", {}).get("assignments") or [])
                rows = recost_task(
                    task,
                    rows,
                    role_by_id,
                    next_assignment,
                    portfolio_weights,
                    route_path=route_path,
                    route_specific=True,
                )
                task["resources"]["assignments"] = rows

    update_role_totals(db)
    allocate_package_cost_views(db)
    aggregate_financials(db)
    update_route_cost_model(db)
    audit_rows = build_audit_rows(db)
    update_metadata(db, route_task_count, len(audit_rows))

    # Add explicit source records for the new estimate basis.
    source_urls = {str(row.get("URL") or row.get("url") or "") for row in db.get("sources", [])}
    additions = [
        {
            "Source": "BLS Nuclear Engineers occupational pay data",
            "Type": "Labor-rate benchmark",
            "URL": "https://www.bls.gov/ooh/architecture-and-engineering/nuclear-engineers.htm",
            "Use in Plan": "Reasonableness check for technical salary basis before full burden and contractor loading.",
        },
        {
            "Source": "BLS Architectural and Engineering Managers occupational pay data",
            "Type": "Labor-rate benchmark",
            "URL": "https://www.bls.gov/ooh/management/architectural-and-engineering-managers.htm",
            "Use in Plan": "Reasonableness check for management and technical-authority salary basis.",
        },
        {
            "Source": "NRC 10 CFR 170.20 professional staff-hour rates",
            "Type": "Regulatory fee basis",
            "URL": "https://www.nrc.gov/reading-rm/doc-collections/cfr/part170/part170-0020.html",
            "Use in Plan": "Advanced-reactor reduced and full professional review-rate planning references.",
        },
        {
            "Source": "GAO Cost Estimating and Assessment Guide GAO-20-195G",
            "Type": "Cost-estimating practice",
            "URL": "https://www.gao.gov/products/gao-20-195g",
            "Use in Plan": "Bottom-up WBS, assumptions, risk/uncertainty, documentation, and reconciliation approach.",
        },
    ]
    for row in additions:
        if row["URL"] not in source_urls:
            db.setdefault("sources", []).append(row)

    write_sharded_database(db, ROOT / "data", application_version="4.2.2")
    update_schema()

    AUDIT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(audit_rows[0].keys()))
        writer.writeheader()
        writer.writerows(audit_rows)

    print(f"Updated {len(db['tasks'])} shared tasks and {route_task_count} route tasks")
    print(f"Wrote {AUDIT_CSV}")


if __name__ == "__main__":
    main()
