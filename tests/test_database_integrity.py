from __future__ import annotations

from jsonschema import Draft202012Validator
import pytest


def all_module_tasks(database: dict) -> list[dict]:
    return [
        task
        for module in database["pathway_modules"].values()
        for stage_tasks in module.values()
        for task in stage_tasks
    ]


def test_database_matches_schema(database: dict, schema: dict) -> None:
    errors = sorted(Draft202012Validator(schema).iter_errors(database), key=lambda error: list(error.absolute_path))
    assert not errors, "\n".join(f"{'/'.join(map(str, error.absolute_path))}: {error.message}" for error in errors[:20])


def test_project_identity_and_paths(database: dict) -> None:
    assert database["project"]["name"] == "Project-MSR"
    assert database["meta"]["public_release"] is False
    assert set(database["pathways"]) == {"doe_launchpad", "part50", "part52", "part53", "part57"}
    assert "not currently available" in database["pathways"]["part57"]["status"].lower()
    assert database["pathways"]["doe_launchpad"]["supported_stages"] == ["demonstrator"]
    for path in ["part50", "part52", "part53", "part57"]:
        assert database["pathways"][path]["supported_stages"] == ["power_reactor"]


def test_task_and_module_ids_are_unique(database: dict) -> None:
    tasks = database["tasks"] + all_module_tasks(database)
    ids = [task["id"] for task in tasks]
    assert len(ids) == len(set(ids))
    assert all(task_id.startswith(("S-", "D-", "P-", "P50-", "P52-", "P53-", "P57-")) for task_id in ids)


def test_every_base_and_pathway_task_has_detailed_execution_content(database: dict) -> None:
    required_fields = [
        "purpose",
        "required_inputs",
        "work_steps",
        "tools_and_methods",
        "deliverables_and_records",
        "acceptance_exit_criteria",
        "minimum_technical_content",
        "core_producing_team",
        "review_approval_only",
    ]
    for task in database["tasks"] + all_module_tasks(database):
        assert task.get("description"), task["id"]
        assert task.get("schedule"), task["id"]
        assert task.get("cost"), task["id"]
        assert task.get("resources"), task["id"]
        assert task.get("governance"), task["id"]
        for field in required_fields:
            assert task["execution"].get(field), f"{task['id']} missing {field}"


def test_resource_model_integrity(database: dict) -> None:
    task_ids = {task["id"] for task in database["tasks"]}
    role_ids = {role["role_id"] for role in database["resources"]["roles"]}
    assignment_ids = [row["assignment_id"] for row in database["resources"]["assignments"]]
    assert {"CNO", "CTO"}.issubset(role_ids)
    assert len(assignment_ids) == len(set(assignment_ids))
    assert all(row["task_id"] in task_ids for row in database["resources"]["assignments"])
    assert all(row["role_id"] in role_ids for row in database["resources"]["assignments"])
    assert all(
        allocation["role_id"] in role_ids
        for task in all_module_tasks(database)
        for allocation in task.get("resources", {}).get("assignments", [])
    )


def test_direct_demonstrator_package_is_exactly_30m(database: dict) -> None:
    budget = database["financials"]["demonstrator_direct_budget"]
    package_total = sum(float(row["Direct Non-Labor ($000)"]) for row in budget if row["WBS ID"] != "TOTAL")
    total_row = next(row for row in budget if row["WBS ID"] == "TOTAL")
    assert package_total == 30_000.0
    assert float(total_row["Direct Non-Labor ($000)"]) == 30_000.0


def test_data_quality_counts_reconcile(database: dict) -> None:
    quality = database["data_quality"]
    assert quality["base_task_count"] == len(database["tasks"])
    assert quality["base_assignment_count"] == len(database["resources"]["assignments"])
    assert quality["role_count"] == len(database["resources"]["roles"])
    assert quality["route_task_count"] == len(all_module_tasks(database))


def test_project_identity_scan(database: dict) -> None:
    import json

    blob = json.dumps(database).lower()
    for forbidden in ["fission" + "aire", "weinberg" + "-1", "w1" + " plan", "foak" + " plan"]:
        assert forbidden not in blob


def test_every_task_has_engineering_ready_work_package(database: dict) -> None:
    required = {
        "engineering_readiness_level", "primary_domain", "work_pattern", "scope_statement", "objective",
        "entry_criteria", "controlled_inputs", "execution_procedure", "requirements_and_guidance",
        "toolchain", "deliverable_register", "verification_and_validation", "interfaces",
        "risks_and_controls", "quality_records", "definition_of_done", "resource_plan", "execution_controls",
    }
    tasks = database["tasks"] + all_module_tasks(database)
    assert database["meta"]["version"] == "4.2.0"
    assert database["data_quality"]["engineering_ready_task_count"] == len(tasks)
    for task in tasks:
        package = task.get("engineering_work_package") or {}
        assert required.issubset(package), task["id"]
        assert len(package["scope_statement"]) >= 100, task["id"]
        assert len(package["controlled_inputs"]) >= 2, task["id"]
        assert len(package["execution_procedure"]) >= 5, task["id"]
        assert package["toolchain"], task["id"]
        assert package["deliverable_register"], task["id"]
        assert len(package["verification_and_validation"]) >= 4, task["id"]
        assert package["risks_and_controls"], task["id"]
        assert len(package["definition_of_done"]) >= 5, task["id"]
        assert task["execution"]["engineering_ready"] is True
        assert task["execution"]["detail_level"] == "engineering_ready_v4"


def test_internal_display_has_no_warning_payloads_or_cno_led_commentary(database: dict) -> None:
    import json

    blob = json.dumps(database).lower()
    assert '"warnings"' not in blob
    assert '"availability_note"' not in blob
    assert "cno-led" not in blob
    assert "cno led" not in blob


def test_every_task_has_reconciled_bottom_up_cost_basis(database: dict) -> None:
    tasks = database["tasks"] + all_module_tasks(database)
    required = {
        "basis_of_estimate_id", "estimate_class", "estimate_method", "estimate_currency_year",
        "planned_fte_years", "planned_labor_hours", "labor_effort_breakdown",
        "direct_non_labor_before_risk_kusd", "risk_allowance_kusd", "cost_components",
        "low_kusd", "high_kusd", "prior_estimate", "estimate_change", "cost_drivers",
        "exclusions_and_double_counting_controls", "reestimate_triggers",
    }
    for task in tasks:
        cost = task.get("cost") or {}
        assert required.issubset(cost), task["id"]
        direct_components = sum(
            float(value or 0.0)
            for key, value in cost["cost_components"].items()
            if key != "risk_allowance_kusd"
        )
        assert direct_components == pytest.approx(float(cost["direct_non_labor_before_risk_kusd"]), abs=0.02), task["id"]
        assert float(cost["non_labor_kusd"]) == pytest.approx(
            float(cost["direct_non_labor_before_risk_kusd"]) + float(cost["risk_allowance_kusd"]), abs=0.02
        ), task["id"]
        assert float(cost["total_kusd"]) == pytest.approx(float(cost["labor_kusd"]) + float(cost["non_labor_kusd"]), abs=0.02), task["id"]
        assert float(cost["low_kusd"]) <= float(cost["total_kusd"]) <= float(cost["high_kusd"]), task["id"]
        assert sum(float(value or 0.0) for value in cost["labor_effort_breakdown"].values()) == pytest.approx(
            float(cost["planned_labor_hours"]), abs=0.2
        ), task["id"]


def test_core_and_reactivity_control_costs_are_material(database: dict) -> None:
    by_id = {task["id"]: task for task in database["tasks"]}
    demo = by_id["D-3.4.c"]["cost"]
    power = by_id["P-3.4.c"]["cost"]
    assert demo["planned_fte_years"] >= 2.5
    assert demo["total_kusd"] >= 1_000.0
    assert power["planned_fte_years"] >= 10.0
    assert power["total_kusd"] >= 3_500.0
    assert power["fully_burdened_task_view_kusd"] >= 5_000.0


def test_non_additive_package_allocations_reconcile(database: dict) -> None:
    by_id = {task["id"]: task for task in database["tasks"]}
    for source_id in ["P-PKG-01", "S-PKG-01", "S-PKG-05"]:
        source = by_id[source_id]["cost"]
        allocation = source["allocation_view"]
        allocated = sum(
            float(row.get("allocated_kusd") or 0.0)
            for task in database["tasks"]
            for row in task["cost"].get("allocated_program_package_sources", [])
            if row.get("source_task_id") == source_id
        )
        assert allocated == pytest.approx(float(allocation["allocated_to_detailed_tasks_kusd"]), abs=0.05)
        assert allocation["non_additive_display_allocation"] is True
    assert sum(float(task["cost"]["total_kusd"]) for task in database["tasks"]) == pytest.approx(
        float(database["route_cost_model"]["common_program_cost_kusd"]), abs=0.1
    )


def test_route_fee_double_count_is_removed_from_common_package(database: dict) -> None:
    task = next(task for task in database["tasks"] if task["id"] == "P-PKG-08")
    assert task["name"] == "Independent Licensing Review and Application Assurance"
    assert float(task["cost"]["cost_components"]["regulatory_review_fees_kusd"]) == 0.0
    assert "selected licensing-path module" in task["description"].lower()


def test_task_cost_audit_metadata_is_complete(database: dict) -> None:
    assert database["meta"]["cost_estimate_version"] == "4.2.0"
    assert database["data_quality"]["costed_task_count"] == len(database["tasks"]) + len(all_module_tasks(database))
    assert database["financials"]["task_cost_reestimate_v4_2"]["costed_activity_count"] == len(database["tasks"])
