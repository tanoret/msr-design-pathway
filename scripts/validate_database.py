#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import networkx as nx
from jsonschema import Draft202012Validator

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import DEFAULT_DATABASE, _load_database_uncached, load_sharded_database
from src.database_sharding import SHARDED_DATABASE_FORMAT
from src.pathway_engine import EXECUTABLE_POWER_PATHS, ScenarioOptions, build_scenario, pathway_variants

PATHWAYS = {"doe_launchpad", "part50", "part52", "part53", "part57"}


def load(path: Path) -> dict[str, Any]:
    if path.name.endswith(".manifest.json"):
        return load_sharded_database(path, verify_semantic_hash=True)
    return _load_database_uncached(path)


def all_module_tasks(database: dict[str, Any]) -> list[dict[str, Any]]:
    return [task for module in database["pathway_modules"].values() for stage in module.values() for task in stage]


def validate(database: dict[str, Any], schema: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    if schema:
        schema_errors = sorted(Draft202012Validator(schema).iter_errors(database), key=lambda item: list(item.absolute_path))
        errors.extend(f"Schema {'/'.join(map(str, item.absolute_path))}: {item.message}" for item in schema_errors[:20])

    required = {
        "meta", "project", "pathways", "pathway_modules", "tasks", "resources", "financials",
        "milestones", "risks", "design_review_gates", "test_matrices", "sources", "data_quality",
        "licensing_path_table", "route_cost_model",
    }
    missing = sorted(required.difference(database))
    if missing:
        errors.append(f"Missing top-level keys: {', '.join(missing)}")
    if database.get("project", {}).get("name") != "Project-MSR":
        errors.append("Project name is not Project-MSR.")
    missing_paths = sorted(PATHWAYS.difference(database.get("pathways", {})))
    if missing_paths:
        errors.append(f"Missing pathways: {', '.join(missing_paths)}")

    tasks = database.get("tasks") or []
    module_tasks = all_module_tasks(database)
    ids = [str(task.get("id")) for task in tasks + module_tasks]
    if len(ids) != len(set(ids)):
        errors.append("Base and route-module task IDs are not unique.")
    role_ids = {str(role.get("role_id")) for role in database.get("resources", {}).get("roles") or []}
    if not {"CNO", "CTO"}.issubset(role_ids):
        errors.append("CNO and/or CTO is missing from the resource model.")

    for task in tasks + module_tasks:
        execution = task.get("execution") or {}
        for field in ["purpose", "required_inputs", "work_steps", "tools_and_methods", "deliverables_and_records", "acceptance_exit_criteria", "minimum_technical_content"]:
            if not execution.get(field):
                errors.append(f"Task {task.get('id')} has incomplete execution field {field}.")
                break
        for assignment in task.get("resources", {}).get("assignments") or []:
            if str(assignment.get("role_id")) not in role_ids:
                errors.append(f"Route assignment {assignment.get('assignment_id')} references an unknown role.")
                break

    base_ids = {task["id"] for task in tasks}
    for assignment in database.get("resources", {}).get("assignments") or []:
        if assignment.get("task_id") not in base_ids:
            errors.append(f"Base assignment {assignment.get('assignment_id')} references an unknown task.")
            break

    budget = database.get("financials", {}).get("demonstrator_direct_budget") or []
    package_total = sum(float(row.get("Direct Non-Labor ($000)") or 0.0) for row in budget if row.get("WBS ID") != "TOTAL")
    if abs(package_total - 30_000.0) > 0.01:
        errors.append(f"Demonstrator direct package totals {package_total:,.3f}, not 30,000 ($000).")

    forbidden_blob = json.dumps(database).lower()
    for token in ["fission" + "aire", "weinberg" + "-1", "w1" + " plan", "foak" + " plan"]:
        if token in forbidden_blob:
            errors.append(f"Public-release token remains: {token}")

    scenarios: list[ScenarioOptions] = []
    for path in ["part50", "part52", "part53"]:
        for variant in pathway_variants(database, path):
            scenarios.append(ScenarioOptions(power_reactor_path=path, power_reactor_variant=variant))
    for fallback in EXECUTABLE_POWER_PATHS:
        scenarios.append(
            ScenarioOptions(
                power_reactor_path="part57",
                power_reactor_variant="foak_standardized",
                part57_mode="current_with_fallback",
                part57_fallback_path=fallback,
                part57_fallback_variant=next(iter(pathway_variants(database, fallback))),
            )
        )
    for variant in pathway_variants(database, "part57"):
        scenarios.append(ScenarioOptions(power_reactor_path="part57", power_reactor_variant=variant, part57_mode="hypothetical_final_rule"))

    for options in scenarios:
        try:
            scenario = build_scenario(database, options)
        except Exception as exc:  # noqa: BLE001 - validation should report any scenario failure
            errors.append(f"Scenario build failed for {options}: {exc}")
            continue
        scenario_ids = [task["id"] for task in scenario["tasks"]]
        graph = nx.DiGraph()
        graph.add_nodes_from(scenario_ids)
        for task in scenario["tasks"]:
            graph.add_edges_from((pred, task["id"]) for pred in task["schedule"].get("predecessors", []))
        if not nx.is_directed_acyclic_graph(graph):
            errors.append(f"Scenario dependency cycle for {options}")
        if scenario["summary"]["demonstrator_mechanical_completion_target"] != "2028-12-31":
            errors.append(f"Demonstrator target changed for {options}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Project-MSR planning database and all pathway scenarios.")
    parser.add_argument("database", nargs="?", default=DEFAULT_DATABASE, type=Path)
    parser.add_argument("--schema", default=PROJECT_ROOT / "data" / "project_msr_database.schema.json", type=Path)
    args = parser.parse_args()
    database = load(args.database)
    schema = json.loads(args.schema.read_text(encoding="utf-8")) if args.schema.exists() else None
    errors = validate(database, schema)
    if args.database.name.endswith(".manifest.json"):
        manifest = json.loads(args.database.read_text(encoding="utf-8"))
        if manifest.get("format") != SHARDED_DATABASE_FORMAT:
            errors.append("Unrecognized sharded database manifest format.")
    if errors:
        print("Database validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    route_tasks = len(all_module_tasks(database))
    print(
        "Database validation passed: "
        f"{len(database['tasks']):,} shared tasks, "
        f"{route_tasks:,} route tasks, "
        f"{len(database['resources']['assignments']):,} shared assignments, "
        f"{len(database['resources']['roles']):,} roles."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
