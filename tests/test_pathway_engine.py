from __future__ import annotations

import networkx as nx
import pytest

from src.pathway_engine import (
    EXECUTABLE_POWER_PATHS,
    ScenarioOptions,
    build_scenario,
    compare_pathways,
    pathway_variants,
)


def assert_valid_scenario(scenario: dict) -> None:
    task_ids = [task["id"] for task in scenario["tasks"]]
    assignment_ids = [row["assignment_id"] for row in scenario["resource_assignments"]]
    assert len(task_ids) == len(set(task_ids))
    assert len(assignment_ids) == len(set(assignment_ids))
    assert scenario["summary"]["active_task_count"] == len(task_ids)
    assert scenario["summary"]["assignment_count"] == len(assignment_ids)
    assert scenario["summary"]["demonstrator_mechanical_completion_target"] == "2028-12-31"
    task_id_set = set(task_ids)
    assert all(
        predecessor in task_id_set
        for task in scenario["tasks"]
        for predecessor in task["schedule"].get("predecessors", [])
    )
    graph = nx.DiGraph()
    graph.add_nodes_from(task_ids)
    for task in scenario["tasks"]:
        graph.add_edges_from((predecessor, task["id"]) for predecessor in task["schedule"].get("predecessors", []))
    assert nx.is_directed_acyclic_graph(graph)


@pytest.mark.parametrize(
    ("path", "variant", "expected_id"),
    [
        ("part50", "cp_ol", "P50-18"),
        ("part50", "cp_ol_lwa", "P50-08"),
        ("part52", "straight_col", "P52-15"),
        ("part52", "esp_col", "P52-E02"),
        ("part52", "dc_col", "P52-D03"),
        ("part52", "esp_dc_col", "P52-E02"),
        ("part53", "col", "P53-C02"),
        ("part53", "cp_ol", "P53-P03"),
    ],
)
def test_each_executable_product_stack_builds_distinct_scenario(database: dict, path: str, variant: str, expected_id: str) -> None:
    scenario = build_scenario(database, ScenarioOptions(power_reactor_path=path, power_reactor_variant=variant))
    assert_valid_scenario(scenario)
    task_ids = {task["id"] for task in scenario["tasks"]}
    assert "D-LP2-12" in task_ids
    assert expected_id in task_ids
    assert scenario["summary"]["power_reactor_path"] == path
    assert scenario["summary"]["power_reactor_variant"] == variant


def test_doe_launchpad_is_demonstrator_only(database: dict) -> None:
    scenario = build_scenario(database, ScenarioOptions(power_reactor_path="part50", power_reactor_variant="cp_ol"))
    demo_route_tasks = [task for task in scenario["tasks"] if task.get("pathway_specific") and task.get("concept") == "Demonstrator"]
    power_route_tasks = [task for task in scenario["tasks"] if task.get("pathway_specific") and task.get("concept") == "Power Reactor"]
    assert demo_route_tasks
    assert all(task["id"].startswith("D-LP2-") for task in demo_route_tasks)
    assert all(not task["id"].startswith("D-LP2-") for task in power_route_tasks)
    assert all("doe_launchpad" in task.get("pathway_applicability", []) for task in demo_route_tasks)


@pytest.mark.parametrize("fallback", EXECUTABLE_POWER_PATHS)
def test_current_part57_contains_full_executable_fallback(database: dict, fallback: str) -> None:
    fallback_variant = next(iter(pathway_variants(database, fallback)))
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
    assert_valid_scenario(scenario)
    ids = {task["id"] for task in scenario["tasks"]}
    assert "P57-R05" in ids
    assert any(task_id.startswith({"part50": "P50-", "part52": "P52-", "part53": "P53-"}[fallback]) for task_id in ids)
    assert scenario["summary"]["part57_readiness_overlay_cost_kusd"] > 0
    assert scenario["summary"]["fallback_route_cost_kusd"] > 0
    assert scenario["summary"]["commercial_route_total_kusd"] == pytest.approx(
        scenario["summary"]["power_route_cost_kusd"] + scenario["summary"]["part57_readiness_overlay_cost_kusd"]
    )
    assert scenario["summary"]["effective_executable_power_path"] == fallback
    assert "warnings" not in scenario


def test_hypothetical_part57_is_explicitly_nonbaseline(database: dict) -> None:
    scenario = build_scenario(
        database,
        ScenarioOptions(
            power_reactor_path="part57",
            power_reactor_variant="manufacturing_high_volume",
            part57_mode="hypothetical_final_rule",
        ),
    )
    assert_valid_scenario(scenario)
    ids = {task["id"] for task in scenario["tasks"]}
    assert "P57-H04" in ids
    assert not any(task_id.startswith("P50-") or task_id.startswith("P52-") or task_id.startswith("P53-") for task_id in ids)
    assert scenario["summary"]["commercial_route_total_kusd"] == pytest.approx(scenario["summary"]["power_route_cost_kusd"])
    assert "warnings" not in scenario


def test_path_costs_show_material_product_stack_differences(database: dict) -> None:
    rows = compare_pathways(database)
    by_key = {(row["Path Key"], row["Variant Key"]): row for row in rows}
    p50 = by_key[("part50", "cp_ol")]["Commercial Route Total ($000)"]
    p52_straight = by_key[("part52", "straight_col")]["Commercial Route Total ($000)"]
    p52_full = by_key[("part52", "esp_dc_col")]["Commercial Route Total ($000)"]
    p53 = by_key[("part53", "col")]["Commercial Route Total ($000)"]
    assert p52_full - p50 > 75_000
    assert p52_straight > p50
    assert p53 > p50
    assert max(row["Commercial Route Total ($000)"] for row in rows if row["Executable"]) - min(
        row["Commercial Route Total ($000)"] for row in rows if row["Executable"]
    ) > 75_000
    part57 = by_key[("part57", "current_part53_col")]
    assert part57["Route Activities"] == 23
    assert part57["Commercial Route Total ($000)"] == pytest.approx(
        part57["Power Route Cost ($000)"] + part57["Part 57 Readiness Component ($000)"]
    )


def test_route_milestones_are_product_specific(database: dict) -> None:
    p50 = build_scenario(database, ScenarioOptions(power_reactor_path="part50", power_reactor_variant="cp_ol"))
    p52 = build_scenario(database, ScenarioOptions(power_reactor_path="part52", power_reactor_variant="straight_col"))
    p53 = build_scenario(database, ScenarioOptions(power_reactor_path="part53", power_reactor_variant="col"))
    labels50 = " | ".join(row["Milestone / Decision Gate"].lower() for row in p50["milestones"])
    labels52 = " | ".join(row["Milestone / Decision Gate"].lower() for row in p52["milestones"])
    labels53 = " | ".join(row["Milestone / Decision Gate"].lower() for row in p53["milestones"])
    assert "construction permit" in labels50 and "operating license" in labels50
    assert "combined license" in labels52 and "52.103(g)" in labels52
    assert "part 53 combined license" in labels53 and "readiness" in labels53
    assert all("doe launch pad" in " | ".join(row["Milestone / Decision Gate"].lower() for row in scenario["milestones"]) for scenario in [p50, p52, p53])


def test_commercial_schedule_retains_common_2035_target_and_path_specific_front_end(database: dict) -> None:
    p50 = build_scenario(database, ScenarioOptions(power_reactor_path="part50", power_reactor_variant="cp_ol"))["summary"]
    p52 = build_scenario(database, ScenarioOptions(power_reactor_path="part52", power_reactor_variant="esp_dc_col"))["summary"]
    p53 = build_scenario(database, ScenarioOptions(power_reactor_path="part53", power_reactor_variant="col"))["summary"]
    for summary in (p50, p52, p53):
        assert summary["power_construction_start_date"] == "2030-01-01"
        assert summary["power_commercial_operation_date"] == "2035-12-31"
    assert len({p50["power_application_date"], p52["power_application_date"], p53["power_application_date"]}) >= 2
    assert p50["formal_review_cycles"] == 2
    assert p52["formal_review_cycles"] == 3


def test_annual_profiles_reconcile_with_scenario_totals(database: dict) -> None:
    scenario = build_scenario(database, ScenarioOptions())
    for task in scenario["tasks"]:
        annual = sum(float(value or 0.0) for value in task["cost"].get("annual_kusd", {}).values())
        assert annual == pytest.approx(float(task["cost"]["total_kusd"]), abs=0.02)
    for assignment in scenario["resource_assignments"]:
        annual_fte = sum(float(value or 0.0) for value in assignment.get("annual_fte_years", {}).values())
        assert annual_fte == pytest.approx(float(assignment["fte_years"]), abs=0.02)
    assert sum(scenario["annual_cost_kusd"].values()) == pytest.approx(scenario["summary"]["total_cost_kusd"], abs=0.1)
    assert sum(scenario["annual_fte_years"].values()) == pytest.approx(scenario["summary"]["fte_years"], abs=0.1)


def test_cno_and_cto_remain_in_active_resource_model(database: dict) -> None:
    scenario = build_scenario(database, ScenarioOptions())
    role_ids = {row["role_id"] for row in scenario["resource_assignments"]}
    assert {"CNO", "CTO"}.issubset(role_ids)


def test_resource_and_funding_peaks_are_in_commercial_execution_window(database: dict) -> None:
    for path in ["part50", "part52", "part53"]:
        for variant in pathway_variants(database, path):
            scenario = build_scenario(database, ScenarioOptions(power_reactor_path=path, power_reactor_variant=variant))
            peak_fte_year = max(scenario["annual_fte_years"], key=scenario["annual_fte_years"].get)
            peak_cost_year = max(scenario["annual_cost_kusd"], key=scenario["annual_cost_kusd"].get)
            assert 2031 <= int(peak_fte_year) <= 2033
            assert 2031 <= int(peak_cost_year) <= 2033
            assert scenario["annual_fte_years"]["2027"] < scenario["annual_fte_years"][peak_fte_year]
            assert scenario["annual_cost_kusd"]["2028"] < scenario["annual_cost_kusd"][peak_cost_year]


def test_default_resource_profile_ramps_without_a_post_peak_cliff(database: dict) -> None:
    scenario = build_scenario(database, ScenarioOptions())
    annual = scenario["annual_fte_years"]
    assert annual["2026"] < annual["2027"] < annual["2031"] < annual["2032"]
    assert annual["2028"] < annual["2029"]
    assert annual["2027"] <= 1.05 * annual["2029"]
    assert annual["2033"] >= 0.62 * annual["2032"]
    assert annual["2034"] >= 0.45 * annual["2032"]
    assert annual["2035"] >= 20.0
