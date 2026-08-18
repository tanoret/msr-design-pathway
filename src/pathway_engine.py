from __future__ import annotations

import calendar
import copy
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from typing import Any, Iterable

import networkx as nx

DEMONSTRATOR_PATH = "doe_launchpad"
POWER_PATHS = ("part50", "part52", "part53", "part57")
EXECUTABLE_POWER_PATHS = ("part50", "part52", "part53")
PATH_DISPLAY_NAMES = {
    "doe_launchpad": "DOE Launch Pad",
    "part50": "10 CFR Part 50",
    "part52": "10 CFR Part 52",
    "part53": "10 CFR Part 53",
    "part57": "Proposed 10 CFR Part 57",
}

DEMO_PREDECESSOR_REMAP = {
    "D-LP-11": "D-LP2-04",
    "D-LP-12": "D-LP2-14",
    "D-LP-04": "D-LP2-06",
}

BASE_CONSTRUCTION_START = date(2030, 1, 1)
BASE_MECHANICAL_COMPLETION = date(2034, 9, 30)
BASE_OPERATION_AUTHORIZATION = date(2035, 3, 31)
BASE_INITIAL_CRITICALITY = date(2035, 6, 30)
BASE_COMMERCIAL_OPERATION = date(2035, 12, 31)
BASE_OPTIMIZED_REFERENCE = date(2038, 12, 31)


@dataclass(frozen=True)
class ScenarioOptions:
    demonstrator_variant: str = "launchpad_usa"
    power_reactor_path: str = "part53"
    power_reactor_variant: str = "col"
    part57_mode: str = "current_with_fallback"
    part57_fallback_path: str = "part53"
    part57_fallback_variant: str = "col"
    labor_factor: float = 1.0
    non_labor_factor: float = 1.0
    power_schedule_shift_months: int = 0
    preserve_demo_2028_target: bool = True


class ScenarioError(ValueError):
    """Raised when a scenario selection is internally inconsistent."""


def parse_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value), "%Y-%m-%d").date()


def iso(value: date) -> str:
    return value.isoformat()


def add_months(value: date, months: int) -> date:
    month_index = value.year * 12 + value.month - 1 + int(months)
    year, month_zero = divmod(month_index, 12)
    month = month_zero + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def month_delta(start: date, finish: date) -> int:
    """Calendar-month difference used for schedule phase shifts."""
    return (finish.year - start.year) * 12 + (finish.month - start.month)


def day_after(value: date) -> date:
    return value + timedelta(days=1)


def annual_fractions(start: date, finish: date, year_weights: dict[str, float] | None = None) -> dict[str, float]:
    """Allocate task effort/cost over active years using supplied weights.

    Calendar overlap remains the base. Portfolio and task-shape weights move
    flexible work within the controlled activity window while preserving the
    task total exactly.
    """
    raw: dict[str, float] = {}
    for year in range(start.year, finish.year + 1):
        low = max(start, date(year, 1, 1))
        high = min(finish, date(year, 12, 31))
        if high >= low:
            overlap = float((high - low).days + 1)
            raw[str(year)] = overlap * float((year_weights or {}).get(str(year), 1.0))
    total = sum(raw.values()) or 1.0
    return {year: value / total for year, value in raw.items()}


def _task_year_weights(
    task: dict[str, Any],
    start: date,
    finish: date,
    portfolio_weights: dict[str, float] | None,
) -> dict[str, float]:
    """Combine the portfolio ramp with a task-specific loading shape.

    ``back_loaded`` is used for commercial qualification, final design, and
    licensing closure; ``bell`` is used for fabrication, construction, and test
    campaigns; ``front_loaded`` is reserved for strategy and requirements work.
    The factors affect only allocation within the authored start/finish window.
    """
    years = list(range(start.year, finish.year + 1))
    if not years:
        return {}
    shape = str((task.get("schedule") or {}).get("loading_shape") or "flat").lower()
    override = (task.get("schedule") or {}).get("year_weight_multipliers") or {}
    result: dict[str, float] = {}
    denominator = max(len(years) - 1, 1)
    for index, year in enumerate(years):
        position = index / denominator
        if shape == "back_loaded":
            shape_factor = 0.42 + 1.38 * (position ** 1.35)
        elif shape == "front_loaded":
            shape_factor = 1.75 - 1.05 * (position ** 0.8)
        elif shape == "bell":
            shape_factor = 0.62 + 1.05 * (1.0 - abs(2.0 * position - 1.0))
        elif shape == "milestone_backloaded":
            shape_factor = 0.30 + 1.70 * (position ** 1.7)
        else:
            shape_factor = 1.0
        result[str(year)] = (
            float((portfolio_weights or {}).get(str(year), 1.0))
            * shape_factor
            * float(override.get(str(year), 1.0))
        )
    return result


def _duration_years(start: date, finish: date) -> float:
    return max(((finish - start).days + 1) / 365.25, 1 / 12)


def _variant_ok(task: dict[str, Any], variant: str) -> bool:
    variants = task.get("variant_applicability") or ["all"]
    return "all" in variants or variant in variants


def _mode_ok(task: dict[str, Any], mode: str | None) -> bool:
    modes = task.get("mode_applicability") or ["all"]
    return mode is None or "all" in modes or mode in modes


def _select_module_tasks(
    database: dict[str, Any],
    pathway: str,
    scope: str,
    *,
    variant: str,
    mode: str | None = None,
) -> list[dict[str, Any]]:
    modules = database.get("pathway_modules", {}).get(pathway, {}).get(scope, [])
    return [task for task in modules if _variant_ok(task, variant) and _mode_ok(task, mode)]


def pathway_variants(database: dict[str, Any], pathway: str) -> dict[str, dict[str, Any]]:
    return copy.deepcopy(database["pathways"][pathway].get("variants") or {})


def default_variant(database: dict[str, Any], pathway: str) -> str:
    return str(database["pathways"][pathway].get("default_variant") or next(iter(pathway_variants(database, pathway))))


def _validate_options(database: dict[str, Any], options: ScenarioOptions) -> None:
    if options.demonstrator_variant not in pathway_variants(database, DEMONSTRATOR_PATH):
        raise ScenarioError(f"Unknown DOE Launch Pad variant: {options.demonstrator_variant}")
    if options.power_reactor_path not in POWER_PATHS:
        raise ScenarioError(f"Unknown commercial power-reactor path: {options.power_reactor_path}")
    if options.power_reactor_variant not in pathway_variants(database, options.power_reactor_path):
        raise ScenarioError(
            f"Unknown {options.power_reactor_path} variant: {options.power_reactor_variant}"
        )
    if options.part57_mode not in {"current_with_fallback", "hypothetical_final_rule"}:
        raise ScenarioError(f"Unknown Part 57 planning mode: {options.part57_mode}")
    if options.power_reactor_path == "part57" and options.part57_mode == "current_with_fallback":
        if options.part57_fallback_path not in EXECUTABLE_POWER_PATHS:
            raise ScenarioError("Current Part 57 planning requires a Part 50, 52, or 53 fallback.")
        if options.part57_fallback_variant not in pathway_variants(database, options.part57_fallback_path):
            raise ScenarioError(
                f"Unknown fallback variant {options.part57_fallback_variant} for {options.part57_fallback_path}."
            )
    if options.labor_factor <= 0 or options.non_labor_factor <= 0:
        raise ScenarioError("Cost and labor factors must be positive.")


def _route_context(options: ScenarioOptions) -> dict[str, str]:
    if options.power_reactor_path != "part57":
        return {
            "effective_path": options.power_reactor_path,
            "effective_variant": options.power_reactor_variant,
            "part57_overlay": "none",
        }
    if options.part57_mode == "current_with_fallback":
        return {
            "effective_path": options.part57_fallback_path,
            "effective_variant": options.part57_fallback_variant,
            "part57_overlay": "current_with_fallback",
        }
    return {
        "effective_path": "part57",
        "effective_variant": options.power_reactor_variant,
        "part57_overlay": "hypothetical_final_rule",
    }


def _task_finish(tasks: Iterable[dict[str, Any]], task_id: str) -> date:
    for task in tasks:
        if task.get("id") == task_id:
            return parse_date(task["schedule"]["finish"])
    raise ScenarioError(f"Required route anchor task is not active: {task_id}")


def _route_schedule_profile(route_tasks: list[dict[str, Any]], options: ScenarioOptions) -> dict[str, Any]:
    context = _route_context(options)
    path = context["effective_path"]
    variant = context["effective_variant"]

    if path == "part50":
        construction_authorization = _task_finish(route_tasks, "P50-09")
        operation_authorization = _task_finish(route_tasks, "P50-18")
        application = _task_finish(route_tasks, "P50-05")
        license_issue = operation_authorization
        review_cycles = 2
    elif path == "part52":
        construction_authorization = _task_finish(route_tasks, "P52-09")
        operation_authorization = _task_finish(route_tasks, "P52-15")
        application = _task_finish(route_tasks, "P52-06")
        license_issue = _task_finish(route_tasks, "P52-09")
        review_cycles = 1 + int("esp" in variant) + int("dc" in variant)
    elif path == "part53":
        if variant == "cp_ol":
            construction_authorization = _task_finish(route_tasks, "P53-P02")
            application = _task_finish(route_tasks, "P53-P01")
            license_issue = _task_finish(route_tasks, "P53-P03")
            review_cycles = 2
        else:
            construction_authorization = _task_finish(route_tasks, "P53-12")
            application = _task_finish(route_tasks, "P53-C01")
            license_issue = _task_finish(route_tasks, "P53-C02")
            review_cycles = 1
        operation_authorization = _task_finish(route_tasks, "P53-15")
    elif path == "part57":
        construction_authorization = _task_finish(route_tasks, "P57-H10")
        operation_authorization = _task_finish(route_tasks, "P57-H11")
        application = _task_finish(route_tasks, "P57-H09")
        license_issue = _task_finish(route_tasks, "P57-H10")
        review_cycles = 1
    else:  # pragma: no cover - validated above
        raise ScenarioError(path)

    # The nominal plan begins commercial field construction on 2030-01-01.
    # A route may authorize earlier, but the shared construction mobilization
    # remains fixed unless the user applies a schedule sensitivity.
    nominal_start = BASE_CONSTRUCTION_START
    if construction_authorization >= nominal_start:
        nominal_start = day_after(construction_authorization)
    construction_start = add_months(nominal_start, int(options.power_schedule_shift_months))
    construction_shift = month_delta(BASE_CONSTRUCTION_START, construction_start)
    mechanical_completion = add_months(BASE_MECHANICAL_COMPLETION, construction_shift)

    # Preserve the common 2035 licensed-operation target while respecting any
    # later route-specific authorization or user-entered schedule shift.
    minimum_operation_authorization = add_months(mechanical_completion, 6)
    operation_authorization = max(operation_authorization, minimum_operation_authorization, add_months(BASE_OPERATION_AUTHORIZATION, construction_shift))
    initial_criticality = max(add_months(operation_authorization, 3), add_months(BASE_INITIAL_CRITICALITY, construction_shift))
    commercial_operation = max(add_months(operation_authorization, 9), add_months(BASE_COMMERCIAL_OPERATION, construction_shift))
    optimized_reference = max(add_months(commercial_operation, 30), add_months(BASE_OPTIMIZED_REFERENCE, construction_shift))

    return {
        "effective_path": path,
        "effective_variant": variant,
        "application_date": application,
        "construction_authorization_date": construction_authorization,
        "license_issue_date": license_issue,
        "construction_start_date": construction_start,
        "construction_shift_months": construction_shift,
        "mechanical_completion_date": mechanical_completion,
        "operation_authorization_date": operation_authorization,
        "initial_criticality_date": initial_criticality,
        "commercial_operation_date": commercial_operation,
        "optimized_reference_date": optimized_reference,
        "review_cycles": review_cycles,
    }


def _copy_assignment(
    assignment: dict[str, Any],
    *,
    task_start: date,
    task_finish: date,
    labor_factor: float,
    task_id: str,
    route_label: str | None = None,
    year_weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    row = copy.deepcopy(assignment)
    row["task_id"] = task_id
    if route_label:
        row["scenario_route"] = route_label
    fte_years = float(row.get("fte_years") or 0.0) * labor_factor
    rate = float(row.get("loaded_rate_kusd_per_fte_year") or 0.0)
    labor_cost = fte_years * rate
    fractions = annual_fractions(task_start, task_finish, year_weights)
    row["start"] = iso(task_start)
    row["finish"] = iso(task_finish)
    row["fte_years"] = round(fte_years, 6)
    row["avg_fte"] = round(fte_years / _duration_years(task_start, task_finish), 6)
    row["labor_cost_kusd"] = round(labor_cost, 6)
    row["annual_fte_years"] = {year: round(fte_years * frac, 6) for year, frac in fractions.items()}
    row["annual_labor_kusd"] = {year: round(labor_cost * frac, 6) for year, frac in fractions.items()}
    return row


def _copy_task(
    task: dict[str, Any],
    *,
    shift_months: int,
    labor_factor: float,
    non_labor_factor: float,
    assignment_source: dict[str, dict[str, Any]],
    route_label: str | None = None,
    year_weights: dict[str, float] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    # The engineering work-package payload is intentionally large and immutable
    # during scenario calculation. Copy only structures that the scenario engine
    # changes, while sharing read-only technical detail with the loaded database.
    copied = dict(task)
    copied["schedule"] = copy.deepcopy(task.get("schedule") or {})
    copied["cost"] = copy.deepcopy(task.get("cost") or {})
    copied["resources"] = copy.deepcopy(task.get("resources") or {})
    copied["execution"] = copy.deepcopy(task.get("execution") or {})

    schedule = copied["schedule"]
    start = add_months(parse_date(schedule["start"]), shift_months)
    finish = add_months(parse_date(schedule["finish"]), shift_months)
    schedule["start"] = iso(start)
    schedule["finish"] = iso(finish)
    schedule["duration_months"] = round(((finish - start).days + 1) / 30.4375, 1)
    if schedule.get("latest_required_finish"):
        schedule["latest_required_finish"] = iso(add_months(parse_date(schedule["latest_required_finish"]), shift_months))

    original_cost = copied.get("cost", {})
    original_labor = float(original_cost.get("labor_kusd") or 0.0)
    original_non_labor = float(original_cost.get("non_labor_kusd") or 0.0)
    original_total = float(original_cost.get("total_kusd") or (original_labor + original_non_labor))
    original_risk = float(original_cost.get("risk_allowance_kusd") or 0.0)
    original_direct_non_labor = float(
        original_cost.get("direct_non_labor_before_risk_kusd")
        if original_cost.get("direct_non_labor_before_risk_kusd") is not None
        else max(0.0, original_non_labor - original_risk)
    )
    labor = original_labor * labor_factor
    direct_non_labor = original_direct_non_labor * non_labor_factor
    risk_pct = float(original_cost.get("risk_allowance_pct") or 0.0)
    contingency_only = original_direct_non_labor == 0.0 and original_risk > 0.0 and "contingency" in str(copied.get("name") or "").lower()
    risk = original_risk * non_labor_factor if contingency_only else (labor + direct_non_labor) * risk_pct
    non_labor = direct_non_labor + risk
    total = labor + non_labor
    task_weights = _task_year_weights(copied, start, finish, year_weights)
    fractions = annual_fractions(start, finish, task_weights)
    cost = copied["cost"]
    cost["labor_kusd"] = round(labor, 6)
    cost["direct_non_labor_before_risk_kusd"] = round(direct_non_labor, 6)
    cost["direct_cost_before_risk_kusd"] = round(labor + direct_non_labor, 6)
    cost["risk_allowance_kusd"] = round(risk, 6)
    cost["non_labor_kusd"] = round(non_labor, 6)
    cost["total_kusd"] = round(total, 6)

    original_components = original_cost.get("cost_components") or {}
    components: dict[str, float] = {}
    for key, value in original_components.items():
        if key == "risk_allowance_kusd":
            continue
        components[key] = round(float(value or 0.0) * non_labor_factor, 6)
    components["risk_allowance_kusd"] = round(risk, 6)
    cost["cost_components"] = components

    original_low = float(original_cost.get("low_kusd") or original_total)
    original_high = float(original_cost.get("high_kusd") or original_total)
    low_pct = max(0.0, 1.0 - original_low / original_total) if original_total else 0.0
    high_pct = max(0.0, original_high / original_total - 1.0) if original_total else 0.0
    cost["low_kusd"] = round(total * (1.0 - low_pct), 6)
    cost["high_kusd"] = round(total * (1.0 + high_pct), 6)
    cost["planned_fte_years"] = round(float(original_cost.get("planned_fte_years") or 0.0) * labor_factor, 6)
    cost["planned_labor_hours"] = round(float(original_cost.get("planned_labor_hours") or 0.0) * labor_factor, 1)
    if original_cost.get("labor_effort_breakdown"):
        cost["labor_effort_breakdown"] = {
            key: round(float(value or 0.0) * labor_factor, 1)
            for key, value in original_cost["labor_effort_breakdown"].items()
        }
    cost["blended_loaded_rate_kusd_per_fte_year"] = round(
        labor / cost["planned_fte_years"], 3
    ) if cost.get("planned_fte_years") else 0.0
    allocated = float(original_cost.get("allocated_program_package_kusd") or 0.0) * non_labor_factor
    cost["allocated_program_package_kusd"] = round(allocated, 6)
    if original_cost.get("allocated_program_package_sources"):
        cost["allocated_program_package_sources"] = [
            {
                **row,
                "allocated_kusd": round(float(row.get("allocated_kusd") or 0.0) * non_labor_factor, 6),
            }
            for row in original_cost["allocated_program_package_sources"]
        ]
    cost["fully_burdened_task_view_kusd"] = round(total + allocated, 6)
    change = cost.get("estimate_change") or {}
    prior_total = float((cost.get("prior_estimate") or {}).get("total_kusd") or 0.0)
    change["labor_delta_kusd"] = round(labor - float((cost.get("prior_estimate") or {}).get("labor_kusd") or 0.0), 6)
    change["non_labor_delta_kusd"] = round(non_labor - float((cost.get("prior_estimate") or {}).get("non_labor_kusd") or 0.0), 6)
    change["total_delta_kusd"] = round(total - prior_total, 6)
    change["total_change_pct"] = round(((total / prior_total) - 1.0) * 100.0, 2) if prior_total > 0 else None
    cost["estimate_change"] = change
    cost["annual_labor_kusd"] = {year: round(labor * frac, 6) for year, frac in fractions.items()}
    cost["annual_non_labor_kusd"] = {year: round(non_labor * frac, 6) for year, frac in fractions.items()}
    cost["annual_kusd"] = {year: round(total * frac, 6) for year, frac in fractions.items()}

    assignments: list[dict[str, Any]] = []
    inline = copied.get("resources", {}).get("assignments") or []
    if inline:
        raw_assignments = inline
    else:
        raw_assignments = [assignment_source[aid] for aid in copied.get("resources", {}).get("assignment_ids") or [] if aid in assignment_source]
    for raw in raw_assignments:
        assignments.append(
            _copy_assignment(
                raw,
                task_start=start,
                task_finish=finish,
                labor_factor=labor_factor,
                task_id=str(copied["id"]),
                route_label=route_label,
                year_weights=task_weights,
            )
        )
    resources = copied["resources"]
    resources["assignments"] = assignments
    resources["assignment_ids"] = [row["assignment_id"] for row in assignments]
    resources["fte_years"] = round(sum(float(row.get("fte_years") or 0.0) for row in assignments), 6)
    resources["avg_fte"] = round(resources["fte_years"] / _duration_years(start, finish), 6)
    annual_fte: dict[str, float] = {}
    for row in assignments:
        for year, value in (row.get("annual_fte_years") or {}).items():
            annual_fte[year] = annual_fte.get(year, 0.0) + float(value)
    resources["annual_fte_years"] = {year: round(value, 6) for year, value in sorted(annual_fte.items())}

    source_package = task.get("engineering_work_package")
    if isinstance(source_package, dict):
        package = dict(source_package)
        controls = dict(source_package.get("execution_controls") or {})
        controls["schedule_start"] = schedule["start"]
        controls["schedule_finish"] = schedule["finish"]
        controls["predecessors"] = list(schedule.get("predecessors") or [])
        package["execution_controls"] = controls
        resource_plan = dict(source_package.get("resource_plan") or {})
        resource_plan["planned_fte_years"] = resources["fte_years"]
        resource_plan["planned_average_fte"] = resources["avg_fte"]
        package["resource_plan"] = resource_plan
        copied["engineering_work_package"] = package

    if route_label:
        copied["scenario_route"] = route_label
    return copied, assignments


def _common_task_shift(task: dict[str, Any], profile: dict[str, Any], options: ScenarioOptions) -> int:
    shift = 0
    if task.get("concept") == "Power Reactor":
        shift = int(options.power_schedule_shift_months)
        start = parse_date(task["schedule"]["start"])
        if task.get("task_scope") == "power_reactor_construction" and start >= BASE_CONSTRUCTION_START:
            shift = int(profile["construction_shift_months"])
    return shift


def _commercial_operation_task(task: dict[str, Any]) -> bool:
    task_id = str(task.get("id") or "")
    name = str(task.get("name") or "").lower()
    return task_id.startswith("P-OPT-") or any(
        phrase in name
        for phrase in ["initial criticality", "power ascension", "commercial operation", "optimization"]
    )


def _align_operation_tasks(task: dict[str, Any], profile: dict[str, Any]) -> int:
    if task.get("concept") != "Power Reactor" or not _commercial_operation_task(task):
        return 0
    start = parse_date(task["schedule"]["start"])
    minimum = profile["operation_authorization_date"]
    if start >= minimum:
        return 0
    return max(0, month_delta(start, minimum))


def _patch_common_task_text(task: dict[str, Any], options: ScenarioOptions) -> None:
    if task.get("id") == "P-LIC-DEC.01":
        task["name"] = "Commercial power-reactor licensing pathway and product-stack decision"
        task["description"] = (
            "Select and maintain the commercial power-reactor licensing strategy independently from the DOE-authorized demonstrator. "
            "The decision compares Part 50, Part 52, Part 53, and Part 57 readiness using explicit product, design-maturity, construction-verification, fleet, cost, and schedule criteria."
        )
    if task.get("concept") == "Power Reactor":
        task["selected_power_path"] = options.power_reactor_path
        task["selected_power_variant"] = options.power_reactor_variant


def _active_route_tasks(database: dict[str, Any], options: ScenarioOptions) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    demo = _select_module_tasks(
        database,
        "doe_launchpad",
        "demonstrator",
        variant=options.demonstrator_variant,
    )
    selected_power: list[dict[str, Any]] = []
    route_meta: dict[str, Any] = {"demo_route_ids": [task["id"] for task in demo]}

    if options.power_reactor_path == "part57":
        selected_power.extend(
            _select_module_tasks(
                database,
                "part57",
                "power_reactor",
                variant=options.power_reactor_variant,
                mode=options.part57_mode,
            )
        )
        if options.part57_mode == "current_with_fallback":
            fallback = _select_module_tasks(
                database,
                options.part57_fallback_path,
                "power_reactor",
                variant=options.part57_fallback_variant,
            )
            fallback_labeled = []
            for source_task in fallback:
                task = dict(source_task)
                task["scenario_route"] = "Part 57 executable fallback"
                task["fallback_for_part57"] = True
                fallback_labeled.append(task)
            selected_power.extend(fallback_labeled)
            fallback = fallback_labeled
            route_meta["fallback_route_ids"] = [task["id"] for task in fallback]
    else:
        selected_power.extend(
            _select_module_tasks(
                database,
                options.power_reactor_path,
                "power_reactor",
                variant=options.power_reactor_variant,
            )
        )
    route_meta["power_route_ids"] = [task["id"] for task in selected_power]
    return demo + selected_power, route_meta


def _operation_anchor(options: ScenarioOptions) -> str:
    context = _route_context(options)
    path, variant = context["effective_path"], context["effective_variant"]
    if path == "part50":
        return "P50-18"
    if path == "part52":
        return "P52-15"
    if path == "part53":
        return "P53-15"
    if path == "part57":
        return "P57-H11"
    raise ScenarioError(path)


def _remap_predecessors(tasks: list[dict[str, Any]], options: ScenarioOptions) -> None:
    active_ids = {str(task["id"]) for task in tasks}
    demo_host = "D-LP2-03U" if options.demonstrator_variant == "launchpad_usa" else "D-LP2-03I"
    remap = {**DEMO_PREDECESSOR_REMAP, "D-LP-02": demo_host, "P-LIC-53.07": _operation_anchor(options)}
    for task in tasks:
        predecessors: list[str] = []
        for predecessor in task.get("schedule", {}).get("predecessors") or []:
            predecessor = remap.get(str(predecessor), str(predecessor))
            if predecessor in active_ids and predecessor != task["id"] and predecessor not in predecessors:
                predecessors.append(predecessor)
        if task.get("id") == "P53-P03":
            predecessors = [item for item in predecessors if item != "P53-15"]
        task.setdefault("schedule", {})["predecessors"] = predecessors


def _topological_validation(tasks: list[dict[str, Any]]) -> None:
    ids = [str(task["id"]) for task in tasks]
    if len(ids) != len(set(ids)):
        duplicates = sorted({task_id for task_id in ids if ids.count(task_id) > 1})
        raise ScenarioError(f"Duplicate active task IDs: {duplicates[:10]}")
    graph = nx.DiGraph()
    graph.add_nodes_from(ids)
    for task in tasks:
        for predecessor in task.get("schedule", {}).get("predecessors") or []:
            graph.add_edge(str(predecessor), str(task["id"]))
    if not nx.is_directed_acyclic_graph(graph):
        cycle = nx.find_cycle(graph)
        raise ScenarioError(f"Scenario dependency cycle: {cycle[:8]}")


def _route_cost(tasks: list[dict[str, Any]], ids: set[str]) -> dict[str, float]:
    selected = [task for task in tasks if task["id"] in ids]
    labor = sum(float(task.get("cost", {}).get("labor_kusd") or 0.0) for task in selected)
    non_labor = sum(float(task.get("cost", {}).get("non_labor_kusd") or 0.0) for task in selected)
    repeat_credit = sum(float(task.get("cost", {}).get("repeat_unit_credit_kusd") or 0.0) for task in selected)
    return {
        "labor_kusd": labor,
        "non_labor_kusd": non_labor,
        "total_kusd": labor + non_labor,
        "repeat_unit_credit_kusd": repeat_credit,
        "repeat_route_cost_kusd": max((labor + non_labor) - repeat_credit, 0.0),
    }


def _milestone(
    milestone_id: str,
    concept: str,
    label: str,
    date_value: date,
    milestone_type: str,
    authority: str,
    evidence: str,
    successor: str,
    pathway: str = "common",
) -> dict[str, Any]:
    return {
        "Milestone ID": milestone_id,
        "Program / Concept": concept,
        "Milestone / Decision Gate": label,
        "Baseline Date": iso(date_value),
        "Type": milestone_type,
        "Entry Criteria / Evidence": evidence,
        "Decision Authority": authority,
        "Successor Work Authorized": successor,
        "Schedule Basis": "Scenario-derived from the active licensing products and construction/operation sequence.",
        "Status": "Planning target",
        "Pathway": pathway,
    }


def _route_milestones(
    route_tasks: list[dict[str, Any]],
    profile: dict[str, Any],
    options: ScenarioOptions,
) -> list[dict[str, Any]]:
    task_by_id = {task["id"]: task for task in route_tasks}
    rows: list[dict[str, Any]] = []
    demo_host_id = "D-LP2-03U" if options.demonstrator_variant == "launchpad_usa" else "D-LP2-03I"
    rows.extend(
        [
            _milestone("DEMO-LP-01", "Demonstrator", "DOE Launch Pad route and host decision", _task_finish(route_tasks, demo_host_id), "Authorization strategy", "CNO / DOE / Host", "Host due diligence, eligibility, roles, property, IP, and authorization interface accepted", "Finalize DOE/host agreement and safety-basis architecture", "doe_launchpad"),
            _milestone("DEMO-LP-02", "Demonstrator", "DOE/host authorization application complete", _task_finish(route_tasks, "D-LP2-12"), "Authorization application", "CNO / Program Director", "Integrated safety, environment, QA, material, security, host, and construction evidence index approved", "DOE/host review and readiness assessment", "doe_launchpad"),
            _milestone("DEMO-LP-03", "Demonstrator", "Authorization to perform irreversible site work", _task_finish(route_tasks, "D-LP2-14"), "Construction authorization", "DOE / Host", "Authorization conditions and construction readiness evidence accepted", "Irreversible host-site construction", "doe_launchpad"),
            _milestone("DEMO-LP-04", "Demonstrator", "Demonstrator mechanical completion and construction turnover", date(2028, 12, 31), "Mechanical completion", "CNO / Construction / Host", "Installed configuration, as-builts, turnover packages, and controlled punch list complete", "Cold and hot commissioning", "doe_launchpad"),
            _milestone("DEMO-LP-05", "Demonstrator", "Demonstrator operation authorization readiness", _task_finish(route_tasks, "D-LP2-16"), "Operation readiness", "DOE / Host / CNO", "Commissioning, nuclear-material, procedure, staffing, training, and readiness evidence accepted", "Initial criticality and experimental campaign", "doe_launchpad"),
        ]
    )

    path = profile["effective_path"]
    variant = profile["effective_variant"]
    if options.power_reactor_path == "part57" and options.part57_mode == "current_with_fallback":
        rows.extend([
            _milestone("PWR-P57-RDY", "Power Reactor", "Proposed Part 57 eligibility and pilot-application readiness", _task_finish(route_tasks, "P57-R04"), "Regulatory readiness", "CNO / Regulatory Counsel", "Eligibility, deployment model, standardization business case, and draft application crosswalk complete", "Maintain fallback and evaluate future migration", "part57"),
            _milestone("PWR-P57-DEC", "Power Reactor", "Part 57 migration decision with executable fallback preserved", _task_finish(route_tasks, "P57-R05"), "Pathway decision", "CNO / Owner", "Current rule status, implementation guidance, eligibility, and fallback licensing basis reviewed", "Continue fallback or approve controlled migration after a usable final rule", "part57"),
        ])
    if path == "part50":
        rows.extend([
            _milestone("PWR-P50-01", "Power Reactor", "Part 50 Construction Permit application submitted", _task_finish(route_tasks, "P50-05"), "Application", "CNO / Applicant", "PSAR, ER, certifications, QA, and hearing record ready", "NRC CP review and hearing", "part50"),
            _milestone("PWR-P50-02", "Power Reactor", "Part 50 Construction Permit issued", _task_finish(route_tasks, "P50-09"), "Construction authorization", "NRC", "CP findings, hearing, ACRS, conditions, and commitments complete", "Detailed design and construction", "part50"),
            _milestone("PWR-P50-03", "Power Reactor", "Part 50 Operating License application submitted", _task_finish(route_tasks, "P50-14"), "Application", "CNO / Applicant", "As-built FSAR, TS, programs, staffing, training, and test evidence ready", "NRC OL review and inspections", "part50"),
            _milestone("PWR-P50-04", "Power Reactor", "Part 50 Operating License and operation authorization", profile["operation_authorization_date"], "Operation authorization", "NRC", "10 CFR 50.57 findings, inspections, programs, and tests complete", "Initial criticality", "part50"),
        ])
    elif path == "part52":
        if "esp" in variant:
            rows.append(_milestone("PWR-P52-ESP", "Power Reactor", "Early Site Permit issued", _task_finish(route_tasks, "P52-E02"), "Site approval", "NRC", "ESP safety/environmental review and hearing complete", "Reference ESP in COL and maintain site conditions", "part52"))
        if "dc" in variant:
            rows.append(_milestone("PWR-P52-DC", "Power Reactor", "Design Certification final rule", _task_finish(route_tasks, "P52-D03"), "Standard design approval", "NRC / Commission", "DC safety review, ACRS, rulemaking, Tier 1/2, and standard ITAAC complete", "Reference certified design in COL", "part52"))
        rows.extend([
            _milestone("PWR-P52-01", "Power Reactor", "Part 52 Combined License application submitted", _task_finish(route_tasks, "P52-06"), "Application", "CNO / Applicant", "Final design information, FSAR, ER, TS, programs, Tier 1/2, and ITAAC ready", "NRC COL review and hearing", "part52"),
            _milestone("PWR-P52-02", "Power Reactor", "Part 52 Combined License issued", _task_finish(route_tasks, "P52-09"), "Construction authorization", "NRC", "COL review, ACRS, hearing, and conditions complete", "Construction under COL and ITAAC program", "part52"),
            _milestone("PWR-P52-03", "Power Reactor", "All ITAAC complete and 52.103(g) finding", profile["operation_authorization_date"], "Operation authorization", "NRC", "ITAAC objective evidence, ICNs/UINs, inspections, hearing readiness, and acceptance-criteria finding complete", "Initial criticality", "part52"),
        ])
    elif path == "part53":
        if variant == "cp_ol":
            rows.extend([
                _milestone("PWR-P53-CPAPP", "Power Reactor", "Part 53 Construction Permit application submitted", _task_finish(route_tasks, "P53-P01"), "Application", "CNO / Applicant", "Preliminary Part 53 safety case and ER ready", "NRC CP review", "part53"),
                _milestone("PWR-P53-CP", "Power Reactor", "Part 53 Construction Permit issued", _task_finish(route_tasks, "P53-P02"), "Construction authorization", "NRC", "Part 53 CP findings, hearing, and conditions complete", "Construction and final safety case", "part53"),
                _milestone("PWR-P53-OL", "Power Reactor", "Part 53 Operating License issued", _task_finish(route_tasks, "P53-P03"), "License issuance", "NRC", "Final Part 53 safety case, programs, testing, and OL review complete", "Readiness for operation", "part53"),
            ])
        else:
            rows.extend([
                _milestone("PWR-P53-APP", "Power Reactor", "Part 53 Combined License application submitted", _task_finish(route_tasks, "P53-C01"), "Application", "CNO / Applicant", "PRA/SRE, LBEs, classification, DiD, functional containment, programs, and application complete", "NRC Part 53 COL review", "part53"),
                _milestone("PWR-P53-COL", "Power Reactor", "Part 53 Combined License issued", _task_finish(route_tasks, "P53-C02"), "Construction authorization", "NRC", "Part 53 COL review, ACRS/hearing, and license conditions complete", "Construction and performance verification", "part53"),
            ])
        rows.append(_milestone("PWR-P53-OP", "Power Reactor", "Part 53 readiness finding and authorization to operate", profile["operation_authorization_date"], "Operation authorization", "NRC", "Construction verification, performance evidence, monitoring, testing, and license conditions complete", "Initial criticality", "part53"))
    else:
        rows.extend([
            _milestone("PWR-P57-APP", "Power Reactor", "Hypothetical Part 57 standardized application submitted", _task_finish(route_tasks, "P57-H09"), "Hypothetical application", "CNO / Applicant", "Assumed final-rule products and digital evidence package complete", "Hypothetical NRC review", "part57"),
            _milestone("PWR-P57-LIC", "Power Reactor", "Hypothetical Part 57 license issued", _task_finish(route_tasks, "P57-H10"), "Hypothetical license", "NRC", "Assumed final-rule review and hearing complete", "Factory/site construction and standardized verification", "part57"),
            _milestone("PWR-P57-OP", "Power Reactor", "Hypothetical Part 57 readiness for operation", profile["operation_authorization_date"], "Hypothetical operation authorization", "NRC", "Standardized factory/site evidence and targeted inspections complete", "Initial criticality", "part57"),
        ])

    rows.extend([
        _milestone("PWR-COMMON-MC", "Power Reactor", "Power-reactor mechanical completion", profile["mechanical_completion_date"], "Mechanical completion", "CNO / EPC / Design Authority", "Construction complete, as-built configuration and turnover records accepted", "Preoperational and startup testing", path),
        _milestone("PWR-COMMON-IC", "Power Reactor", "Power-reactor initial criticality", profile["initial_criticality_date"], "Startup", "CNO / Licensed Operations", "Operation authorization, startup procedures, fuel/material readiness, and test prerequisites complete", "Power ascension", path),
        _milestone("PWR-COMMON-COD", "Power Reactor", "Commercial operation target", profile["commercial_operation_date"], "Commercial operation", "Owner / CNO", "Power ascension, performance demonstration, and commercial acceptance complete", "Reliability growth and economic optimization", path),
        _milestone("PWR-COMMON-OPT", "Power Reactor", "Optimized reference-plant baseline", profile["optimized_reference_date"], "Fleet baseline", "CNO / CTO / Owner", "Reliability, chemistry, component life, staffing, automation, and economics optimization complete", "Repeat deployment", path),
    ])
    return sorted(rows, key=lambda row: (row["Baseline Date"], row["Milestone ID"]))



def build_scenario(database: dict[str, Any], options: ScenarioOptions | None = None) -> dict[str, Any]:
    options = options or ScenarioOptions()
    _validate_options(database, options)
    route_raw, route_meta = _active_route_tasks(database, options)

    # The effective route tasks are needed to derive construction and operation
    # sequencing. For current Part 57 mode this means the full fallback route.
    profile = _route_schedule_profile(route_raw, options)
    assignment_source = {row["assignment_id"]: row for row in database["resources"]["assignments"]}
    year_weights = copy.deepcopy((database.get("planning_profile") or {}).get("year_weights") or {})

    tasks: list[dict[str, Any]] = []
    assignments: list[dict[str, Any]] = []
    for original in database["tasks"]:
        shift = _common_task_shift(original, profile, options)
        shift = max(shift, _align_operation_tasks(original, profile))
        copied, rows = _copy_task(
            original,
            shift_months=shift,
            labor_factor=options.labor_factor,
            non_labor_factor=options.non_labor_factor,
            assignment_source=assignment_source,
            year_weights=year_weights,
        )
        _patch_common_task_text(copied, options)
        tasks.append(copied)
        assignments.extend(rows)

    # Route tasks keep their authored product sequence; the user-entered global
    # power schedule sensitivity is applied to commercial route tasks only.
    for original in route_raw:
        shift = 0 if original.get("concept") == "Demonstrator" else int(options.power_schedule_shift_months)
        route_label = original.get("scenario_route") or PATH_DISPLAY_NAMES.get(original.get("pathway_applicability", [""])[0], "Route-specific")
        copied, rows = _copy_task(
            original,
            shift_months=shift,
            labor_factor=options.labor_factor,
            non_labor_factor=options.non_labor_factor,
            assignment_source={},
            route_label=route_label,
            year_weights=year_weights,
        )
        tasks.append(copied)
        assignments.extend(rows)

    _remap_predecessors(tasks, options)
    _topological_validation(tasks)

    route_ids = set(route_meta["power_route_ids"])
    demo_ids = set(route_meta["demo_route_ids"])
    fallback_ids = set(route_meta.get("fallback_route_ids") or [])
    part57_ids = {task_id for task_id in route_ids if task_id.startswith("P57-")}
    part57_readiness_ids = {task_id for task_id in part57_ids if task_id.startswith("P57-R")}
    effective_ids = route_ids - part57_ids if fallback_ids else route_ids

    common_ids = {task["id"] for task in database["tasks"]}
    common_cost = _route_cost(tasks, common_ids)
    demo_cost = _route_cost(tasks, demo_ids)
    power_cost = _route_cost(tasks, effective_ids)
    part57_overlay_cost = _route_cost(tasks, part57_readiness_ids)
    fallback_cost = _route_cost(tasks, fallback_ids)

    labor_total = sum(float(task.get("cost", {}).get("labor_kusd") or 0.0) for task in tasks)
    non_labor_total = sum(float(task.get("cost", {}).get("non_labor_kusd") or 0.0) for task in tasks)
    fte_years = sum(float(row.get("fte_years") or 0.0) for row in assignments)
    annual_cost: dict[str, float] = {}
    annual_labor: dict[str, float] = {}
    annual_non_labor: dict[str, float] = {}
    annual_fte: dict[str, float] = {}
    for task in tasks:
        for year, value in (task.get("cost", {}).get("annual_kusd") or {}).items():
            annual_cost[year] = annual_cost.get(year, 0.0) + float(value)
        for year, value in (task.get("cost", {}).get("annual_labor_kusd") or {}).items():
            annual_labor[year] = annual_labor.get(year, 0.0) + float(value)
        for year, value in (task.get("cost", {}).get("annual_non_labor_kusd") or {}).items():
            annual_non_labor[year] = annual_non_labor.get(year, 0.0) + float(value)
    for row in assignments:
        for year, value in (row.get("annual_fte_years") or {}).items():
            annual_fte[year] = annual_fte.get(year, 0.0) + float(value)

    milestones = _route_milestones(route_raw, profile, options)
    selected_power_meta = copy.deepcopy(database["pathways"][options.power_reactor_path])
    selected_demo_meta = copy.deepcopy(database["pathways"][DEMONSTRATOR_PATH])

    commercial_route_total_kusd = power_cost["total_kusd"] + (part57_overlay_cost["total_kusd"] if fallback_ids else 0.0)

    summary = {
        "demonstrator_path": DEMONSTRATOR_PATH,
        "demonstrator_variant": options.demonstrator_variant,
        "power_reactor_path": options.power_reactor_path,
        "power_reactor_variant": options.power_reactor_variant,
        "effective_executable_power_path": profile["effective_path"],
        "effective_executable_power_variant": profile["effective_variant"],
        "part57_mode": options.part57_mode if options.power_reactor_path == "part57" else "not_selected",
        "part57_fallback_path": options.part57_fallback_path if options.power_reactor_path == "part57" and options.part57_mode == "current_with_fallback" else None,
        "part57_fallback_variant": options.part57_fallback_variant if options.power_reactor_path == "part57" and options.part57_mode == "current_with_fallback" else None,
        "active_task_count": len(tasks),
        "route_specific_task_count": len(route_raw),
        "demo_route_task_count": len(demo_ids),
        "power_route_task_count": len(effective_ids),
        "commercial_route_task_count": len(route_ids),
        "part57_readiness_task_count": len(part57_readiness_ids),
        "fallback_route_task_count": len(fallback_ids),
        "assignment_count": len(assignments),
        "fte_years": fte_years,
        "labor_cost_kusd": labor_total,
        "non_labor_cost_kusd": non_labor_total,
        "total_cost_kusd": labor_total + non_labor_total,
        "common_program_cost_kusd": common_cost["total_kusd"],
        "demo_route_cost_kusd": demo_cost["total_kusd"],
        "power_route_cost_kusd": power_cost["total_kusd"],
        "part57_readiness_overlay_cost_kusd": part57_overlay_cost["total_kusd"],
        "fallback_route_cost_kusd": fallback_cost["total_kusd"],
        "commercial_route_total_kusd": commercial_route_total_kusd,
        "route_specific_cost_kusd": demo_cost["total_kusd"] + commercial_route_total_kusd,
        "estimated_repeat_power_route_cost_kusd": power_cost["repeat_route_cost_kusd"],
        "planning_start": "2026-10-01",
        "demonstrator_authorization_complete_target": "2028-12-31",
        "demonstrator_mechanical_completion_target": "2028-12-31",
        "demonstrator_operations_start_target": "2029-01-01",
        "demonstrator_operations_complete_target": "2029-12-31",
        "power_construction_start_date": iso(profile["construction_start_date"]),
        "power_application_date": iso(profile["application_date"]),
        "power_construction_authorization_date": iso(profile["construction_authorization_date"]),
        "power_mechanical_completion_date": iso(profile["mechanical_completion_date"]),
        "power_operation_authorization_date": iso(profile["operation_authorization_date"]),
        "power_initial_criticality_date": iso(profile["initial_criticality_date"]),
        "power_commercial_operation_date": iso(profile["commercial_operation_date"]),
        "power_optimized_reference_date": iso(profile["optimized_reference_date"]),
        "formal_review_cycles": profile["review_cycles"],
        "construction_shift_months": profile["construction_shift_months"],
    }

    return {
        "meta": {
            "scenario_generated": datetime.now().astimezone().isoformat(timespec="seconds"),
            "database_version": database.get("meta", {}).get("version"),
            "options": asdict(options),
        },
        "project": copy.deepcopy(database["project"]),
        "planning_profile": copy.deepcopy(database.get("planning_profile") or {}),
        "pathways": {"demonstrator": selected_demo_meta, "power_reactor": selected_power_meta},
        "summary": summary,
        "schedule_profile": {key: iso(value) if isinstance(value, date) else value for key, value in profile.items()},
        "tasks": sorted(tasks, key=lambda task: (task["schedule"]["start"], str(task.get("stream_id") or ""), task["id"])),
        "resource_assignments": assignments,
        "resource_roles": copy.deepcopy(database["resources"]["roles"]),
        "annual_cost_kusd": {year: round(value, 6) for year, value in sorted(annual_cost.items())},
        "annual_labor_kusd": {year: round(value, 6) for year, value in sorted(annual_labor.items())},
        "annual_non_labor_kusd": {year: round(value, 6) for year, value in sorted(annual_non_labor.items())},
        "annual_fte_years": {year: round(value, 6) for year, value in sorted(annual_fte.items())},
        "milestones": milestones,
        "risks": [copy.deepcopy(risk) for risk in database.get("risks", []) if not risk.get("pathway") or risk.get("pathway") in {DEMONSTRATOR_PATH, options.power_reactor_path, profile["effective_path"]}],
        "design_review_gates": copy.deepcopy(database.get("design_review_gates") or []),
        "leadership_governance": copy.deepcopy(database.get("leadership_governance") or []),
        "raci": copy.deepcopy(database.get("raci") or []),
        "test_matrices": copy.deepcopy(database.get("test_matrices") or {}),
        "implementation_playbooks": copy.deepcopy(database.get("implementation_playbooks") or {}),
        "fuel_supply_plan": copy.deepcopy(database.get("fuel_supply_plan") or {}),
        "chemistry_processing_plan": copy.deepcopy(database.get("chemistry_processing_plan") or {}),
        "regulatory_crosswalk": copy.deepcopy(database.get("regulatory_crosswalk") or []),
        "sources": copy.deepcopy(database.get("sources") or []),
    }


def compare_pathways(database: dict[str, Any], *, include_part57_hypothetical: bool = True) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    variants = {
        "part50": list(pathway_variants(database, "part50")),
        "part52": list(pathway_variants(database, "part52")),
        "part53": list(pathway_variants(database, "part53")),
    }
    for path, path_variants in variants.items():
        for variant in path_variants:
            scenario = build_scenario(database, ScenarioOptions(power_reactor_path=path, power_reactor_variant=variant))
            summary = scenario["summary"]
            rows.append({
                "Path": PATH_DISPLAY_NAMES[path],
                "Path Key": path,
                "Variant": database["pathways"][path]["variants"][variant]["label"],
                "Variant Key": variant,
                "Regulatory Status": database["pathways"][path]["status"],
                "Executable": True,
                "Formal Review Cycles": summary["formal_review_cycles"],
                "Route Activities": summary["commercial_route_task_count"],
                "Power Route Cost ($000)": summary["power_route_cost_kusd"],
                "Part 57 Readiness Component ($000)": 0.0,
                "Commercial Route Total ($000)": summary["commercial_route_total_kusd"],
                "Total Program Cost ($000)": summary["total_cost_kusd"],
                "Repeat Power Route Cost ($000)": summary["estimated_repeat_power_route_cost_kusd"],
                "Application": summary["power_application_date"],
                "Construction Authorization": summary["power_construction_authorization_date"],
                "Mechanical Completion": summary["power_mechanical_completion_date"],
                "Operation Authorization": summary["power_operation_authorization_date"],
                "Commercial Operation": summary["power_commercial_operation_date"],
            })
    # Current Part 57 always includes a complete fallback; show each fallback as
    # a distinct executable planning case.
    for fallback in EXECUTABLE_POWER_PATHS:
        fallback_variant = default_variant(database, fallback)
        scenario = build_scenario(
            database,
            ScenarioOptions(
                power_reactor_path="part57",
                power_reactor_variant="foak_standardized",
                part57_mode="current_with_fallback",
                part57_fallback_path=fallback,
                part57_fallback_variant=fallback_variant,
            ),
        )
        summary = scenario["summary"]
        rows.append({
            "Path": "Proposed Part 57 readiness",
            "Path Key": "part57",
            "Variant": f"Current readiness + {PATH_DISPLAY_NAMES[fallback]} fallback",
            "Variant Key": f"current_{fallback}_{fallback_variant}",
            "Regulatory Status": "Proposed; fallback is executable",
            "Executable": True,
            "Formal Review Cycles": summary["formal_review_cycles"],
            "Route Activities": summary["commercial_route_task_count"],
            "Power Route Cost ($000)": summary["power_route_cost_kusd"],
            "Part 57 Readiness Component ($000)": summary["part57_readiness_overlay_cost_kusd"],
            "Commercial Route Total ($000)": summary["commercial_route_total_kusd"],
            "Total Program Cost ($000)": summary["total_cost_kusd"],
            "Repeat Power Route Cost ($000)": summary["estimated_repeat_power_route_cost_kusd"],
            "Application": summary["power_application_date"],
            "Construction Authorization": summary["power_construction_authorization_date"],
            "Mechanical Completion": summary["power_mechanical_completion_date"],
            "Operation Authorization": summary["power_operation_authorization_date"],
            "Commercial Operation": summary["power_commercial_operation_date"],
        })
    if include_part57_hypothetical:
        for variant in pathway_variants(database, "part57"):
            scenario = build_scenario(
                database,
                ScenarioOptions(
                    power_reactor_path="part57",
                    power_reactor_variant=variant,
                    part57_mode="hypothetical_final_rule",
                ),
            )
            summary = scenario["summary"]
            rows.append({
                "Path": "Proposed Part 57",
                "Path Key": "part57",
                "Variant": database["pathways"]["part57"]["variants"][variant]["label"] + " (hypothetical)",
                "Variant Key": f"hypothetical_{variant}",
                "Regulatory Status": "Hypothetical final-rule sensitivity; not executable",
                "Executable": False,
                "Formal Review Cycles": summary["formal_review_cycles"],
                "Route Activities": summary["commercial_route_task_count"],
                "Power Route Cost ($000)": summary["power_route_cost_kusd"],
                "Part 57 Readiness Component ($000)": summary["part57_readiness_overlay_cost_kusd"],
                "Commercial Route Total ($000)": summary["commercial_route_total_kusd"],
                "Total Program Cost ($000)": summary["total_cost_kusd"],
                "Repeat Power Route Cost ($000)": summary["estimated_repeat_power_route_cost_kusd"],
                "Application": summary["power_application_date"],
                "Construction Authorization": summary["power_construction_authorization_date"],
                "Mechanical Completion": summary["power_mechanical_completion_date"],
                "Operation Authorization": summary["power_operation_authorization_date"],
                "Commercial Operation": summary["power_commercial_operation_date"],
            })
    return rows


def route_activity_delta(database: dict[str, Any], path: str, variant: str, *, mode: str | None = None) -> list[dict[str, Any]]:
    """Return the bottom-up route activities without the shared program baseline."""
    if path == "doe_launchpad":
        return _select_module_tasks(database, path, "demonstrator", variant=variant)
    return _select_module_tasks(database, path, "power_reactor", variant=variant, mode=mode)
