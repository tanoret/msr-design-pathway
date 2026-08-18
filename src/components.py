from __future__ import annotations

import html
import json
import textwrap
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

import networkx as nx
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
THEME_PATH = PROJECT_ROOT / "assets" / "theme.css"

ROUTE_COLORS = {
    "doe_launchpad": "#0f9f8f",
    "part50": "#315efb",
    "part52": "#7c3aed",
    "part53": "#e76f51",
    "part57": "#64748b",
}
STREAM_COLORS = {
    "0": "#64748b",
    "1": "#315efb",
    "2": "#0f9f8f",
    "3": "#7c3aed",
    "4": "#e76f51",
    "5": "#2f80ed",
    "6": "#c47b23",
}
DOMAIN_COLORS = {
    "licensing_authorization": "#315efb",
    "analysis_model": "#7c3aed",
    "test_experiment": "#0f9f8f",
    "design_engineering": "#2f80ed",
    "procurement_fabrication": "#c47b23",
    "construction_installation": "#e76f51",
    "operations_program": "#15936f",
    "management_control": "#64748b",
}

CHART_COLORS = [
    "#315efb", "#0f9f8f", "#7c3aed", "#e76f51", "#c47b23",
    "#15936f", "#2f80ed", "#64748b", "#d1495b", "#4f7cac",
]

PLOTLY_CONFIG = {
    "displaylogo": False,
    "responsive": True,
    "scrollZoom": False,
    "displayModeBar": "hover",
    "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
    "toImageButtonOptions": {"format": "png", "filename": "project-msr-chart", "height": 1200, "width": 2000, "scale": 2},
}


def apply_page_style() -> None:
    css = THEME_PATH.read_text(encoding="utf-8") if THEME_PATH.exists() else ""
    if css:
        try:
            st.html(css)
        except AttributeError:
            st.markdown(css, unsafe_allow_html=True)


def render_sidebar_brand() -> None:
    st.sidebar.markdown(
        """
        <div class="msr-brand">
          <div class="msr-brand-mark">MSR</div>
          <div><div class="msr-brand-name">Project-MSR</div><div class="msr-brand-sub">Integrated development planner</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero(title: str, subtitle: str, kicker: str = "Integrated engineering and licensing planner", chips: list[str] | None = None) -> None:
    chip_html = "".join(f'<span class="msr-pill">{html.escape(str(chip))}</span>' for chip in (chips or []))
    st.markdown(
        f"""
        <div class="msr-hero">
          <div class="msr-eyebrow">{html.escape(kicker)}</div>
          <div class="msr-title">{html.escape(title)}</div>
          <div class="msr-subtitle">{html.escape(subtitle)}</div>
          {f'<div style="position:relative;z-index:1;margin-top:.75rem">{chip_html}</div>' if chip_html else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title: str, copy: str = "", kicker: str = "") -> None:
    st.markdown(
        f"""
        <div class="msr-section">
          {f'<div class="msr-section-kicker">{html.escape(kicker)}</div>' if kicker else ''}
          <div class="msr-section-title">{html.escape(title)}</div>
          {f'<div class="msr-section-copy">{html.escape(copy)}</div>' if copy else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi(label: str, value: str, note: str = "") -> None:
    st.markdown(
        f"""
        <div class="msr-kpi">
          <div class="msr-kpi-label">{html.escape(label)}</div>
          <div class="msr-kpi-value">{html.escape(value)}</div>
          {f'<div class="msr-kpi-note">{html.escape(note)}</div>' if note else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_money_kusd(value: float | int | None) -> str:
    value = float(value or 0.0)
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:,.2f}B"
    if abs(value) >= 1_000:
        return f"${value / 1_000:,.1f}M"
    return f"${value:,.0f}k"


def format_fte(value: float | int | None) -> str:
    return f"{float(value or 0.0):,.1f}"


def render_note(text: str, kind: str = "note") -> None:
    class_name = "msr-success" if kind == "success" else "msr-note"
    st.markdown(f'<div class="{class_name}">{html.escape(str(text))}</div>', unsafe_allow_html=True)


def render_path_card(title: str, pathway: dict[str, Any], variant_label: str, status_kind: str | None = None) -> None:
    del status_kind
    products = "".join(f'<span class="msr-pill">{html.escape(str(product))}</span>' for product in pathway.get("products") or [])
    st.markdown(
        f"""
        <div class="msr-card">
          <div class="msr-card-title">{html.escape(title)}</div>
          <div style="font-weight:750;color:#203654">{html.escape(pathway.get('label', ''))}</div>
          <div class="msr-card-copy" style="margin-top:.2rem">{html.escape(variant_label)}</div>
          <div class="msr-card-copy" style="margin-top:.55rem">{html.escape(pathway.get('summary', ''))}</div>
          <div style="margin-top:.7rem">{products}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _neighbors_within(graph: nx.DiGraph, center: str, depth: int) -> set[str]:
    selected = {center}
    queue = deque([(center, 0)])
    while queue:
        node, distance = queue.popleft()
        if distance >= depth:
            continue
        for adjacent in set(graph.predecessors(node)).union(graph.successors(node)):
            if adjacent not in selected:
                selected.add(adjacent)
                queue.append((adjacent, distance + 1))
    return selected


def _bounded_nodes(graph: nx.DiGraph, candidates: set[str], center_id: str | None, max_nodes: int) -> set[str]:
    if len(candidates) <= max_nodes:
        return candidates
    undirected = graph.to_undirected()
    ordered: list[str] = []
    if center_id and center_id in candidates:
        ordered.append(center_id)
        ordered.extend(node for node in nx.bfs_tree(undirected, center_id) if node in candidates and node not in ordered)
    for node in sorted(candidates):
        if node not in ordered:
            ordered.append(node)
        if len(ordered) >= max_nodes:
            break
    return set(ordered[:max_nodes])


def _hierarchical_positions(subgraph: nx.DiGraph, task_by_id: dict[str, dict[str, Any]]) -> dict[str, tuple[float, float]]:
    try:
        order = list(nx.topological_sort(subgraph))
    except nx.NetworkXUnfeasible:
        spring = nx.spring_layout(subgraph, seed=42, k=max(0.4, 2.3 / max(len(subgraph), 1) ** 0.5))
        return {node: (float(coords[0]), float(coords[1])) for node, coords in spring.items()}
    levels: dict[str, int] = {}
    for node in order:
        predecessors = list(subgraph.predecessors(node))
        levels[node] = 0 if not predecessors else max(levels[pred] + 1 for pred in predecessors)
    grouped: dict[int, list[str]] = defaultdict(list)
    for node, level in levels.items():
        grouped[level].append(node)
    positions: dict[str, tuple[float, float]] = {}
    for level, nodes in grouped.items():
        nodes.sort(key=lambda node: (
            str(task_by_id[node].get("phase") or ""),
            str(task_by_id[node].get("schedule", {}).get("start") or ""),
            node,
        ))
        spacing = 1.95
        midpoint = (len(nodes) - 1) / 2.0
        for index, node in enumerate(nodes):
            positions[node] = (float(level) * 3.35, float(midpoint - index) * spacing)
    return positions


def _wrap_label(value: str, width: int = 20, max_lines: int = 3) -> str:
    lines = textwrap.wrap(value, width=width)[:max_lines]
    if len(" ".join(lines)) < len(value) and lines:
        lines[-1] = lines[-1].rstrip(" .") + "…"
    return "<br>".join(lines)


def _compact_node_id(value: str) -> str:
    """Format route IDs in two short lines so text stays inside the node."""
    parts = value.split("-")
    if len(parts) >= 3:
        return html.escape("-".join(parts[:-1])) + "<br>" + html.escape(parts[-1])
    if len(value) > 7 and "-" in value:
        left, right = value.rsplit("-", 1)
        return html.escape(left) + "<br>" + html.escape(right)
    return html.escape(value)


def pathway_graph_figure(
    tasks: list[dict[str, Any]],
    *,
    selected_id: str | None = None,
    center_id: str | None = None,
    depth: int = 3,
    max_nodes: int = 180,
    show_names: bool = False,
) -> tuple[go.Figure, int]:
    task_by_id = {str(task["id"]): task for task in tasks}
    graph = nx.DiGraph()
    graph.add_nodes_from(task_by_id)
    for task in tasks:
        target = str(task["id"])
        for predecessor in (task.get("schedule") or {}).get("predecessors") or []:
            predecessor = str(predecessor)
            if predecessor in task_by_id:
                graph.add_edge(predecessor, target)
    if not graph.nodes:
        return go.Figure(), 0
    if center_id and center_id in graph:
        node_ids = _neighbors_within(graph, center_id, depth)
    else:
        node_ids = set(task_by_id)
    node_ids = _bounded_nodes(graph, node_ids, center_id, max_nodes)
    subgraph = graph.subgraph(node_ids).copy()
    positions = _hierarchical_positions(subgraph, task_by_id)

    edge_x: list[float | None] = []
    edge_y: list[float | None] = []
    annotations: list[dict[str, Any]] = []
    for source, target in subgraph.edges:
        x0, y0 = positions[source]
        x1, y1 = positions[target]
        # Stop the line just before the target marker so the arrowhead does not
        # run through the task ID.
        dx, dy = x1 - x0, y1 - y0
        length = max((dx * dx + dy * dy) ** 0.5, 1e-9)
        trim = 0.22
        x_end = x1 - trim * dx / length
        y_end = y1 - trim * dy / length
        edge_x.extend([x0, x_end, None])
        edge_y.extend([y0, y_end, None])
        annotations.append(
            dict(
                x=x_end, y=y_end, ax=x0, ay=y0, xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=2, arrowsize=.72, arrowwidth=1.15,
                arrowcolor="#94a3b8", opacity=.88, standoff=0, startstandoff=0,
            )
        )
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y, mode="lines", line=dict(width=1.15, color="#cbd5e1"),
        hoverinfo="skip", name="Dependencies",
    )

    node_x: list[float] = []
    node_y: list[float] = []
    text: list[str] = []
    hover: list[str] = []
    colors: list[str] = []
    sizes: list[int] = []
    line_colors: list[str] = []
    line_widths: list[int] = []
    customdata: list[list[str]] = []
    selected_points: list[int] = []
    for index, node in enumerate(subgraph.nodes):
        task = task_by_id[node]
        x, y = positions[node]
        ewp = task.get("engineering_work_package") or {}
        pattern = str(ewp.get("work_pattern") or "design_engineering")
        route = str(task.get("pathway_applicability", [""])[0] if task.get("pathway_applicability") else task.get("scenario_route") or "")
        node_x.append(x)
        node_y.append(y)
        label_name = _wrap_label(str(task.get("name") or ""), 22, 2) if show_names else ""
        text.append(f"<b>{_compact_node_id(node)}</b>{'<br>' + label_name if label_name else ''}")
        colors.append(ROUTE_COLORS.get(route, DOMAIN_COLORS.get(pattern, STREAM_COLORS.get(str(task.get("stream_id") or "0"), "#64748b"))))
        is_selected = node == selected_id
        if is_selected:
            selected_points.append(index)
        sizes.append(86 if is_selected else 76)
        line_colors.append("#0f172a" if is_selected else "#ffffff")
        line_widths.append(4 if is_selected else 2.2)
        schedule = task.get("schedule") or {}
        deliverables = (ewp.get("deliverable_register") or [])[:3]
        deliverable_text = "<br>".join(f"• {html.escape(str(item.get('deliverable') or ''))}" for item in deliverables) or "—"
        hover.append(
            f"<b>{html.escape(node)} — {html.escape(str(task.get('name') or ''))}</b><br>"
            f"{html.escape(str(task.get('phase') or ''))}<br>"
            f"{schedule.get('start', '—')} → {schedule.get('finish', '—')}<br>"
            f"Cost: {format_money_kusd((task.get('cost') or {}).get('total_kusd'))}<br>"
            f"FTE-years: {float((task.get('resources') or {}).get('fte_years') or 0):,.2f}<br><br>"
            f"<b>Primary outputs</b><br>{deliverable_text}<extra></extra>"
        )
        customdata.append([node, str(task.get("name") or ""), str(task.get("phase") or ""), pattern])
    node_trace = go.Scatter(
        x=node_x, y=node_y, mode="markers+text", text=text, textposition="middle center",
        textfont=dict(size=10.5, color="#ffffff", family="Inter, Segoe UI, Arial"),
        hovertemplate=hover, customdata=customdata,
        marker=dict(size=sizes, symbol="square", color=colors, line=dict(width=line_widths, color=line_colors), opacity=.98),
        name="Tasks",
    )
    fig = go.Figure([edge_trace, node_trace])
    fig.update_layout(
        height=max(720, min(1280, 500 + len(subgraph) * 16)),
        margin=dict(l=28, r=28, t=34, b=28), showlegend=False,
        plot_bgcolor="#f8fafc", paper_bgcolor="#ffffff",
        xaxis=dict(visible=False, fixedrange=False, automargin=True),
        yaxis=dict(visible=False, fixedrange=False, automargin=True, scaleanchor=None),
        hoverlabel=dict(bgcolor="#ffffff", bordercolor="#cbd5e1", font_size=12, font_color="#0f172a"),
        annotations=annotations, dragmode="pan", clickmode="event+select",
        selectionrevision="route-graph-v4-1", uirevision="route-graph-v4-1",
    )
    return fig, len(subgraph)

def dependency_graph_figure(tasks: list[dict[str, Any]], center_id: str | None = None, depth: int = 2, max_nodes: int = 160) -> tuple[go.Figure, int]:
    return pathway_graph_figure(tasks, selected_id=center_id, center_id=center_id, depth=depth, max_nodes=max_nodes, show_names=False)


def selected_task_from_event(event: Any) -> str | None:
    if event is None:
        return None
    selection = None
    if isinstance(event, dict):
        selection = event.get("selection", event)
    else:
        selection = getattr(event, "selection", None)
        if selection is None:
            try:
                selection = event["selection"]
            except Exception:
                selection = None
    if selection is None:
        return None
    points = selection.get("points") if isinstance(selection, dict) else getattr(selection, "points", None)
    if not points:
        return None
    point = points[0]
    custom = point.get("customdata") if isinstance(point, dict) else getattr(point, "customdata", None)
    if isinstance(custom, (list, tuple)) and custom:
        return str(custom[0])
    if custom:
        return str(custom)
    return None


def _list_markdown(items: list[Any]) -> None:
    if not items:
        st.markdown('<div class="msr-quiet">No items recorded.</div>', unsafe_allow_html=True)
        return
    for item in items:
        st.markdown(f"- {item}")


def _records_frame(records: list[dict[str, Any]], columns: list[str] | None = None) -> pd.DataFrame:
    frame = pd.DataFrame(records or [])
    if frame.empty:
        return frame
    if columns:
        columns = [column for column in columns if column in frame.columns]
        frame = frame[columns]
    frame.columns = [str(column).replace("_", " ").title() for column in frame.columns]
    return frame


def render_task_detail(task: dict[str, Any], compact: bool = False) -> None:
    schedule = task.get("schedule") or {}
    cost = task.get("cost") or {}
    resources = task.get("resources") or {}
    ewp = task.get("engineering_work_package") or {}
    execution = task.get("execution") or {}
    implementation = task.get("implementation_plan") or {}
    pills = [task.get("concept"), task.get("phase"), task.get("scenario_route"), ewp.get("primary_domain"), ewp.get("work_pattern")]
    pill_html = "".join(f'<span class="msr-pill">{html.escape(str(value).replace("_", " ").title())}</span>' for value in pills if value)
    st.markdown(
        f"""
        <div class="msr-task-head">
          <div class="msr-task-title">{html.escape(str(task.get('id')))} — {html.escape(str(task.get('name') or ''))}</div>
          <div class="msr-task-meta">{html.escape(str(task.get('execution_stream') or ''))}</div>
          <div>{pill_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(8)
    cols[0].metric("Start", schedule.get("start") or "—")
    cols[1].metric("Finish", schedule.get("finish") or "—")
    cols[2].metric("Duration", f"{float(schedule.get('duration_months') or 0):,.1f} mo")
    cols[3].metric("FTE-years", f"{float(resources.get('fte_years') or 0):,.2f}")
    cols[4].metric("Labor", format_money_kusd(cost.get("labor_kusd")))
    cols[5].metric("Direct non-labor", format_money_kusd(cost.get("direct_non_labor_before_risk_kusd")))
    cols[6].metric("Task cost", format_money_kusd(cost.get("total_kusd")))
    cols[7].metric("Fully burdened view", format_money_kusd(cost.get("fully_burdened_task_view_kusd") or cost.get("total_kusd")))

    tabs = st.tabs(["Scope", "Implementation", "Inputs", "Engineering procedure", "Outputs", "Requirements & tools", "Interfaces & controls", "Cost basis", "Resources"])
    with tabs[0]:
        render_section_header("Technical scope", str(ewp.get("engineering_readiness_level") or ""), "Work package")
        st.write(task.get("description") or execution.get("purpose") or "—")
        st.markdown("#### Objective")
        st.write(ewp.get("objective") or "—")
        context = ewp.get("planning_and_decision_context") or {}
        if context:
            st.markdown("#### Decision and planning context")
            context_cols = st.columns(2)
            with context_cols[0]:
                st.markdown("**Decision supported**")
                st.write(context.get("decision_supported") or "—")
                st.markdown("**Why this activity occurs now**")
                st.write(context.get("why_now") or "—")
            with context_cols[1]:
                st.markdown("**Parallel-work rule**")
                st.write(context.get("parallel_work_rules") or "—")
                st.markdown("**Stop conditions**")
                st.write(context.get("stop_conditions") or "—")
        questions = ewp.get("engineering_questions_to_close") or []
        if questions:
            st.markdown("#### Engineering questions to close")
            _list_markdown(questions)
        st.markdown("#### Entry criteria")
        _list_markdown(ewp.get("entry_criteria") or [])
        resource_plan = ewp.get("resource_plan") or {}
        team_cols = st.columns(3)
        with team_cols[0]:
            st.markdown("#### Producing team")
            _list_markdown(resource_plan.get("core_producing_team") or [])
        with team_cols[1]:
            st.markdown("#### Assurance & enabling")
            _list_markdown(resource_plan.get("supporting_assurance_and_enabling_roles") or [])
        with team_cols[2]:
            st.markdown("#### Technical authority")
            st.write(resource_plan.get("technical_authority") or task.get("responsible_role") or "—")
    with tabs[1]:
        render_section_header("Implementation plan", str(implementation.get("implementation_readiness") or "Execution basis"), "Execution")
        st.write(implementation.get("implementation_summary") or "—")
        strategy = implementation.get("delivery_strategy") or {}
        make_buy = implementation.get("make_buy_partner_decision") or {}
        strategy_cols = st.columns(2)
        with strategy_cols[0]:
            st.markdown("#### Delivery strategy")
            if strategy:
                for key, value in strategy.items():
                    st.markdown(f"**{str(key).replace('_', ' ').title()}**")
                    st.write(value if not isinstance(value, (list, dict)) else value)
            else:
                st.write("—")
        with strategy_cols[1]:
            st.markdown("#### Make / buy / partner")
            if make_buy:
                for key, value in make_buy.items():
                    st.markdown(f"**{str(key).replace('_', ' ').title()}**")
                    st.write(value if not isinstance(value, (list, dict)) else value)
            else:
                st.write("—")

        auth = _records_frame(implementation.get("authorizations_and_prerequisites") or [], ["authorization", "evidence"])
        if not auth.empty:
            st.markdown("#### Authorizations and prerequisites")
            st.dataframe(auth, use_container_width=True, hide_index=True, height=min(430, 95 + 62 * len(auth)))

        st.markdown("#### Field execution sequence")
        for index, step in enumerate(implementation.get("implementation_steps") or [], start=1):
            step_id = step.get("step_id") or f"IMP-{index:02d}"
            action = step.get("action") or "Implementation action"
            with st.expander(f"{step_id} · {action}", expanded=index == 1):
                cols = st.columns([1.05, 1])
                with cols[0]:
                    st.markdown("**Responsible / work location**")
                    st.write(f"{step.get('responsible_role') or '—'} · {step.get('work_location') or '—'}")
                    st.markdown("**Required inputs**")
                    _list_markdown(step.get("required_inputs") or [])
                    st.markdown("**Detailed execution guidance**")
                    st.write(step.get("detailed_guidance") or "—")
                with cols[1]:
                    st.markdown("**Tools and equipment**")
                    _list_markdown(step.get("tools_equipment") or [])
                    st.markdown("**Outputs and retained records**")
                    _list_markdown(step.get("outputs_and_records") or [])
                    st.markdown("**Acceptance condition**")
                    st.write(step.get("acceptance_condition") or "—")
                if step.get("hold_point"):
                    st.markdown("**Hold point**")
                    st.write(step.get("hold_point"))

        procurement = implementation.get("procurement_and_contracting_actions") or []
        long_leads = implementation.get("long_lead_items") or []
        decisions = implementation.get("decision_points") or []
        field_work = implementation.get("field_lab_or_vendor_activities") or []
        contingencies = implementation.get("fallbacks_and_contingencies") or []
        cols = st.columns(2)
        with cols[0]:
            st.markdown("#### Procurement and contracting")
            _list_markdown(procurement)
            if long_leads:
                st.markdown("#### Long-lead items")
                st.dataframe(_records_frame(long_leads, ["item", "action"]), use_container_width=True, hide_index=True, height=min(430, 95 + 58 * len(long_leads)))
            if field_work:
                st.markdown("#### Laboratory, field, and vendor work")
                st.dataframe(_records_frame(field_work, ["activity", "where", "evidence"]), use_container_width=True, hide_index=True, height=min(520, 95 + 70 * len(field_work)))
        with cols[1]:
            if decisions:
                st.markdown("#### Decisions and release gates")
                st.dataframe(_records_frame(decisions, ["decision", "required_by", "evidence"]), use_container_width=True, hide_index=True, height=min(520, 95 + 70 * len(decisions)))
            if contingencies:
                st.markdown("#### Fallbacks and contingencies")
                st.dataframe(_records_frame(contingencies, ["trigger", "response"]), use_container_width=True, hide_index=True, height=min(520, 95 + 74 * len(contingencies)))

        st.markdown("#### Implementation records")
        _list_markdown(implementation.get("implementation_records") or [])
        source_basis = implementation.get("implementation_source_basis") or []
        if source_basis:
            st.markdown("#### Technical and execution precedents")
            st.dataframe(_records_frame(source_basis), use_container_width=True, hide_index=True, height=min(520, 95 + 55 * len(source_basis)))
        open_decisions = implementation.get("open_decisions") or []
        if open_decisions:
            st.markdown("#### Open implementation decisions")
            if isinstance(open_decisions[0], dict):
                st.dataframe(_records_frame(open_decisions, ["decision", "owner", "required_by", "closure_evidence"]), use_container_width=True, hide_index=True, height=min(520, 95 + 68 * len(open_decisions)))
            else:
                _list_markdown(open_decisions)

    with tabs[2]:
        frame = _records_frame(ewp.get("controlled_inputs") or [], ["input_id", "input", "source_or_owner", "required_maturity", "verification_before_use", "configuration_control"])
        if frame.empty:
            _list_markdown(execution.get("required_inputs") or [])
        else:
            st.dataframe(frame, use_container_width=True, hide_index=True, height=min(720, 86 + 44 * len(frame)))
    with tabs[3]:
        steps = ewp.get("execution_procedure") or []
        for index, item in enumerate(steps, start=1):
            step_no = int(item.get("step") or index)
            action = str(item.get("action") or "Engineering action")
            with st.expander(f"Step {step_no:02d} · {action}", expanded=step_no == 1):
                left, right = st.columns([1.05, 1])
                with left:
                    st.markdown("**Work instruction**")
                    st.write(item.get("work_instruction") or action)
                    st.markdown("**Engineering guidance**")
                    st.write(item.get("engineering_guidance") or "—")
                    st.markdown("**Step inputs**")
                    st.write(item.get("step_inputs") or "Use the applicable controlled inputs and assumptions.")
                with right:
                    st.markdown("**Expected output and retained evidence**")
                    st.write(item.get("step_outputs") or item.get("expected_evidence") or "—")
                    st.markdown("**Verification**")
                    st.write(item.get("verification") or "—")
                    st.markdown("**Acceptance and completion signal**")
                    st.write(item.get("step_acceptance") or item.get("completion_signal") or "—")
                checkpoint = item.get("review_checkpoint")
                if checkpoint:
                    st.markdown("**Review checkpoint / hold point**")
                    st.write(checkpoint)
                checks = item.get("engineering_checks") or []
                if checks:
                    st.markdown("**Checks to perform**")
                    _list_markdown(checks)
        holds = ewp.get("required_reviews_and_hold_points") or []
        if holds:
            st.markdown("#### Required reviews and hold points")
            st.dataframe(_records_frame(holds), use_container_width=True, hide_index=True, height=min(420, 90 + 58 * len(holds)))
    with tabs[4]:
        frame = _records_frame(ewp.get("deliverable_register") or [], ["deliverable_id", "deliverable", "minimum_contents", "format_and_records", "preparer", "independent_review", "approval", "downstream_use"])
        if not frame.empty:
            st.dataframe(frame, use_container_width=True, hide_index=True, height=min(720, 95 + 50 * len(frame)))
        st.markdown("#### Definition of done")
        _list_markdown(ewp.get("definition_of_done") or [])
        st.markdown("#### Required quality records")
        _list_markdown(ewp.get("quality_records") or [])
        minimum_record = ewp.get("minimum_execution_record") or []
        if minimum_record:
            st.markdown("#### Minimum execution record")
            _list_markdown(minimum_record)
    with tabs[5]:
        req = _records_frame(ewp.get("requirements_and_guidance") or [], ["authority_type", "citation", "topic", "applicability", "planned_compliance_evidence"])
        if not req.empty:
            st.markdown("#### Requirements and guidance")
            st.dataframe(req, use_container_width=True, hide_index=True, height=min(600, 90 + 44 * len(req)))
        tools = _records_frame(ewp.get("toolchain") or [], ["tool_or_method", "tool_type", "intended_use", "qualification_and_control", "required_record"])
        if not tools.empty:
            st.markdown("#### Toolchain and method controls")
            st.dataframe(tools, use_container_width=True, hide_index=True, height=min(650, 90 + 46 * len(tools)))
    with tabs[6]:
        interface_df = _records_frame(ewp.get("interfaces") or [], ["direction", "interface", "required_exchange", "interface_owner"])
        if not interface_df.empty:
            st.markdown("#### Interfaces")
            st.dataframe(interface_df, use_container_width=True, hide_index=True, height=min(520, 90 + 42 * len(interface_df)))
        risk_df = _records_frame(ewp.get("risks_and_controls") or [], ["risk_id", "risk_or_uncertainty", "control", "escalation_trigger"])
        if not risk_df.empty:
            st.markdown("#### Task-level risks and controls")
            st.dataframe(risk_df, use_container_width=True, hide_index=True, height=min(460, 90 + 44 * len(risk_df)))
        verification_df = _records_frame(ewp.get("verification_and_validation") or [], ["verification", "method", "evidence"])
        if not verification_df.empty:
            st.markdown("#### Verification and validation")
            st.dataframe(verification_df, use_container_width=True, hide_index=True, height=360)
        controls = ewp.get("execution_controls") or {}
        logic = ewp.get("schedule_logic_and_parallelization") or {}
        st.markdown("#### Schedule, parallelization, and change controls")
        if logic:
            for label, key in [("Use of predecessor products", "predecessor_use"), ("Parallel execution", "parallel_execution"), ("Progress measure", "status_measure")]:
                st.markdown(f"**{label}**")
                st.write(logic.get(key) or "—")
        if controls:
            compact_controls = [{"Control": str(key).replace("_", " ").title(), "Value": value if not isinstance(value, (dict, list)) else json.dumps(value, ensure_ascii=False)} for key, value in controls.items()]
            st.dataframe(pd.DataFrame(compact_controls), use_container_width=True, hide_index=True, height=min(460, 90 + 38 * len(compact_controls)))
    with tabs[7]:
        st.markdown("#### Basis of estimate")
        estimate_cols = st.columns(4)
        estimate_cols[0].metric("Direct task estimate", format_money_kusd(cost.get("total_kusd")))
        estimate_cols[1].metric("Allocated contract share", format_money_kusd(cost.get("allocated_program_package_kusd")))
        estimate_cols[2].metric("Fully burdened task view", format_money_kusd(cost.get("fully_burdened_task_view_kusd") or cost.get("total_kusd")))
        estimate_cols[3].metric(
            "Planning range",
            f"{format_money_kusd(cost.get('low_kusd'))} – {format_money_kusd(cost.get('high_kusd'))}",
        )
        basis_rows = [
            {"Field": "Basis of estimate", "Value": cost.get("basis_of_estimate_id") or "—"},
            {"Field": "Estimate class", "Value": cost.get("estimate_class") or "—"},
            {"Field": "Estimate method", "Value": cost.get("estimate_method") or "—"},
            {"Field": "Currency basis", "Value": f"Constant {cost.get('estimate_currency_year') or 2026} USD"},
            {"Field": "Planned labor hours", "Value": f"{float(cost.get('planned_labor_hours') or 0):,.0f}"},
            {"Field": "Blended loaded rate", "Value": f"${float(cost.get('blended_loaded_rate_kusd_per_fte_year') or 0):,.1f}k/FTE-year"},
            {"Field": "Risk allowance", "Value": f"{float(cost.get('risk_allowance_pct') or 0):.1%} / {format_money_kusd(cost.get('risk_allowance_kusd'))}"},
            {"Field": "Estimate status", "Value": cost.get("estimate_status") or "—"},
        ]
        st.dataframe(pd.DataFrame(basis_rows), use_container_width=True, hide_index=True, height=360)

        component_labels = {
            "labor_kusd": "Loaded labor",
            "external_engineering_and_lab_services_kusd": "External engineering and laboratory services",
            "software_compute_and_data_kusd": "Software, compute, and data",
            "equipment_materials_and_fabrication_kusd": "Equipment, materials, and fabrication",
            "facility_test_and_field_operations_kusd": "Facility, test, and field operations",
            "regulatory_review_fees_kusd": "Regulatory review fees",
            "legal_hearing_and_advisory_kusd": "Legal, hearing, and advisory",
            "travel_and_field_support_kusd": "Travel and field support",
            "other_direct_kusd": "Other direct cost",
            "risk_allowance_kusd": "Task risk allowance",
        }
        component_rows = [{"Cost component": "Loaded labor", "Cost ($000)": float(cost.get("labor_kusd") or 0.0)}]
        for key, value in (cost.get("cost_components") or {}).items():
            component_rows.append({"Cost component": component_labels.get(key, key.replace("_", " ").title()), "Cost ($000)": float(value or 0.0)})
        component_frame = pd.DataFrame(component_rows)
        if not component_frame.empty:
            component_frame["Share of task"] = component_frame["Cost ($000)"] / max(float(cost.get("total_kusd") or 0.0), 1e-12)
            st.markdown("#### Direct cost composition")
            st.dataframe(component_frame, use_container_width=True, hide_index=True, height=min(520, 92 + 42 * len(component_frame)))

        labor_breakdown = cost.get("labor_effort_breakdown") or {}
        if labor_breakdown:
            labor_rows = [
                {"Labor activity": key.replace("_", " ").title(), "Hours": float(value or 0.0)}
                for key, value in labor_breakdown.items()
            ]
            labor_frame = pd.DataFrame(labor_rows)
            labor_frame["Share"] = labor_frame["Hours"] / max(labor_frame["Hours"].sum(), 1e-12)
            st.markdown("#### Labor effort breakdown")
            st.dataframe(labor_frame, use_container_width=True, hide_index=True, height=min(380, 92 + 42 * len(labor_frame)))

        prior = cost.get("prior_estimate") or {}
        change = cost.get("estimate_change") or {}
        if prior:
            st.markdown("#### Re-estimate comparison")
            comparison = pd.DataFrame(
                [
                    {"Measure": "Labor ($000)", "Prior": float(prior.get("labor_kusd") or 0.0), "Revised": float(cost.get("labor_kusd") or 0.0)},
                    {"Measure": "Non-labor ($000)", "Prior": float(prior.get("non_labor_kusd") or 0.0), "Revised": float(cost.get("non_labor_kusd") or 0.0)},
                    {"Measure": "Total ($000)", "Prior": float(prior.get("total_kusd") or 0.0), "Revised": float(cost.get("total_kusd") or 0.0)},
                    {"Measure": "FTE-years", "Prior": float(prior.get("fte_years") or 0.0), "Revised": float(cost.get("planned_fte_years") or 0.0)},
                ]
            )
            comparison["Delta"] = comparison["Revised"] - comparison["Prior"]
            st.dataframe(comparison, use_container_width=True, hide_index=True, height=270)
            st.write(change.get("reason") or "")

        allocations = cost.get("allocated_program_package_sources") or []
        if allocations:
            st.markdown("#### Allocated program-package costs")
            st.dataframe(_records_frame(allocations, ["source_task_id", "allocated_kusd", "basis"]), use_container_width=True, hide_index=True, height=min(340, 90 + 52 * len(allocations)))
            st.caption("This allocation is a non-additive management view. The accounting cost remains on the source package task and is not summed twice in program totals.")

        st.markdown("#### Cost drivers")
        _list_markdown(cost.get("cost_drivers") or [])
        st.markdown("#### Exclusions and double-counting controls")
        _list_markdown(cost.get("exclusions_and_double_counting_controls") or [])
        st.markdown("#### Re-estimate triggers")
        _list_markdown(cost.get("reestimate_triggers") or [])
        st.markdown("#### Direct non-labor basis")
        st.write(cost.get("direct_non_labor_basis") or "—")
        st.markdown("#### Uncertainty basis")
        st.write(cost.get("uncertainty_range_basis") or "—")

    with tabs[8]:
        assignments = resources.get("assignments") or []
        if assignments:
            fields = ["role", "work_type", "avg_fte", "fte_years", "loaded_rate_kusd_per_fte_year", "labor_cost_kusd"]
            frame = pd.DataFrame(assignments)
            frame = frame[[field for field in fields if field in frame.columns]]
            frame.columns = [column.replace("_", " ").title().replace("Kusd", "$000") for column in frame.columns]
            st.dataframe(frame, use_container_width=True, hide_index=True, height=min(580, 90 + 40 * len(frame)))
        else:
            st.write("Resource assignments are maintained in the scenario-level resource table.")
        st.markdown("#### Cost and schedule record")
        st.json({"cost": cost, "schedule": schedule}, expanded=False)


def render_kpi_cards(items: list[dict[str, Any]]) -> None:
    if not items:
        return
    columns = st.columns(len(items))
    for column, item in zip(columns, items):
        with column:
            render_kpi(str(item.get("label") or ""), str(item.get("value") or ""), str(item.get("help") or item.get("note") or ""))


def style_plotly_figure(fig: go.Figure, *, height: int | None = None) -> go.Figure:
    has_title = bool(getattr(fig.layout.title, "text", None))
    fig.update_layout(
        template="plotly_white",
        colorway=CHART_COLORS,
        font=dict(family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Arial, sans-serif", color="#334155", size=12),
        title=dict(font=dict(size=19, color="#0f172a", family="Inter, Segoe UI, Arial"), x=0.01, xanchor="left", y=0.98),
        paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
        margin=dict(l=36, r=24, t=64 if has_title else 30, b=40),
        hoverlabel=dict(bgcolor="#ffffff", bordercolor="#cbd5e1", font_color="#0f172a", font_size=12),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1,
            bgcolor="rgba(255,255,255,.88)", bordercolor="#e2e8f0", borderwidth=1,
            font=dict(size=11), itemclick="toggle", itemdoubleclick="toggleothers",
        ),
        bargap=.24, bargroupgap=.08, barcornerradius=5,
        hovermode="closest", transition_duration=180,
    )
    if height:
        fig.update_layout(height=height)
    axis_style = dict(
        gridcolor="#e8eef6", zeroline=False, showline=True, linecolor="#cbd5e1",
        linewidth=1, ticks="outside", tickcolor="#94a3b8", tickfont=dict(size=11),
        title_font=dict(size=12, color="#475569"), automargin=True,
    )
    fig.update_xaxes(**axis_style)
    fig.update_yaxes(**axis_style)
    return fig

def route_graph_figure(tasks: list[dict[str, Any]], selected_id: str | None = None, title: str | None = None) -> go.Figure:
    fig, _ = pathway_graph_figure(tasks, selected_id=selected_id, max_nodes=max(40, len(tasks) + 5), show_names=False)
    if title:
        fig.update_layout(title=title)
    return style_plotly_figure(fig)


def extract_selected_task_id(event: Any) -> str | None:
    return selected_task_from_event(event)
