from __future__ import annotations

from src.components import dependency_graph_figure, extract_selected_task_id, route_graph_figure
from src.pathway_engine import ScenarioOptions, build_scenario


def test_dependency_graph_is_self_contained_plotly_figure(database: dict) -> None:
    scenario = build_scenario(database, ScenarioOptions())
    center = scenario["tasks"][150]["id"]
    figure, node_count = dependency_graph_figure(scenario["tasks"], center_id=center, depth=2, max_nodes=100)
    assert 1 <= node_count <= 100
    assert len(figure.data) >= 2
    assert figure.layout.showlegend is False
    task_trace = figure.data[1]
    assert task_trace.customdata
    assert any(str(row[0]) == center for row in task_trace.customdata)


def test_route_graph_exposes_task_ids_for_click_selection(database: dict) -> None:
    scenario = build_scenario(database, ScenarioOptions(power_reactor_path="part52", power_reactor_variant="straight_col"))
    route_tasks = [task for task in scenario["tasks"] if task.get("pathway_specific")]
    figure = route_graph_figure(route_tasks, selected_id=route_tasks[0]["id"])
    task_trace = figure.data[1]
    selected = str(task_trace.customdata[0][0])
    event = {"selection": {"points": [{"customdata": [selected, "Task"]}]}}
    assert extract_selected_task_id(event) == selected


def test_route_graph_uses_compact_readable_nodes_and_modern_layout(database: dict) -> None:
    scenario = build_scenario(database, ScenarioOptions(power_reactor_path="part53", power_reactor_variant="col"))
    route_tasks = [task for task in scenario["tasks"] if task.get("pathway_specific")]
    figure = route_graph_figure(route_tasks, selected_id=route_tasks[0]["id"])
    node_trace = figure.data[1]
    assert max(len(str(label).replace("<br>", "")) for label in node_trace.text) <= 20
    assert all("<br>" in str(label) or len(str(label)) <= 14 for label in node_trace.text)
    assert figure.layout.plot_bgcolor == "#ffffff" or figure.layout.plot_bgcolor == "#f8fafc"
    assert figure.layout.hoverlabel.bgcolor == "#ffffff"
    assert figure.layout.height >= 720
