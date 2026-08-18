from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.auth import render_logout_control, require_authentication
from src.analytics import (
    annual_financial_frame,
    annual_staffing_frame,
    assignments_frame,
    category_cost_frame,
    engineering_work_package_frames,
    milestones_frame,
    quarterly_staffing_frame,
    risks_frame,
    role_summary_frame,
    route_cost_frame,
    scenario_export_tables,
    stream_summary_frame,
    tasks_frame,
    work_type_summary_frame,
)
from src.components import (
    CHART_COLORS,
    PLOTLY_CONFIG,
    ROUTE_COLORS,
    apply_page_style,
    extract_selected_task_id,
    format_fte,
    format_money_kusd,
    render_hero,
    render_kpi_cards,
    render_note,
    render_path_card,
    render_section_header,
    render_sidebar_brand,
    render_task_detail,
    route_graph_figure,
    style_plotly_figure,
)
from src.data_loader import DEFAULT_DATABASE, DatabaseValidationError, load_database, load_database_bytes
from src.pathway_engine import (
    DEMONSTRATOR_PATH,
    EXECUTABLE_POWER_PATHS,
    PATH_DISPLAY_NAMES,
    POWER_PATHS,
    ScenarioError,
    ScenarioOptions,
    build_scenario,
    compare_pathways,
    default_variant,
    pathway_variants,
)

st.set_page_config(
    page_title="Project-MSR Integrated Planner",
    page_icon="⚛",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Project-MSR integrated engineering and licensing planner."},
)
apply_page_style()

PATHWAY_FEATURES = [
    {
        "Path": "Part 50",
        "Products": "Construction Permit, then Operating License",
        "Design timing": "Preliminary design at CP; final as-built design at OL",
        "Construction verification": "Appendix B design/construction controls and NRC inspections",
        "Operation gate": "10 CFR 50.57 OL findings",
        "Distinct work": "Two formal application stages; PSAR-to-as-built change control; FSAR, operating programs, startup evidence, and OL findings",
        "Deployment logic": "Design flexibility during construction with a second licensing decision before operation",
    },
    {
        "Path": "Part 52",
        "Products": "COL, optionally preceded by ESP and/or Design Certification",
        "Design timing": "Substantially complete design and operating information before COL",
        "Construction verification": "Tier 1/Tier 2, ITAAC, ICNs/UINs, all-ITAAC-complete package",
        "Operation gate": "10 CFR 52.103(g) acceptance-criteria finding",
        "Distinct work": "Front-end design finality; optional ESP/DC products; Tier architecture; ITAAC evidence, closure notifications, and operation finding",
        "Deployment logic": "Higher nonrecurring standardization investment with reuse potential for repeat units",
    },
    {
        "Path": "Part 53",
        "Products": "Risk-informed COL or CP/OL sequence",
        "Design timing": "Safety case matures around PRA/SRE, LBEs, classification, defense in depth, and performance requirements",
        "Construction verification": "Performance-based verification, inspections, commitments, and readiness evidence",
        "Operation gate": "Part 53 license conditions and readiness authorization",
        "Distinct work": "PRA/SRE technical adequacy; LBE selection; SSC classification/special treatment; functional containment; performance monitoring",
        "Deployment logic": "Technology-inclusive, risk-informed, performance-based safety case",
    },
    {
        "Path": "Part 57 planning",
        "Products": "Rule-readiness and migration planning; standardized/high-volume sensitivity products",
        "Design timing": "Standard design and repeat-deployment envelope",
        "Construction verification": "Factory/site evidence and targeted-inspection planning",
        "Operation gate": "Selected executable fallback or future rule implementation",
        "Distinct work": "Eligibility, rule-readiness, standardization, manufacturing, multi-site, remote-operation, and migration planning",
        "Deployment logic": "Planning case paired with an executable Part 50, 52, or 53 baseline when current-with-fallback mode is selected",
    },
]

NAV_ITEMS = [
    "Overview",
    "Pathway comparison",
    "Licensing plan",
    "Pathway graph",
    "Schedule",
    "Work packages",
    "Resources",
    "Financials",
    "Cost basis",
    "Experiments",
    "Implementation",
    "Risks & gates",
    "Data & export",
]


ROUTE_DISPLAY_COLORS = {
    "DOE Launch Pad": ROUTE_COLORS["doe_launchpad"],
    "10 CFR Part 50": ROUTE_COLORS["part50"],
    "10 CFR Part 52": ROUTE_COLORS["part52"],
    "10 CFR Part 53": ROUTE_COLORS["part53"],
    "Proposed 10 CFR Part 57": ROUTE_COLORS["part57"],
    "Shared program baseline": "#94a3b8",
}

STREAM_LABELS = {
    "0": "Program backbone",
    "1": "Methods, validation & topicals",
    "2A": "Integral thermal-hydraulics facility",
    "2B": "INL critical experiment",
    "3": "Demonstrator engineering & authorization",
    "4": "Demonstrator experimental campaign",
    "5": "Commercial engineering & licensing",
    "6": "Commercial construction, startup & optimization",
}

STREAM_COLORS_APP = {
    "0": "#64748b",
    "1": "#315efb",
    "2A": "#0f9f8f",
    "2B": "#13b6a6",
    "3": "#7c3aed",
    "4": "#e76f51",
    "5": "#2f80ed",
    "6": "#c47b23",
}

WORK_TYPE_COLORS = {
    "Direct technical work": "#315efb",
    "Required assurance and enabling work": "#0f9f8f",
    "Management and controls": "#94a3b8",
}


def _fingerprint(database: dict[str, Any]) -> str:
    seed = "|".join(
        [
            str(database.get("meta", {}).get("version") or ""),
            str(database.get("meta", {}).get("generated") or ""),
            str(database.get("data_quality", {}).get("engineering_ready_task_count") or ""),
        ]
    )
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]


def select_database() -> tuple[dict[str, Any], str]:
    with st.sidebar.expander("Database", expanded=False):
        source = st.radio("Source", ["Bundled database", "Upload compatible JSON"], index=0)
        try:
            if source == "Upload compatible JSON":
                uploaded = st.file_uploader("Project-MSR JSON", type=["json"])
                if uploaded is not None:
                    return load_database_bytes(uploaded.getvalue()), uploaded.name
            return load_database(DEFAULT_DATABASE), Path(DEFAULT_DATABASE).name
        except (DatabaseValidationError, json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
            st.error(f"Database load failed: {exc}")
            st.stop()
    return load_database(DEFAULT_DATABASE), Path(DEFAULT_DATABASE).name


def _variant_select(database: dict[str, Any], path: str, label: str, key: str) -> str:
    variants = pathway_variants(database, path)
    keys = list(variants)
    default = default_variant(database, path)
    index = keys.index(default) if default in keys else 0
    return st.selectbox(label, keys, index=index, format_func=lambda value: variants[value]["label"], key=key)


def scenario_controls(database: dict[str, Any]) -> ScenarioOptions:
    st.sidebar.markdown("### Scenario configuration")

    demo_variant = _variant_select(database, DEMONSTRATOR_PATH, "Demonstrator implementation", "demo_variant")
    path = st.sidebar.selectbox(
        "Commercial licensing path",
        POWER_PATHS,
        index=POWER_PATHS.index("part53"),
        format_func=lambda value: PATH_DISPLAY_NAMES[value],
        key="power_path",
    )
    variant = _variant_select(database, path, "Commercial product sequence", f"variant_{path}")

    part57_mode = "current_with_fallback"
    fallback_path = "part53"
    fallback_variant = default_variant(database, fallback_path)
    if path == "part57":
        part57_mode = st.sidebar.radio(
            "Part 57 planning mode",
            ["current_with_fallback", "hypothetical_final_rule"],
            format_func=lambda value: database["pathways"]["part57"]["modes"][value]["label"],
        )
        if part57_mode == "current_with_fallback":
            fallback_path = st.sidebar.selectbox(
                "Executable fallback",
                EXECUTABLE_POWER_PATHS,
                index=EXECUTABLE_POWER_PATHS.index("part53"),
                format_func=lambda value: PATH_DISPLAY_NAMES[value],
            )
            fallback_variant = _variant_select(database, fallback_path, "Fallback product sequence", f"fallback_{fallback_path}")

    with st.sidebar.expander("Scenario sensitivities", expanded=False):
        labor_factor = st.slider("Labor effort factor", 0.70, 1.50, 1.00, 0.05)
        non_labor_factor = st.slider("Non-labor cost factor", 0.70, 1.60, 1.00, 0.05)
        schedule_shift = st.slider("Commercial schedule shift (months)", -12, 36, 0, 1)

    return ScenarioOptions(
        demonstrator_variant=demo_variant,
        power_reactor_path=path,
        power_reactor_variant=variant,
        part57_mode=part57_mode,
        part57_fallback_path=fallback_path,
        part57_fallback_variant=fallback_variant,
        labor_factor=labor_factor,
        non_labor_factor=non_labor_factor,
        power_schedule_shift_months=schedule_shift,
        preserve_demo_2028_target=True,
    )


def comparison_rows(database_version: str, database: dict[str, Any]) -> list[dict[str, Any]]:
    del database_version
    return compare_pathways(database)


def route_label(database: dict[str, Any], path: str, variant: str) -> str:
    return database["pathways"][path]["variants"][variant]["label"]


def top_metrics(scenario: dict[str, Any]) -> None:
    summary = scenario["summary"]
    render_kpi_cards(
        [
            {"label": "Program cost", "value": format_money_kusd(summary["total_cost_kusd"]), "help": "Active integrated scenario"},
            {"label": "Route-specific cost", "value": format_money_kusd(summary["route_specific_cost_kusd"]), "help": "DOE and commercial route work"},
            {"label": "Commercial route", "value": format_money_kusd(summary["commercial_route_total_kusd"]), "help": "Selected licensing product stack"},
            {"label": "Labor demand", "value": f"{summary['fte_years']:,.1f} FTE-yr", "help": "Resource-loaded effort"},
            {"label": "Active work packages", "value": f"{summary['active_task_count']:,}", "help": "Shared and route-specific"},
            {"label": "Commercial operation", "value": summary["power_commercial_operation_date"], "help": "Modeled scenario date"},
        ]
    )


def _plot(
    fig: go.Figure,
    *,
    key: str | None = None,
    height: int | None = None,
    config: dict[str, Any] | None = None,
):
    style_plotly_figure(fig, height=height)
    chart_config = dict(PLOTLY_CONFIG)
    if config:
        chart_config.update(config)
    return st.plotly_chart(fig, use_container_width=True, theme=None, key=key, config=chart_config)


def _short_label(value: Any, limit: int = 54) -> str:
    value = str(value or "")
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "…"


def _add_date_marker(fig: go.Figure, date_value: Any, label: str, *, color: str = "#64748b", y: float = 1.015) -> None:
    marker_date = pd.to_datetime(date_value)
    fig.add_shape(
        type="line", x0=marker_date, x1=marker_date, y0=0, y1=1,
        xref="x", yref="paper", line=dict(width=1.35, dash="dot", color=color),
    )
    fig.add_annotation(
        x=marker_date, y=y, xref="x", yref="paper", text=label,
        showarrow=False, yanchor="bottom", font=dict(size=10.5, color=color),
        bgcolor="rgba(255,255,255,.86)", borderpad=2,
    )


def _consolidated_stream_frame(scenario: dict[str, Any]) -> pd.DataFrame:
    frame = stream_summary_frame(scenario["tasks"], scenario["resource_assignments"])
    if frame.empty:
        return frame
    grouped = (
        frame.groupby("Stream ID", as_index=False)
        .agg(
            Activities=("Activities", "sum"),
            Start=("Start", "min"),
            Finish=("Finish", "max"),
            **{
                "Labor Cost ($000)": ("Labor Cost ($000)", "sum"),
                "Non-Labor Cost ($000)": ("Non-Labor Cost ($000)", "sum"),
                "Total Cost ($000)": ("Total Cost ($000)", "sum"),
                "FTE-years": ("FTE-years", "sum"),
            },
        )
    )
    grouped["Execution Stream"] = grouped["Stream ID"].astype(str).map(STREAM_LABELS).fillna(grouped["Stream ID"].astype(str))
    return grouped.sort_values("Stream ID", kind="stable").reset_index(drop=True)

def filter_tasks(
    tasks: list[dict[str, Any]],
    query: str,
    concepts: list[str],
    streams: list[str],
    domains: list[str],
    route_scope: str,
    critical_only: bool,
) -> list[dict[str, Any]]:
    query = query.strip().lower()
    output: list[dict[str, Any]] = []
    for task in tasks:
        package = task.get("engineering_work_package") or {}
        if concepts and task.get("concept") not in concepts:
            continue
        if streams and task.get("execution_stream") not in streams:
            continue
        if domains and package.get("primary_domain") not in domains:
            continue
        if route_scope == "Route-specific" and not task.get("pathway_specific"):
            continue
        if route_scope == "Shared baseline" and task.get("pathway_specific"):
            continue
        if critical_only and not task.get("schedule", {}).get("critical"):
            continue
        if query:
            blob = json.dumps(
                {
                    "id": task.get("id"),
                    "name": task.get("name"),
                    "description": task.get("description"),
                    "phase": task.get("phase"),
                    "regulatory_basis": task.get("regulatory_basis"),
                    "package": package,
                },
                ensure_ascii=False,
            ).lower()
            if query not in blob:
                continue
        output.append(task)
    return output


def overview_tab(database: dict[str, Any], scenario: dict[str, Any], options: ScenarioOptions) -> None:
    summary = scenario["summary"]
    render_section_header(
        "Active development architecture",
        "The nominal plan starts in Q4 2026, completes demonstrator construction and authorization in 2028, operates the demonstrator in 2029, starts commercial construction in 2030, and reaches licensed commercial operation in 2035.",
        "Program",
    )
    col1, col2 = st.columns(2)
    with col1:
        render_path_card(
            "Demonstrator authorization",
            scenario["pathways"]["demonstrator"],
            route_label(database, DEMONSTRATOR_PATH, options.demonstrator_variant),
        )
    with col2:
        selected_label = route_label(database, options.power_reactor_path, options.power_reactor_variant)
        if options.power_reactor_path == "part57" and options.part57_mode == "current_with_fallback":
            selected_label += f" · fallback {PATH_DISPLAY_NAMES[options.part57_fallback_path]} / {route_label(database, options.part57_fallback_path, options.part57_fallback_variant)}"
        render_path_card("Commercial power-reactor licensing", scenario["pathways"]["power_reactor"], selected_label)

    render_section_header("Planning commitments")
    render_kpi_cards(
        [
            {"label": "Planning start", "value": summary["planning_start"], "help": "Q4 2026"},
            {"label": "Demonstrator built/licensed", "value": summary["demonstrator_mechanical_completion_target"], "help": "Construction and authorization"},
            {"label": "Demonstrator operations", "value": "2029", "help": "Experimental operating campaign"},
            {"label": "Commercial construction", "value": summary["power_construction_start_date"], "help": "Field construction begins"},
            {"label": "Commercial authorization", "value": summary["power_operation_authorization_date"], "help": "Selected licensing route"},
            {"label": "Commercial operation", "value": summary["power_commercial_operation_date"], "help": "Fully licensed and operating"},
        ]
    )

    stages = pd.DataFrame(
        [
            {"Program stage": "1 · Methods and topicals", "Nominal window": "Q4 2026-2031", "Primary outcome": "Qualified analytical methods, validation evidence, and topical reports"},
            {"Program stage": "2 · Parallel evidence facilities", "Nominal window": "Q4 2026-2029", "Primary outcome": "Integral thermal-hydraulics and critical-experiment data"},
            {"Program stage": "3 · Demonstrator engineering and authorization", "Nominal window": "Q4 2026-Dec 2028", "Primary outcome": "Built and authorized demonstrator"},
            {"Program stage": "4 · Demonstrator operations", "Nominal window": "Jan-Dec 2029", "Primary outcome": "Qualified data for commercial design and licensing"},
            {"Program stage": "5 · Commercial engineering and licensing", "Nominal window": "2027-2035", "Primary outcome": "Licensed commercial reactor and completed operating programs"},
            {"Program stage": "6 · Commercial construction and optimization", "Nominal window": "2030-2038", "Primary outcome": "Commercial operation in 2035 and sustained reliability/economic optimization"},
        ]
    )
    st.dataframe(stages, use_container_width=True, hide_index=True, height=285)

    profile = scenario.get("planning_profile") or {}
    principles = profile.get("ramp_principles") or []
    if principles:
        render_section_header("Mobilization and continuity rules")
        cols = st.columns(2)
        for idx, principle in enumerate(principles):
            with cols[idx % 2]:
                st.markdown(f'<div class="msr-card msr-compact-card"><div class="msr-card-title">Rule {idx + 1:02d}</div><div class="msr-card-copy">{principle}</div></div>', unsafe_allow_html=True)

def comparison_tab(database: dict[str, Any], database_fp: str) -> None:
    render_section_header(
        "Licensing-path comparison",
        "Bottom-up applicant activities, resources, non-labor allowances, review cycles, product structures, construction verification, and operation gates are compared separately from the shared reactor-development program.",
        "Commercial licensing",
    )
    comparison = pd.DataFrame(comparison_rows(database_fp, database))
    executable = comparison[comparison["Executable"]].copy()
    planning_cases = comparison[~comparison["Executable"]].copy()

    if not executable.empty:
        low = executable.loc[executable["Commercial Route Total ($000)"].idxmin()]
        high = executable.loc[executable["Commercial Route Total ($000)"].idxmax()]
        early = executable.loc[pd.to_datetime(executable["Commercial Operation"]).idxmin()]
        render_kpi_cards(
            [
                {"label": "Lowest route cost", "value": format_money_kusd(low["Commercial Route Total ($000)"]), "help": low["Variant"]},
                {"label": "Highest route cost", "value": format_money_kusd(high["Commercial Route Total ($000)"]), "help": high["Variant"]},
                {"label": "Cost spread", "value": format_money_kusd(high["Commercial Route Total ($000)"] - low["Commercial Route Total ($000)"]), "help": "Executable modeled routes"},
                {"label": "Earliest operation", "value": early["Commercial Operation"], "help": early["Variant"]},
                {"label": "Most route tasks", "value": f"{int(executable['Route Activities'].max())}", "help": "Selected product stack"},
                {"label": "Review cycles", "value": f"{int(executable['Formal Review Cycles'].max())} max", "help": "Modeled formal stages"},
            ]
        )

    display = executable.copy()
    display["FOAK route cost ($M)"] = display["Commercial Route Total ($000)"] / 1000.0
    display["Repeat route cost ($M)"] = display["Repeat Power Route Cost ($000)"] / 1000.0
    symbol_map = {1: "diamond", 2: "circle", 3: "square", 4: "triangle-up"}
    fig = go.Figure()
    for path_key, group in display.groupby("Path Key", sort=False):
        custom = group[["Variant", "Formal Review Cycles", "Route Activities", "Application", "Construction Authorization", "Mechanical Completion", "Commercial Operation"]].to_numpy()
        sizes = (16 + group["Route Activities"].astype(float) * .65).clip(18, 38)
        symbols = [symbol_map.get(int(value), "circle") for value in group["Formal Review Cycles"]]
        fig.add_scatter(
            x=group["FOAK route cost ($M)"], y=group["Repeat route cost ($M)"], mode="markers",
            name=PATH_DISPLAY_NAMES.get(path_key, path_key),
            marker=dict(size=sizes, symbol=symbols, color=ROUTE_COLORS.get(path_key, "#64748b"), opacity=.92, line=dict(width=1.5, color="#ffffff")),
            customdata=custom,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>FOAK route: $%{x:.1f}M<br>Repeat route: $%{y:.1f}M"
                "<br>Formal review cycles: %{customdata[1]}<br>Route activities: %{customdata[2]}"
                "<br>Application: %{customdata[3]}<br>Construction authorization: %{customdata[4]}"
                "<br>Mechanical completion: %{customdata[5]}<br>Commercial operation: %{customdata[6]}<extra></extra>"
            ),
        )
    max_axis = max(display["FOAK route cost ($M)"].max(), display["Repeat route cost ($M)"].max()) * 1.08
    fig.add_shape(type="line", x0=0, y0=0, x1=max_axis, y1=max_axis, line=dict(color="#cbd5e1", dash="dash", width=1), layer="below")
    fig.add_annotation(x=max_axis * .75, y=max_axis * .77, text="Equal FOAK / repeat cost", showarrow=False, font=dict(size=10, color="#94a3b8"), textangle=-34)
    fig.update_layout(title="First-of-a-kind licensing investment versus repeat-deployment burden")
    fig.update_xaxes(title="FOAK route cost ($M)", range=[0, max_axis], ticksuffix="M")
    fig.update_yaxes(title="Repeat route cost ($M)", range=[0, max_axis], ticksuffix="M")
    _plot(fig, height=600)

    table_columns = [
        "Path", "Variant", "Regulatory Status", "Formal Review Cycles", "Route Activities",
        "Power Route Cost ($000)", "Part 57 Readiness Component ($000)", "Commercial Route Total ($000)",
        "Repeat Power Route Cost ($000)", "Application", "Construction Authorization", "Mechanical Completion",
        "Operation Authorization", "Commercial Operation",
    ]
    render_section_header("Route cost and schedule table")
    st.dataframe(
        executable[table_columns],
        use_container_width=True,
        hide_index=True,
        height=440,
        column_config={
            "Power Route Cost ($000)": st.column_config.NumberColumn(format="$%.0f"),
            "Part 57 Readiness Component ($000)": st.column_config.NumberColumn(format="$%.0f"),
            "Commercial Route Total ($000)": st.column_config.NumberColumn(format="$%.0f"),
            "Repeat Power Route Cost ($000)": st.column_config.NumberColumn(format="$%.0f"),
        },
    )
    render_section_header("Work structure by path")
    st.dataframe(pd.DataFrame(PATHWAY_FEATURES), use_container_width=True, hide_index=True, height=330)
    if not planning_cases.empty:
        with st.expander("Part 57 future-rule planning cases", expanded=False):
            st.dataframe(planning_cases[table_columns], use_container_width=True, hide_index=True)

def licensing_tab(database: dict[str, Any], scenario: dict[str, Any], options: ScenarioOptions) -> None:
    summary = scenario["summary"]
    render_section_header(
        "Selected licensing architecture",
        "The demonstrator authorization route and commercial power-reactor licensing route are modeled as separate products with independent task networks.",
        "Licensing plan",
    )
    render_kpi_cards(
        [
            {"label": "Demonstrator", "value": route_label(database, DEMONSTRATOR_PATH, options.demonstrator_variant), "help": "DOE implementation"},
            {"label": "Commercial path", "value": PATH_DISPLAY_NAMES[options.power_reactor_path], "help": "NRC product family"},
            {"label": "Product variant", "value": route_label(database, options.power_reactor_path, options.power_reactor_variant), "help": "Selected sequence"},
            {"label": "Application", "value": summary["power_application_date"], "help": "Commercial product"},
            {"label": "Construction authorization", "value": summary["power_construction_authorization_date"], "help": "Commercial reactor"},
            {"label": "Operation authorization", "value": summary["power_operation_authorization_date"], "help": "Commercial reactor"},
        ]
    )

    route_tasks = [task for task in scenario["tasks"] if task.get("pathway_specific")]
    route_df = tasks_frame(route_tasks)
    plan_tab, cost_tab, products_tab, detail_tab = st.tabs(["Route schedule", "Cost structure", "Products and dates", "Activity dictionary"])
    with plan_tab:
        if not route_df.empty:
            route_df = route_df.copy()
            route_df["Display task"] = route_df.apply(lambda row: f"{row['WBS ID']} · {_short_label(row['Task'], 50)}", axis=1)
            fig = px.timeline(
                route_df,
                x_start="Start",
                x_end="Finish",
                y="Display task",
                color="Scenario Route",
                hover_name="Task",
                hover_data={
                    "WBS ID": True,
                    "Phase": True,
                    "Engineering Domain": True,
                    "Total Cost ($000)": ":,.0f",
                    "FTE-years": ":.2f",
                    "Gate": True,
                    "Display task": False,
                    "Start": "|%b %Y",
                    "Finish": "|%b %Y",
                },
                color_discrete_map=ROUTE_DISPLAY_COLORS,
                title="Authorization and licensing work-package schedule",
            )
            fig.update_yaxes(autorange="reversed", title=None, tickfont=dict(size=10))
            for date_value, label, color in [
                (summary["power_application_date"], "Application", ROUTE_COLORS.get(options.power_reactor_path, "#315efb")),
                (summary["power_construction_authorization_date"], "Construction authorization", "#7c3aed"),
                (summary["power_operation_authorization_date"], "Operation authorization", "#0f9f8f"),
            ]:
                _add_date_marker(fig, date_value, label, color=color)
            _plot(fig, height=max(700, min(1350, 29 * len(route_df))))
    with cost_tab:
        cat = category_cost_frame(route_tasks, route_only=True)
        if not cat.empty:
            cat = cat.head(18).sort_values("Total Cost ($000)").copy()
            cat["Labor ($M)"] = cat["Labor Cost ($000)"] / 1000.0
            cat["Non-labor ($M)"] = cat["Non-Labor Cost ($000)"] / 1000.0
            fig = go.Figure()
            fig.add_bar(y=cat["Category"], x=cat["Labor ($M)"], name="Labor", orientation="h", marker_color=CHART_COLORS[0], customdata=cat[["Activities"]], hovertemplate="%{y}<br>Labor: $%{x:.1f}M<br>Activities: %{customdata[0]}<extra></extra>")
            fig.add_bar(y=cat["Category"], x=cat["Non-labor ($M)"], name="Non-labor", orientation="h", marker_color=CHART_COLORS[1], customdata=cat[["Activities"]], hovertemplate="%{y}<br>Non-labor: $%{x:.1f}M<br>Activities: %{customdata[0]}<extra></extra>")
            fig.update_layout(barmode="stack", title="Route-specific cost by work package")
            fig.update_xaxes(title="Cost ($M)", ticksuffix="M")
            fig.update_yaxes(title=None)
            _plot(fig, height=650)
        route_cost = route_cost_frame(route_tasks)
        st.dataframe(route_cost, use_container_width=True, hide_index=True)
    with products_tab:
        left, right = st.columns(2)
        with left:
            render_section_header("Selected products")
            for product in scenario["pathways"]["power_reactor"].get("products") or []:
                st.markdown(f"- {product}")
        with right:
            render_section_header("Commercial route dates")
            date_rows = [
                {"Milestone": "Application", "Date": summary["power_application_date"]},
                {"Milestone": "Construction authorization", "Date": summary["power_construction_authorization_date"]},
                {"Milestone": "Mechanical completion", "Date": summary["power_mechanical_completion_date"]},
                {"Milestone": "Operation authorization", "Date": summary["power_operation_authorization_date"]},
                {"Milestone": "Commercial operation", "Date": summary["power_commercial_operation_date"]},
            ]
            st.dataframe(date_rows, use_container_width=True, hide_index=True)
    with detail_tab:
        if route_tasks:
            route_ids = [task["id"] for task in route_tasks]
            selected_id = st.selectbox("Open route activity", route_ids, format_func=lambda task_id: f"{task_id} · {next(task['name'] for task in route_tasks if task['id'] == task_id)}")
            render_task_detail(next(task for task in route_tasks if task["id"] == selected_id))

def _graph_panel(tasks: list[dict[str, Any]], key_prefix: str, title: str) -> None:
    if not tasks:
        render_note("No route-specific activities are active for this graph scope.", "neutral")
        return
    task_by_id = {str(task["id"]): task for task in tasks}
    state_key = f"{key_prefix}_selected"
    select_key = f"{key_prefix}_selectbox"
    if st.session_state.get(state_key) not in task_by_id:
        st.session_state[state_key] = next(iter(task_by_id))
    current = st.session_state[state_key]

    graph_col, detail_col = st.columns([1.65, 1], gap="large")
    with graph_col:
        st.caption("Compact task IDs remain inside the nodes. Hover for the full title and key outputs; click a node to synchronize the work-package inspector. Pan and wheel zoom are enabled.")
        figure = route_graph_figure(tasks, selected_id=current, title=title)
        graph_config = dict(PLOTLY_CONFIG)
        graph_config.update({"scrollZoom": True, "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"]})
        event = st.plotly_chart(
            figure,
            use_container_width=True,
            theme=None,
            key=f"{key_prefix}_plot",
            on_select="rerun",
            selection_mode="points",
            config=graph_config,
        )
        clicked = extract_selected_task_id(event)
        if clicked in task_by_id and clicked != current:
            st.session_state[state_key] = clicked
            st.session_state[select_key] = clicked
            st.rerun()
    with detail_col:
        ids = list(task_by_id)
        if select_key not in st.session_state or st.session_state[select_key] not in ids:
            st.session_state[select_key] = current

        def _sync_selection() -> None:
            st.session_state[state_key] = st.session_state[select_key]

        selected = st.selectbox(
            "Selected activity",
            ids,
            key=select_key,
            format_func=lambda task_id: f"{task_id} · {task_by_id[task_id]['name']}",
            on_change=_sync_selection,
        )
        render_task_detail(task_by_id[selected], compact=True)

def pathway_graph_tab(database: dict[str, Any], scenario: dict[str, Any], options: ScenarioOptions) -> None:
    render_section_header(
        "Interactive licensing task graph",
        "The selected route is shown once as an interactive predecessor-successor network. Select any compact task node to open its full engineering work package.",
        "Task articulation",
    )
    demo_tasks = [task for task in scenario["tasks"] if task.get("pathway_specific") and task.get("concept") == "Demonstrator"]
    power_tasks = [task for task in scenario["tasks"] if task.get("pathway_specific") and task.get("concept") == "Power Reactor"]
    tabs = st.tabs(["Demonstrator route", "Commercial route", "Combined route"])
    with tabs[0]:
        _graph_panel(demo_tasks, "demo_route_graph", f"DOE demonstrator route · {route_label(database, DEMONSTRATOR_PATH, options.demonstrator_variant)}")
    with tabs[1]:
        commercial_label = f"{PATH_DISPLAY_NAMES[options.power_reactor_path]} · {route_label(database, options.power_reactor_path, options.power_reactor_variant)}"
        _graph_panel(power_tasks, "power_route_graph", commercial_label)
    with tabs[2]:
        _graph_panel(demo_tasks + power_tasks, "combined_route_graph", "Demonstrator authorization and commercial licensing route")


def schedule_tab(scenario: dict[str, Any]) -> None:
    render_section_header("Integrated schedule", "Program roadmap, detailed work-package schedule, route-only schedule, and authorization/startup milestones.", "Schedule")
    view = st.segmented_control("View", ["Program roadmap", "Detailed Gantt", "Route-only Gantt", "Milestones"], default="Program roadmap", label_visibility="collapsed")
    task_df = tasks_frame(scenario["tasks"])
    if view == "Program roadmap":
        stream_df = _consolidated_stream_frame(scenario)
        fig = px.timeline(
            stream_df,
            x_start="Start",
            x_end="Finish",
            y="Execution Stream",
            color="Stream ID",
            hover_name="Execution Stream",
            hover_data={"Activities": True, "Total Cost ($000)": ":,.0f", "FTE-years": ":.1f", "Stream ID": False, "Start": "|%b %Y", "Finish": "|%b %Y"},
            color_discrete_map=STREAM_COLORS_APP,
            title="Integrated six-stream program roadmap",
        )
        fig.update_yaxes(autorange="reversed", title=None)
        fig.update_layout(showlegend=False)
        for date_value, label, color in [
            (scenario["summary"]["demonstrator_mechanical_completion_target"], "Demonstrator built", "#7c3aed"),
            (scenario["summary"]["power_construction_start_date"], "Commercial build starts", "#c47b23"),
            (scenario["summary"]["power_commercial_operation_date"], "Commercial operation", "#0f9f8f"),
        ]:
            _add_date_marker(fig, date_value, label, color=color)
        _plot(fig, height=620)
        display = stream_df.copy()
        display["Start"] = display["Start"].dt.date
        display["Finish"] = display["Finish"].dt.date
        st.dataframe(display, use_container_width=True, hide_index=True)
    elif view in {"Detailed Gantt", "Route-only Gantt"}:
        c1, c2, c3 = st.columns([1.2, 1, 1])
        concepts = c1.multiselect("Concept", sorted(task_df["Concept"].dropna().unique()), default=[])
        critical_only = c2.checkbox("Critical tasks only", value=view == "Detailed Gantt")
        max_rows = c3.slider("Maximum rows", 25, 300, 120, 25)
        gantt = task_df.copy()
        if view == "Route-only Gantt":
            gantt = gantt[gantt["Pathway Specific"]]
        if concepts:
            gantt = gantt[gantt["Concept"].isin(concepts)]
        if critical_only:
            gantt = gantt[gantt["Critical"]]
        gantt = gantt.sort_values(["Start", "Finish"]).head(max_rows).copy()
        gantt["Display task"] = gantt.apply(lambda row: f"{row['WBS ID']} · {_short_label(row['Task'], 46)}", axis=1)
        color = "Scenario Route" if view == "Route-only Gantt" else "Stream ID"
        color_map = ROUTE_DISPLAY_COLORS if view == "Route-only Gantt" else STREAM_COLORS_APP
        fig = px.timeline(
            gantt,
            x_start="Start",
            x_end="Finish",
            y="Display task",
            color=color,
            hover_name="Task",
            hover_data={"WBS ID": True, "Concept": True, "Phase": True, "Engineering Domain": True, "Total Cost ($000)": ":,.0f", "FTE-years": ":.2f", "Gate": True, "Display task": False, "Start": "|%b %Y", "Finish": "|%b %Y"},
            color_discrete_map=color_map,
            title="Route-specific work packages" if view == "Route-only Gantt" else "Detailed integrated work-package schedule",
        )
        fig.update_yaxes(autorange="reversed", title=None, tickfont=dict(size=9.5))
        _plot(fig, height=max(650, min(1500, 25 * len(gantt))))
    else:
        milestones = milestones_frame(scenario["milestones"]).copy()
        milestone_symbols = {
            "Application": "circle", "Authorization strategy": "circle", "Construction authorization": "diamond",
            "Mechanical completion": "cross", "Operation readiness": "circle", "Operation authorization": "diamond",
            "Commercial operation": "star", "Fleet baseline": "cross",
        }
        fig = go.Figure()
        for pathway, group in milestones.groupby("Pathway", sort=False):
            custom = group[["Milestone / Decision Gate", "Type", "Decision Authority", "Entry Criteria / Evidence", "Successor Work Authorized"]].to_numpy()
            fig.add_scatter(
                x=group["Baseline Date"], y=group["Program / Concept"], mode="markers", name=PATH_DISPLAY_NAMES.get(str(pathway), str(pathway).replace("_", " ").title()),
                marker=dict(
                    size=15, color=ROUTE_DISPLAY_COLORS.get(str(pathway), ROUTE_COLORS.get(str(pathway), "#64748b")),
                    symbol=[milestone_symbols.get(str(value), "circle") for value in group["Type"]],
                    line=dict(width=1.5, color="#ffffff"), opacity=.95,
                ),
                customdata=custom,
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>%{x|%d %b %Y}<br>Type: %{customdata[1]}"
                    "<br>Decision authority: %{customdata[2]}<br>Entry evidence: %{customdata[3]}"
                    "<br>Successor work: %{customdata[4]}<extra></extra>"
                ),
            )
        fig.update_layout(title="Authorization, construction, and startup milestones")
        for date_value, label, color in [
            (scenario["summary"]["demonstrator_mechanical_completion_target"], "Demo complete", "#7c3aed"),
            (scenario["summary"]["power_construction_start_date"], "Commercial build", "#c47b23"),
            (scenario["summary"]["power_commercial_operation_date"], "Commercial operation", "#0f9f8f"),
        ]:
            _add_date_marker(fig, date_value, label, color=color)
        _plot(fig, height=540)
        show = milestones.copy()
        show["Baseline Date"] = show["Baseline Date"].dt.date
        st.dataframe(show, use_container_width=True, hide_index=True, height=500)

def work_packages_tab(scenario: dict[str, Any]) -> None:
    render_section_header(
        "Engineering work-package browser",
        "Every activity includes a structured execution basis, controlled inputs, step-by-step guidance, requirements, toolchain, outputs, verification, interfaces, records, and resource plan.",
        "Task dictionary",
    )
    all_tasks = scenario["tasks"]
    task_df_all = tasks_frame(all_tasks)
    with st.expander("Filters", expanded=True):
        cols = st.columns([2.1, 1, 1, 1, 0.8, 0.7])
        query = cols[0].text_input("Full-text search", placeholder="Search task, inputs, procedure, requirements, tools, outputs...")
        concepts = cols[1].multiselect("Concept", sorted(task_df_all["Concept"].dropna().unique()))
        streams = cols[2].multiselect("Execution stream", sorted(task_df_all["Execution Stream"].dropna().unique()))
        domains = cols[3].multiselect("Engineering domain", sorted(task_df_all["Engineering Domain"].dropna().unique()))
        route_scope = cols[4].selectbox("Scope", ["All", "Route-specific", "Shared baseline"])
        critical_only = cols[5].checkbox("Critical")
    filtered = filter_tasks(all_tasks, query, concepts, streams, domains, route_scope, critical_only)
    st.caption(f"{len(filtered):,} of {len(all_tasks):,} work packages")
    if not filtered:
        render_note("No work packages match the selected filters.", "neutral")
        return
    frame = tasks_frame(filtered)
    table_cols = [
        "WBS ID", "Concept", "Scenario Route", "Execution Stream", "Phase", "Engineering Domain", "Task",
        "Start", "Finish", "FTE-years", "Total Cost ($000)", "Procedure Steps Count", "Outputs Count", "Critical",
    ]
    display = frame[table_cols].copy()
    display["Start"] = display["Start"].dt.date
    display["Finish"] = display["Finish"].dt.date
    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        height=520,
        column_config={
            "FTE-years": st.column_config.NumberColumn(format="%.2f"),
            "Total Cost ($000)": st.column_config.NumberColumn(format="$%.0f"),
            "Critical": st.column_config.CheckboxColumn(),
        },
    )
    selected_id = st.selectbox("Open engineering work package", frame["WBS ID"].tolist(), format_func=lambda task_id: f"{task_id} · {next(task['name'] for task in filtered if task['id'] == task_id)}")
    render_task_detail(next(task for task in filtered if task["id"] == selected_id))


def resources_tab(scenario: dict[str, Any]) -> None:
    render_section_header("Resources and producing-team loading", "Gradual mobilization, sustained technical continuity, discipline demand, quarterly staffing, and task-level assignments.", "Resources")
    roles = role_summary_frame(scenario["resource_assignments"])
    work = work_type_summary_frame(scenario["resource_assignments"])
    annual = annual_staffing_frame(scenario)
    summary = scenario["summary"]
    work_map = work.set_index("Work Type")["Share"].to_dict() if not work.empty else {}
    target_map = (scenario.get("planning_profile") or {}).get("annual_resource_target_fte") or {}
    annual["Planning target"] = annual["Year"].astype(str).map(lambda year: float(target_map.get(year, 0.0)))
    peak_row = annual.loc[annual["FTE"].idxmax()] if not annual.empty else None
    post_2035 = annual[annual["Year"] >= 2035]
    render_kpi_cards(
        [
            {"label": "Total FTE-years", "value": format_fte(summary["fte_years"]), "help": "Integrated scenario"},
            {"label": "Peak annual FTE", "value": f"{annual['FTE'].max():,.1f}" if not annual.empty else "-", "help": f"{int(peak_row['Year'])}" if peak_row is not None else ""},
            {"label": "Q4 2026 mobilization", "value": f"{float(annual.loc[annual['Year'] == 2026, 'FTE'].sum()):,.1f} FTE-y", "help": "Quarter-year loading"},
            {"label": "2035-2038 continuity", "value": f"{post_2035['FTE'].sum():,.1f} FTE-y" if not post_2035.empty else "-", "help": "Startup and early-operation support"},
            {"label": "Direct technical", "value": f"{float(work_map.get('Direct technical work', 0.0)):.1%}", "help": "Producing work"},
            {"label": "Management/controls", "value": f"{float(work_map.get('Management and controls', 0.0)):.1%}", "help": "Planning and decisions"},
        ]
    )
    left, right = st.columns([1.42, 1])
    with left:
        fig = go.Figure()
        fig.add_scatter(
            x=annual["Year"], y=annual["FTE"], name="Modeled demand", mode="lines+markers",
            line=dict(width=3.5, color=CHART_COLORS[0], shape="spline", smoothing=.55),
            marker=dict(size=8, color="#ffffff", line=dict(width=2.5, color=CHART_COLORS[0])),
            fill="tozeroy", fillcolor="rgba(49,94,251,.12)",
            hovertemplate="%{x}<br>Modeled demand: %{y:.1f} FTE-year<extra></extra>",
        )
        fig.add_scatter(
            x=annual["Year"], y=annual["Planning target"], name="Planning target", mode="lines+markers",
            line=dict(width=2.2, color="#64748b", dash="dot"), marker=dict(size=6),
            hovertemplate="%{x}<br>Planning target: %{y:.1f} FTE-year<extra></extra>",
        )
        if peak_row is not None:
            fig.add_annotation(
                x=int(peak_row["Year"]), y=float(peak_row["FTE"]), text=f"Peak {float(peak_row['FTE']):.1f} FTE",
                showarrow=True, arrowhead=2, ax=35, ay=-48, bgcolor="#ffffff", bordercolor="#cbd5e1", borderpad=4,
                font=dict(size=11, color="#0f172a"),
            )
        fig.update_layout(title="Annual staffing ramp - peak shifted into commercial execution")
        fig.update_xaxes(dtick=1, title=None)
        fig.update_yaxes(title="FTE-years", rangemode="tozero")
        _plot(fig, height=460)
    with right:
        colors = [WORK_TYPE_COLORS.get(value, CHART_COLORS[index % len(CHART_COLORS)]) for index, value in enumerate(work["Work Type"])]
        fig = go.Figure(go.Pie(
            labels=work["Work Type"], values=work["FTE-years"], hole=.62, sort=False,
            marker=dict(colors=colors, line=dict(width=2, color="#ffffff")),
            textinfo="percent", textposition="inside", insidetextorientation="horizontal",
            hovertemplate="%{label}<br>%{value:.1f} FTE-years<br>%{percent}<extra></extra>",
        ))
        fig.add_annotation(text=f"{work['FTE-years'].sum():.0f}<br><span style='font-size:11px'>FTE-years</span>", x=.5, y=.5, showarrow=False, font=dict(size=22, color="#0f172a"))
        fig.update_layout(title="Labor classification", legend=dict(orientation="v", y=.5, x=1.02, xanchor="left"))
        _plot(fig, height=460)
    render_section_header("Largest discipline demands")
    top_roles = roles.head(20).sort_values("FTE-years").copy()
    fig = px.bar(
        top_roles,
        x="FTE-years",
        y="Role",
        orientation="h",
        color="Work Type",
        text="FTE-years",
        hover_data={"Assignments": True, "Labor Cost ($000)": ":,.0f", "FTE-years": ":.1f"},
        color_discrete_map=WORK_TYPE_COLORS,
        title="Largest producing and assurance discipline demands",
    )
    fig.update_traces(texttemplate="%{x:.1f}", textposition="outside", cliponaxis=False)
    fig.update_xaxes(title="FTE-years", rangemode="tozero")
    fig.update_yaxes(title=None)
    _plot(fig, height=680)
    with st.expander("Quarterly staffing heat map", expanded=False):
        quarterly = quarterly_staffing_frame(scenario["resource_assignments"])
        if not quarterly.empty:
            top_role_names = roles.head(18)["Role"].tolist()
            heat = quarterly[quarterly["Role"].isin(top_role_names)].pivot_table(index="Role", columns="Quarter", values="FTE", aggfunc="sum", fill_value=0)
            fig = go.Figure(go.Heatmap(
                z=heat.values, x=heat.columns.tolist(), y=heat.index.tolist(),
                colorscale=[[0.0, "#f8fafc"], [.2, "#dbeafe"], [.55, "#60a5fa"], [1.0, "#1d4ed8"]],
                colorbar=dict(title="FTE", thickness=14, len=.72),
                hovertemplate="%{y}<br>%{x}<br>%{z:.2f} active FTE<extra></extra>",
                xgap=1, ygap=1,
            ))
            fig.update_layout(title="Average active FTE by quarter")
            fig.update_xaxes(title=None, tickangle=-45, nticks=min(28, len(heat.columns)))
            fig.update_yaxes(title=None, autorange="reversed")
            _plot(fig, height=720)
    tabs = st.tabs(["Role summary", "Assignment browser", "Annual plan"])
    with tabs[0]:
        st.dataframe(roles, use_container_width=True, hide_index=True, height=520)
    with tabs[1]:
        assignment_df = assignments_frame(scenario["resource_assignments"])
        role_filter = st.multiselect("Role", sorted(assignment_df["Role"].dropna().unique()))
        if role_filter:
            assignment_df = assignment_df[assignment_df["Role"].isin(role_filter)]
        st.dataframe(assignment_df, use_container_width=True, hide_index=True, height=520)
    with tabs[2]:
        st.dataframe(annual, use_container_width=True, hide_index=True, height=500)

def financials_tab(database: dict[str, Any], scenario: dict[str, Any]) -> None:
    render_section_header("Financial plan", "Bottom-up task estimates, annual funding profile, labor and direct-cost composition, selected licensing route, and the controlled demonstrator package.", "Financials")
    summary = scenario["summary"]
    render_kpi_cards(
        [
            {"label": "Shared program", "value": format_money_kusd(summary["common_program_cost_kusd"]), "help": "Methods, experiments, engineering, build"},
            {"label": "DOE demonstrator route", "value": format_money_kusd(summary["demo_route_cost_kusd"]), "help": "Authorization activities"},
            {"label": "Commercial route", "value": format_money_kusd(summary["commercial_route_total_kusd"]), "help": "Selected licensing path"},
            {"label": "Labor", "value": format_money_kusd(summary["labor_cost_kusd"]), "help": "Loaded labor"},
            {"label": "Non-labor", "value": format_money_kusd(summary["non_labor_cost_kusd"]), "help": "Hardware and external cost"},
            {"label": "Total nominal case", "value": format_money_kusd(summary["total_cost_kusd"]), "help": "Integrated scenario"},
        ]
    )
    annual = annual_financial_frame(scenario)
    target_map = (scenario.get("planning_profile") or {}).get("annual_funding_target_musd") or {}
    annual["Planning target ($M)"] = annual["Year"].astype(str).map(lambda year: float(target_map.get(year, 0.0)))
    annual["Labor ($M)"] = annual["Labor Cost ($000)"] / 1000.0
    annual["Non-labor ($M)"] = annual["Non-Labor Cost ($000)"] / 1000.0
    annual["Total ($M)"] = annual["Total Cost ($000)"] / 1000.0
    fig = go.Figure()
    fig.add_bar(x=annual["Year"], y=annual["Labor ($M)"], name="Labor", marker_color=CHART_COLORS[0], hovertemplate="%{x}<br>Labor: $%{y:.1f}M<extra></extra>")
    fig.add_bar(x=annual["Year"], y=annual["Non-labor ($M)"], name="Non-labor", marker_color=CHART_COLORS[1], hovertemplate="%{x}<br>Non-labor: $%{y:.1f}M<extra></extra>")
    fig.add_scatter(x=annual["Year"], y=annual["Planning target ($M)"], mode="lines+markers", name="Planning target", line=dict(width=2.4, dash="dot", color="#64748b"), marker=dict(size=6), hovertemplate="%{x}<br>Planning target: $%{y:.1f}M<extra></extra>")
    peak = annual.loc[annual["Total ($M)"].idxmax()]
    fig.add_annotation(x=int(peak["Year"]), y=float(peak["Total ($M)"]), text=f"Peak ${float(peak['Total ($M)']):.1f}M", showarrow=True, arrowhead=2, ax=38, ay=-48, bgcolor="#ffffff", bordercolor="#cbd5e1", borderpad=4, font=dict(size=11, color="#0f172a"))
    fig.update_layout(barmode="stack", title="Annual cash flow - staged mobilization and later construction peak")
    fig.update_xaxes(dtick=1, title=None)
    fig.update_yaxes(title="Annual expenditure ($M)", ticksuffix="M", rangemode="tozero")
    _plot(fig, height=540)
    left, right = st.columns([1.15, 1])
    with left:
        stream = _consolidated_stream_frame(scenario).sort_values("Total Cost ($000)").copy()
        stream["Labor ($M)"] = stream["Labor Cost ($000)"] / 1000.0
        stream["Non-labor ($M)"] = stream["Non-Labor Cost ($000)"] / 1000.0
        fig = go.Figure()
        fig.add_bar(y=stream["Execution Stream"], x=stream["Labor ($M)"], name="Labor", orientation="h", marker_color=CHART_COLORS[0], hovertemplate="%{y}<br>Labor: $%{x:.1f}M<extra></extra>")
        fig.add_bar(y=stream["Execution Stream"], x=stream["Non-labor ($M)"], name="Non-labor", orientation="h", marker_color=CHART_COLORS[1], hovertemplate="%{y}<br>Non-labor: $%{x:.1f}M<extra></extra>")
        fig.update_layout(barmode="stack", title="Cost by execution stream")
        fig.update_xaxes(title="Cost ($M)", ticksuffix="M")
        fig.update_yaxes(title=None)
        _plot(fig, height=650)
    with right:
        route = route_cost_frame(scenario["tasks"])
        route_specific = route[route["Pathway Specific"]].sort_values("Total Cost ($000)").copy()
        route_specific["Labor ($M)"] = route_specific["Labor Cost ($000)"] / 1000.0
        route_specific["Non-labor ($M)"] = route_specific["Non-Labor Cost ($000)"] / 1000.0
        fig = go.Figure()
        fig.add_bar(y=route_specific["Scenario Route"], x=route_specific["Labor ($M)"], name="Labor", orientation="h", marker_color=CHART_COLORS[0], hovertemplate="%{y}<br>Labor: $%{x:.1f}M<extra></extra>")
        fig.add_bar(y=route_specific["Scenario Route"], x=route_specific["Non-labor ($M)"], name="Non-labor", orientation="h", marker_color=CHART_COLORS[2], hovertemplate="%{y}<br>Non-labor: $%{x:.1f}M<extra></extra>")
        fig.update_layout(barmode="stack", title="Authorization and licensing cost")
        fig.update_xaxes(title="Cost ($M)", ticksuffix="M")
        fig.update_yaxes(title=None)
        _plot(fig, height=650)
    render_section_header("Demonstrator direct package", "Direct non-labor hardware, installation, and startup remain controlled at $30 million.")
    demo_budget = database.get("financials", {}).get("demonstrator_direct_budget") or []
    budget_rows = demo_budget.get("rows") or demo_budget.get("items") or [] if isinstance(demo_budget, dict) else demo_budget
    if budget_rows:
        budget_df = pd.DataFrame(budget_rows)
        numeric = "Direct Non-Labor ($000)" if "Direct Non-Labor ($000)" in budget_df.columns else next((column for column in budget_df.select_dtypes(include="number").columns if column != "% of Cap"), None)
        label = "Direct Package" if "Direct Package" in budget_df.columns else next((column for column in budget_df.columns if any(token in column.lower() for token in ("category", "element"))), budget_df.columns[0])
        plot_df = budget_df[budget_df.get("WBS ID", pd.Series(index=budget_df.index, dtype=str)).astype(str) != "TOTAL"].copy() if "WBS ID" in budget_df.columns else budget_df.copy()
        if numeric:
            plot_df["Amount ($M)"] = pd.to_numeric(plot_df[numeric], errors="coerce").fillna(0.0) / 1000.0
            plot_df["Display package"] = plot_df[label].map(lambda value: _short_label(value, 58))
            plot_df = plot_df.sort_values("Amount ($M)")
            fig = go.Figure(go.Bar(
                x=plot_df["Amount ($M)"], y=plot_df["Display package"], orientation="h",
                marker=dict(color=plot_df["Amount ($M)"], colorscale=[[0, "#dbeafe"], [1, "#315efb"]], showscale=False, line=dict(width=1, color="#ffffff")),
                text=plot_df["Amount ($M)"], texttemplate="$%{text:.1f}M", textposition="outside", cliponaxis=False,
                customdata=plot_df[[label, "% of Cap"]].to_numpy() if "% of Cap" in plot_df.columns else plot_df[[label]].to_numpy(),
                hovertemplate="<b>%{customdata[0]}</b><br>Cost: $%{x:.1f}M<extra></extra>",
            ))
            fig.update_layout(title="Direct demonstrator package allocation", showlegend=False)
            fig.update_xaxes(title="Direct non-labor cost ($M)", ticksuffix="M", rangemode="tozero")
            fig.update_yaxes(title=None)
            _plot(fig, height=590)
        st.dataframe(budget_df, use_container_width=True, hide_index=True)

def cost_basis_tab(database: dict[str, Any], scenario: dict[str, Any]) -> None:
    render_section_header(
        "Task-level cost basis",
        "Bottom-up work-package estimates with loaded labor, direct external cost, explicit task risk, estimate ranges, and non-additive allocation of major engineering contracts to the detailed tasks they support.",
        "Cost basis",
    )
    frame = tasks_frame(scenario["tasks"])
    if frame.empty:
        st.write("No costed activities are available for the selected scenario.")
        return

    direct_total = float(frame["Direct Task Cost ($000)"].sum())
    labor_total = float(frame["Labor Cost ($000)"].sum())
    direct_nonlabor = float(frame["Direct Non-Labor Before Risk ($000)"].sum())
    risk_total = float(frame["Risk Allowance ($000)"].sum())
    changed = int((frame["Estimate Delta ($000)"].abs() > 0.01).sum())
    render_kpi_cards(
        [
            {"label": "Costed activities", "value": f"{len(frame):,}", "help": f"{changed:,} re-estimated from v4.1"},
            {"label": "Loaded labor", "value": format_money_kusd(labor_total), "help": "Producing, checking, integration, records, and task control"},
            {"label": "Direct non-labor", "value": format_money_kusd(direct_nonlabor), "help": "External services, tools, data, equipment, field work, and fees before risk"},
            {"label": "Task risk allowance", "value": format_money_kusd(risk_total), "help": "Explicit work-package uncertainty allowance"},
            {"label": "Accounting total", "value": format_money_kusd(direct_total), "help": "Additive program total for active tasks"},
        ]
    )

    filter_cols = st.columns([1, 1, 1, 1.4])
    with filter_cols[0]:
        concepts = st.multiselect("Concept", sorted(frame["Concept"].dropna().unique()), key="cost_concept_filter")
    with filter_cols[1]:
        scopes = st.multiselect("Task scope", sorted(frame["Task Scope"].dropna().unique()), key="cost_scope_filter")
    with filter_cols[2]:
        classes = st.multiselect("Estimate class", sorted(frame["Estimate Class"].dropna().unique()), key="cost_class_filter")
    with filter_cols[3]:
        query = st.text_input("Find activity", placeholder="Task ID, title, purpose, or domain", key="cost_task_query")

    filtered = frame.copy()
    if concepts:
        filtered = filtered[filtered["Concept"].isin(concepts)]
    if scopes:
        filtered = filtered[filtered["Task Scope"].isin(scopes)]
    if classes:
        filtered = filtered[filtered["Estimate Class"].isin(classes)]
    if query:
        q = query.strip().lower()
        searchable = (
            filtered["WBS ID"].astype(str)
            + " " + filtered["Task"].fillna("").astype(str)
            + " " + filtered["Purpose"].fillna("").astype(str)
            + " " + filtered["Engineering Domain"].fillna("").astype(str)
        ).str.lower()
        filtered = filtered[searchable.str.contains(q, regex=False)]

    top = filtered.nlargest(min(30, len(filtered)), "Fully Burdened Task View ($000)").sort_values("Fully Burdened Task View ($000)")
    left, right = st.columns([1.25, 1])
    with left:
        if not top.empty:
            plot_df = top.copy()
            plot_df["Direct task ($M)"] = plot_df["Direct Task Cost ($000)"] / 1000.0
            plot_df["Allocated contract share ($M)"] = plot_df["Allocated Program Package Share ($000)"] / 1000.0
            plot_df["Display task"] = plot_df.apply(lambda row: f"{row['WBS ID']} · {_short_label(row['Task'], 52)}", axis=1)
            fig = go.Figure()
            fig.add_bar(
                y=plot_df["Display task"], x=plot_df["Direct task ($M)"], orientation="h", name="Direct task estimate",
                marker_color=CHART_COLORS[0],
                customdata=plot_df[["WBS ID", "Task", "Estimate Class", "FTE-years"]].to_numpy(),
                hovertemplate="<b>%{customdata[0]} · %{customdata[1]}</b><br>Direct task: $%{x:.2f}M<br>Class: %{customdata[2]}<br>FTE-years: %{customdata[3]:.2f}<extra></extra>",
            )
            fig.add_bar(
                y=plot_df["Display task"], x=plot_df["Allocated contract share ($M)"], orientation="h", name="Allocated program-package share",
                marker_color=CHART_COLORS[3],
                customdata=plot_df[["WBS ID", "Task"]].to_numpy(),
                hovertemplate="<b>%{customdata[0]} · %{customdata[1]}</b><br>Non-additive allocated share: $%{x:.2f}M<extra></extra>",
            )
            fig.update_layout(barmode="stack", title="Largest fully burdened task views")
            fig.update_xaxes(title="Cost ($M)", ticksuffix="M", rangemode="tozero")
            fig.update_yaxes(title=None)
            _plot(fig, height=max(560, 26 * len(plot_df) + 170))
            st.caption("Allocated program-package shares provide task visibility but remain on the source package task in the accounting total.")
    with right:
        scope_rollup = (
            filtered.groupby("Task Scope", dropna=False, as_index=False)
            .agg(
                Activities=("WBS ID", "count"),
                **{
                    "Prior ($000)": ("Prior Total Cost ($000)", "sum"),
                    "Revised ($000)": ("Direct Task Cost ($000)", "sum"),
                },
            )
        )
        if not scope_rollup.empty:
            scope_rollup["Prior ($M)"] = scope_rollup["Prior ($000)"] / 1000.0
            scope_rollup["Revised ($M)"] = scope_rollup["Revised ($000)"] / 1000.0
            scope_rollup["Scope"] = scope_rollup["Task Scope"].astype(str).str.replace("_", " ").str.title()
            scope_rollup = scope_rollup.sort_values("Revised ($M)")
            fig = go.Figure()
            fig.add_bar(y=scope_rollup["Scope"], x=scope_rollup["Prior ($M)"], orientation="h", name="Prior v4.1", marker_color="#cbd5e1")
            fig.add_bar(y=scope_rollup["Scope"], x=scope_rollup["Revised ($M)"], orientation="h", name="Revised v4.2", marker_color=CHART_COLORS[2])
            fig.update_layout(barmode="group", title="Prior and revised task estimates by scope")
            fig.update_xaxes(title="Accounting cost ($M)", ticksuffix="M")
            fig.update_yaxes(title=None)
            _plot(fig, height=620)

    render_section_header("Costed work-package register", f"{len(filtered):,} activities match the current filters.")
    display_columns = [
        "WBS ID", "Task", "Concept", "Task Scope", "Engineering Domain", "Start", "Finish",
        "FTE-years", "Planned Labor Hours", "Labor Cost ($000)", "Direct Non-Labor Before Risk ($000)",
        "Risk Allowance ($000)", "Direct Task Cost ($000)", "Allocated Program Package Share ($000)",
        "Fully Burdened Task View ($000)", "Low Estimate ($000)", "High Estimate ($000)",
        "Prior Total Cost ($000)", "Estimate Delta ($000)", "Estimate Class", "Basis of Estimate ID",
    ]
    st.dataframe(filtered[display_columns], use_container_width=True, hide_index=True, height=560)
    st.download_button(
        "Download filtered task-cost register",
        filtered[display_columns].to_csv(index=False).encode("utf-8"),
        "project_msr_task_cost_register.csv",
        "text/csv",
        use_container_width=True,
        key="download_filtered_task_cost_register",
    )

    if not filtered.empty:
        task_ids = filtered["WBS ID"].astype(str).tolist()
        selected = st.selectbox(
            "Open complete cost and engineering work package",
            task_ids,
            format_func=lambda task_id: f"{task_id} · {next(task['name'] for task in scenario['tasks'] if str(task['id']) == task_id)}",
            key="cost_basis_task_select",
        )
        selected_task = next(task for task in scenario["tasks"] if str(task["id"]) == selected)
        render_task_detail(selected_task)


def experiments_tab(scenario: dict[str, Any]) -> None:
    render_section_header("Experimental evidence program", "Task-based methods qualification, integral thermal-hydraulics, INL critical experiment, demonstrator testing, and validation evidence.", "Experiments")
    experiment_scopes = {"integral_test_facility", "critical_experiment", "demonstrator_experiments", "methods_and_topicals"}
    tasks = [task for task in scenario["tasks"] if task.get("task_scope") in experiment_scopes]
    frame = tasks_frame(tasks)
    if not frame.empty:
        scope_rollup = frame.groupby("Task Scope", as_index=False).agg(Activities=("WBS ID", "count"), **{"FTE-years": ("FTE-years", "sum"), "Total Cost ($000)": ("Total Cost ($000)", "sum"), "Start": ("Start", "min"), "Finish": ("Finish", "max")})
        scope_labels = {
            "methods_and_topicals": "Methods, validation & topicals",
            "integral_test_facility": "Integral thermal-hydraulics facility",
            "critical_experiment": "INL critical experiment",
            "demonstrator_experiments": "Demonstrator experimental campaign",
        }
        scope_rollup["Evidence stream"] = scope_rollup["Task Scope"].map(scope_labels).fillna(scope_rollup["Task Scope"])
        scope_rollup["Cost ($M)"] = scope_rollup["Total Cost ($000)"] / 1000.0
        chart_df = scope_rollup.sort_values("Cost ($M)")
        fig = px.bar(
            chart_df,
            x="Cost ($M)",
            y="Evidence stream",
            orientation="h",
            text="Cost ($M)",
            color="FTE-years",
            color_continuous_scale=["#dbeafe", "#0f9f8f"],
            hover_data={"Activities": True, "FTE-years": ":.1f", "Start": "|%b %Y", "Finish": "|%b %Y", "Task Scope": False, "Total Cost ($000)": False},
            title="Experimental and methods investment by evidence stream",
        )
        fig.update_traces(texttemplate="$%{x:.1f}M", textposition="outside", cliponaxis=False)
        fig.update_xaxes(title="Cost ($M)", ticksuffix="M")
        fig.update_yaxes(title=None)
        fig.update_layout(coloraxis_colorbar=dict(title="FTE-yr", thickness=14, len=.65))
        _plot(fig, height=440)
        display_rollup = scope_rollup.copy()
        display_rollup["Start"] = display_rollup["Start"].dt.date
        display_rollup["Finish"] = display_rollup["Finish"].dt.date
        st.dataframe(display_rollup[["Evidence stream", "Activities", "FTE-years", "Total Cost ($000)", "Start", "Finish"]], use_container_width=True, hide_index=True, height=260)
    tabs = st.tabs(["Methods and topicals", "Integral thermal-hydraulics", "INL critical experiment", "Demonstrator testing", "Validation matrix"])
    scopes = ["methods_and_topicals", "integral_test_facility", "critical_experiment", "demonstrator_experiments"]
    for tab, scope in zip(tabs[:4], scopes):
        with tab:
            subset = [task for task in tasks if task.get("task_scope") == scope]
            df = tasks_frame(subset)
            if not df.empty:
                st.dataframe(df[["WBS ID", "Task", "Engineering Domain", "Start", "Finish", "FTE-years", "Total Cost ($000)", "Purpose"]], use_container_width=True, hide_index=True, height=480)
                selected = st.selectbox("Open work package", [task["id"] for task in subset], format_func=lambda task_id: f"{task_id} · {next(task['name'] for task in subset if task['id'] == task_id)}", key=f"exp_{scope}")
                render_task_detail(next(task for task in subset if task["id"] == selected))
    with tabs[4]:
        matrix = scenario.get("test_matrices", {}).get("integral_thermal_hydraulics") or []
        matrix_df = pd.DataFrame(matrix)
        if not matrix_df.empty:
            query = st.text_input("Search validation matrix", key="matrix_search")
            if query:
                mask = matrix_df.astype(str).apply(lambda column: column.str.contains(query, case=False, na=False)).any(axis=1)
                matrix_df = matrix_df[mask]
            st.dataframe(matrix_df, use_container_width=True, hide_index=True, height=420)
            row_keys = list(matrix_df.index)
            selected_index = st.selectbox("Open test definition", row_keys, format_func=lambda idx: " · ".join(str(matrix_df.loc[idx, col]) for col in list(matrix_df.columns)[:2]), key="matrix_row")
            selected_row = matrix_df.loc[selected_index]
            with st.expander("Selected test - execution-ready definition", expanded=True):
                columns = st.columns(2)
                for position, (field, value) in enumerate(selected_row.items()):
                    with columns[position % 2]:
                        st.markdown(f"**{str(field).replace('_', ' ').title()}**")
                        if isinstance(value, (list, dict)):
                            st.write(value)
                        else:
                            st.write(str(value))

def implementation_tab(database: dict[str, Any], scenario: dict[str, Any]) -> None:
    playbooks = database.get("implementation_playbooks") or {}
    chemistry = database.get("chemistry_processing_plan") or {}
    fuel = database.get("fuel_supply_plan") or {}
    active_tasks = scenario.get("tasks") or []
    implementation_tasks = [task for task in active_tasks if task.get("implementation_plan")]
    chemistry_tests = chemistry.get("experiment_matrix") or []
    render_section_header(
        "Implementation playbooks and execution plans",
        "Concrete fuel-supply, chemistry, processing, procurement, facility, field-work, acceptance, and contingency plans cross-walked to the active WBS.",
        "Implementation",
    )
    render_kpi_cards([
        {"label": "Active execution plans", "value": f"{len(implementation_tasks):,}", "help": "Scenario tasks with implementation detail"},
        {"label": "Program playbooks", "value": f"{len(playbooks):,}", "help": "Cross-cutting execution playbooks"},
        {"label": "Chemistry tests", "value": f"{len(chemistry_tests):,}", "help": "Defined validation experiments"},
        {"label": "Fuel phases", "value": f"{len(fuel.get('execution_phases') or []):,}", "help": "Requirements through disposition"},
    ])

    closure_register = database.get("implementation_closure_register") or []
    fuel_tab, chemistry_tab, playbook_tab, closure_tab, register_tab = st.tabs([
        "Fuel supply and procurement",
        "Chemistry and salt processing",
        "Other implementation playbooks",
        "Closure register",
        "Task execution register",
    ])

    with fuel_tab:
        st.markdown("### Recommended fuel-supply baseline")
        st.write(fuel.get("recommended_baseline") or fuel.get("objective") or "—")
        branches = fuel.get("technology_branching") or []
        if branches:
            st.markdown("#### Technology branches and licensing boundary")
            _fuel_cols = st.columns(2)
            for idx, value in enumerate(branches):
                with _fuel_cols[idx % 2]:
                    st.markdown(f"**Branch {idx+1}**")
                    render_note(str(value))
        phase_records = fuel.get("execution_phases") or []
        phase_rows = []
        for phase in phase_records:
            phase_rows.append({
                "Phase ID": phase.get("phase_id"),
                "Phase": phase.get("phase"),
                "Window": phase.get("window"),
                "Action count": len(phase.get("actions") or []),
                "Deliverable count": len(phase.get("deliverables") or []),
                "Release gate": phase.get("gate"),
            })
        if phase_rows:
            st.markdown("#### End-to-end execution sequence")
            st.dataframe(pd.DataFrame(phase_rows), use_container_width=True, hide_index=True, height=340)
            phase_ids = [str(item.get("phase_id")) for item in phase_records]
            selected_phase_id = st.selectbox(
                "Open fuel-supply phase",
                phase_ids,
                format_func=lambda pid: f"{pid} · {next(item.get('phase','') for item in phase_records if str(item.get('phase_id')) == pid)}",
                key="impl_fuel_phase",
            )
            selected_phase = next(item for item in phase_records if str(item.get("phase_id")) == selected_phase_id)
            with st.expander(f"{selected_phase_id} · execution instructions", expanded=True):
                st.markdown(f"**Window:** {selected_phase.get('window') or '—'}")
                phase_cols = st.columns(2)
                with phase_cols[0]:
                    st.markdown("**Actions**")
                    for item in selected_phase.get("actions") or []:
                        st.markdown(f"- {item}")
                with phase_cols[1]:
                    st.markdown("**Required deliverables**")
                    for item in selected_phase.get("deliverables") or []:
                        st.markdown(f"- {item}")
                    st.markdown("**Release gate**")
                    render_note(str(selected_phase.get("gate") or "—"))
        routes = pd.DataFrame(fuel.get("candidate_supply_routes") or [])
        if not routes.empty:
            st.markdown("#### Candidate source routes")
            st.dataframe(routes, use_container_width=True, hide_index=True, height=300)
        st.markdown("#### Fuel acceptance data required before use")
        for item in fuel.get("required_acceptance_data") or []:
            st.markdown(f"- {item}")
        linked_ids = set(fuel.get("linked_task_ids") or [])
        linked = [task for task in active_tasks if task.get("id") in linked_ids]
        if linked:
            st.markdown("#### Fuel-supply WBS crosswalk")
            linked_df = tasks_frame(linked)
            st.dataframe(linked_df[["WBS ID","Task","Concept","Start","Finish","Total Cost ($000)","Implementation Summary"]], use_container_width=True, hide_index=True, height=360)
            selected = st.selectbox("Open fuel work package", [task["id"] for task in linked], format_func=lambda tid: f"{tid} · {next(t['name'] for t in linked if t['id']==tid)}", key="impl_fuel_task")
            render_task_detail(next(task for task in linked if task["id"] == selected))

    with chemistry_tab:
        st.markdown("### Chemistry and processing architecture")
        st.write(chemistry.get("objective") or "—")
        decision = chemistry.get("architecture_decision") or {}
        if decision:
            st.markdown(f"**{str(decision.get("question") or "Architecture decision")}**")
            render_note(str(decision.get("rule") or ""))
            decision_cols = st.columns(2)
            with decision_cols[0]:
                st.markdown("#### Alternatives")
                for item in decision.get("alternatives") or []:
                    st.markdown(f"- {item}")
            with decision_cols[1]:
                st.markdown("#### Decision criteria")
                for item in decision.get("decision_criteria") or []:
                    st.markdown(f"- {item}")
                st.markdown("**Required by**")
                st.write(decision.get("required_date") or "—")
        sequence = chemistry.get("campaign_sequence") or []
        if sequence:
            st.markdown("#### Evidence ladder")
            sequence_df = pd.DataFrame([{"Stage": i+1, "Campaign": item} for i,item in enumerate(sequence)])
            st.dataframe(sequence_df, use_container_width=True, hide_index=True, height=min(430, 85 + 48*len(sequence_df)))

        test_df = pd.DataFrame(chemistry_tests)
        if not test_df.empty:
            filters = st.columns([1.2,1,1])
            query = filters[0].text_input("Search experiments", key="chem_impl_search")
            campaign = filters[1].multiselect("Campaign", sorted(test_df["campaign"].dropna().unique()), key="chem_impl_campaign")
            stage = filters[2].multiselect("Material stage", sorted(test_df["material_stage"].dropna().unique()), key="chem_impl_stage")
            view = test_df.copy()
            if query:
                mask = view.astype(str).apply(lambda col: col.str.contains(query, case=False, na=False)).any(axis=1)
                view = view[mask]
            if campaign:
                view = view[view["campaign"].isin(campaign)]
            if stage:
                view = view[view["material_stage"].isin(stage)]
            display_cols = ["test_id","campaign","objective","material_stage","planned_window","facility_strategy","acceptance_basis"]
            st.dataframe(view[display_cols], use_container_width=True, hide_index=True, height=520)
            if not view.empty:
                ids = view["test_id"].tolist()
                selected_id = st.selectbox("Open experiment definition", ids, format_func=lambda tid: f"{tid} · {view.loc[view['test_id']==tid,'campaign'].iloc[0]}", key="chem_impl_test")
                record = next(row for row in chemistry_tests if row.get("test_id") == selected_id)
                with st.expander(f"{selected_id} · execution-ready experiment", expanded=True):
                    c1,c2 = st.columns(2)
                    with c1:
                        for label,key in [("Objective","objective"),("Configuration","configuration"),("Material progression","material_stage"),("Facility strategy","facility_strategy"),("Planned window","planned_window")]:
                            st.markdown(f"**{label}**")
                            st.write(record.get(key) or "—")
                        st.markdown("**Primary measurements**")
                        for item in record.get("primary_measurements") or []: st.markdown(f"- {item}")
                    with c2:
                        st.markdown("**Analytical methods**")
                        for item in record.get("analytical_methods") or []: st.markdown(f"- {item}")
                        st.markdown("**Acceptance basis**")
                        st.write(record.get("acceptance_basis") or "—")
                        st.markdown("**Models / decisions supported**")
                        for item in record.get("model_or_decision_supported") or []: st.markdown(f"- {item}")
                        st.markdown("**Required records**")
                        for item in record.get("required_records") or []: st.markdown(f"- {item}")
                    linked_ids = set(record.get("linked_task_ids") or [])
                    linked = [task for task in active_tasks if task.get("id") in linked_ids]
                    st.markdown("#### Minimum execution sequence")
                    sequence_rows = [
                        {"Step": idx + 1, "Instruction": value}
                        for idx, value in enumerate(record.get("minimum_test_sequence") or [])
                    ]
                    if sequence_rows:
                        st.dataframe(pd.DataFrame(sequence_rows), use_container_width=True, hide_index=True, height=min(520, 90 + 54 * len(sequence_rows)))
                    detail_tabs = st.tabs(["Controls & equipment", "Replicates & samples", "Stop conditions", "Data & decision"])
                    with detail_tabs[0]:
                        detail_cols = st.columns(2)
                        with detail_cols[0]:
                            st.markdown("**Controlled variables**")
                            for item in record.get("controlled_variables") or []:
                                st.markdown(f"- {item}")
                        with detail_cols[1]:
                            st.markdown("**Equipment and consumables**")
                            for item in record.get("equipment_and_consumables") or []:
                                st.markdown(f"- {item}")
                    with detail_tabs[1]:
                        st.markdown("**Replication and uncertainty strategy**")
                        st.write(record.get("replicate_and_uncertainty_strategy") or "—")
                        st.markdown("**Sample and archive plan**")
                        st.write(record.get("sample_and_archive_plan") or "—")
                    with detail_tabs[2]:
                        for item in record.get("stop_conditions") or []:
                            st.markdown(f"- {item}")
                    with detail_tabs[3]:
                        st.markdown("**Required data products**")
                        for item in record.get("data_products") or []:
                            st.markdown(f"- {item}")
                        st.markdown("**Decision rule**")
                        render_note(str(record.get("decision_rule") or "—"))
                    if linked:
                        st.markdown("**Linked WBS tasks**")
                        st.dataframe(tasks_frame(linked)[["WBS ID","Task","Start","Finish","Implementation Summary"]], use_container_width=True, hide_index=True, height=min(300, 80 + 50*len(linked)))

    with playbook_tab:
        keys = [key for key in playbooks if key not in {"PB-FUEL-01","PB-CHEM-01"}]
        selected_key = st.selectbox("Implementation playbook", keys, format_func=lambda key: f"{key} · {playbooks[key].get('title','')}", key="implementation_playbook")
        playbook = playbooks[selected_key]
        st.markdown(f"### {playbook.get('title')}")
        st.write(playbook.get("objective") or "—")
        sequence = playbook.get("execution_sequence") or playbook.get("campaign_sequence") or []
        if sequence:
            st.dataframe(pd.DataFrame([{"Step": i+1,"Execution sequence": value} for i,value in enumerate(sequence)]), use_container_width=True, hide_index=True, height=min(460, 90+52*len(sequence)))
        linked_ids = set(playbook.get("linked_task_ids") or [])
        linked = [task for task in active_tasks if task.get("id") in linked_ids]
        if linked:
            st.markdown("#### Linked active work packages")
            st.dataframe(tasks_frame(linked)[["WBS ID","Task","Engineering Domain","Start","Finish","Implementation Summary"]], use_container_width=True, hide_index=True, height=440)
        if playbook.get("source_urls"):
            st.markdown("#### Source and precedent links")
            for url in playbook.get("source_urls") or []:
                st.code(url, language=None)

    with closure_tab:
        st.markdown("### Decisions and commitments required to convert the planning basis into a committed execution baseline")
        if closure_register:
            closure_df = pd.DataFrame(closure_register)
            rename_map = {
                "closure_id": "ID",
                "closure_item": "Closure item",
                "work_required": "Work required",
                "accountable_functions": "Accountable functions",
                "need_date": "Need date",
                "closure_evidence": "Closure evidence",
                "status": "Status",
            }
            closure_df = closure_df.rename(columns=rename_map)
            display_columns = [col for col in ["ID", "Closure item", "Need date", "Status", "Accountable functions", "Closure evidence"] if col in closure_df.columns]
            st.dataframe(closure_df[display_columns], use_container_width=True, hide_index=True, height=420)
            closure_ids = closure_df["ID"].astype(str).tolist()
            selected_closure = st.selectbox(
                "Open closure item",
                closure_ids,
                format_func=lambda cid: f"{cid} · {closure_df.loc[closure_df['ID'].astype(str) == cid, 'Closure item'].iloc[0]}",
                key="impl_closure_item",
            )
            selected_record = closure_df.loc[closure_df["ID"].astype(str) == selected_closure].iloc[0]
            with st.expander(f"{selected_closure} · closure instructions", expanded=True):
                st.markdown("**Work required**")
                st.write(selected_record.get("Work required") or "—")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Accountable functions**")
                    st.write(selected_record.get("Accountable functions") or "—")
                    st.markdown("**Need date**")
                    st.write(selected_record.get("Need date") or "—")
                with c2:
                    st.markdown("**Closure evidence**")
                    st.write(selected_record.get("Closure evidence") or "—")
                    st.markdown("**Status**")
                    st.write(selected_record.get("Status") or "—")
        else:
            st.info("No program-level closure register is present in the loaded database.")

    with register_tab:
        frame = tasks_frame(implementation_tasks)
        controls = st.columns([1.2,1,1])
        query = controls[0].text_input("Search implementation plans", key="impl_register_search")
        domains = controls[1].multiselect("Engineering domain", sorted(frame["Engineering Domain"].dropna().unique()), key="impl_register_domain")
        playbook_options = sorted({pb for task in implementation_tasks for pb in (task.get("implementation_plan") or {}).get("linked_playbooks",[])})
        selected_playbooks = controls[2].multiselect("Linked playbook", playbook_options, key="impl_register_playbook")
        view = frame.copy()
        if query:
            mask = view[["WBS ID","Task","Implementation Summary","Implementation Readiness"]].astype(str).apply(lambda col: col.str.contains(query, case=False, na=False)).any(axis=1)
            view = view[mask]
        if domains:
            view = view[view["Engineering Domain"].isin(domains)]
        if selected_playbooks:
            view = view[view["Linked Playbooks"].apply(lambda value: any(pb in str(value) for pb in selected_playbooks))]
        cols = ["WBS ID","Task","Concept","Engineering Domain","Start","Finish","Implementation Steps Count","Long-Lead Items Count","Decision Points Count","Linked Playbooks","Implementation Summary"]
        st.dataframe(view[cols], use_container_width=True, hide_index=True, height=560)
        st.download_button(
            "Download filtered implementation register",
            data=view.to_csv(index=False).encode("utf-8"),
            file_name="project_msr_implementation_register.csv",
            mime="text/csv",
            key="download_impl_register",
        )
        if not view.empty:
            ids = view["WBS ID"].astype(str).tolist()
            selected = st.selectbox("Open implementation-ready task", ids, format_func=lambda tid: f"{tid} · {next(t['name'] for t in implementation_tasks if str(t['id'])==tid)}", key="impl_register_task")
            render_task_detail(next(task for task in implementation_tasks if str(task["id"]) == selected))

def risks_gates_tab(scenario: dict[str, Any]) -> None:
    render_section_header("Risks, decision gates, and responsibility", "Integrated risk register, design/readiness gates, organizational assignments, and RACI.", "Controls")
    risks = risks_frame(scenario["risks"])
    risk_tab, gate_tab, governance_tab = st.tabs(["Risk register", "Design and readiness gates", "Organization and RACI"])
    with risk_tab:
        if not risks.empty:
            filters = st.columns(3)
            categories = filters[0].multiselect("Category", sorted(risks["Category"].dropna().unique()))
            pathways = filters[1].multiselect("Pathway", sorted(risks["Pathway"].dropna().unique()))
            text = filters[2].text_input("Risk text contains")
            view = risks.copy()
            if categories:
                view = view[view["Category"].isin(categories)]
            if pathways:
                view = view[view["Pathway"].isin(pathways)]
            if text:
                view = view[view["Risk"].str.contains(text, case=False, na=False)]
            st.dataframe(view, use_container_width=True, hide_index=True, height=680)
    with gate_tab:
        gates = pd.DataFrame(scenario.get("design_review_gates") or [])
        if not gates.empty:
            st.dataframe(gates, use_container_width=True, hide_index=True, height=620)
        milestones = milestones_frame(scenario["milestones"])
        show = milestones.copy()
        show["Baseline Date"] = show["Baseline Date"].dt.date
        render_section_header("Authorization and readiness milestones")
        st.dataframe(show, use_container_width=True, hide_index=True, height=430)
    with governance_tab:
        governance = pd.DataFrame(scenario.get("leadership_governance") or [])
        if not governance.empty:
            st.dataframe(governance, use_container_width=True, hide_index=True, height=440)
        raci = pd.DataFrame(scenario.get("raci") or [])
        if not raci.empty:
            render_section_header("RACI")
            st.dataframe(raci, use_container_width=True, hide_index=True, height=460)


def _xlsx_bytes(scenario: dict[str, Any]) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for name, frame in scenario_export_tables(scenario).items():
            frame.to_excel(writer, sheet_name=name[:31], index=False)
        pd.DataFrame([scenario["summary"]]).to_excel(writer, sheet_name="Scenario Summary", index=False)
    return output.getvalue()


def data_export_tab(database: dict[str, Any], scenario: dict[str, Any], source_name: str, database_fp: str) -> None:
    render_section_header("Data, traceability, and export", "Download the active scenario and its engineering work-package registers for analysis, review, or downstream planning tools.", "Data")
    quality = database.get("data_quality") or {}
    render_kpi_cards(
        [
            {"label": "Database version", "value": database.get("meta", {}).get("version", "-"), "help": source_name},
            {"label": "Shared tasks", "value": f"{quality.get('base_task_count', len(database.get('tasks', []))):,}", "help": "Baseline program"},
            {"label": "Route tasks", "value": f"{quality.get('route_task_count', 0):,}", "help": "Path-specific modules"},
            {"label": "Engineering-ready", "value": f"{quality.get('engineering_ready_task_count', 0):,}", "help": "Structured work packages"},
            {"label": "Resource roles", "value": f"{quality.get('role_count', len(database.get('resources', {}).get('roles', []))):,}", "help": "Labor model"},
            {"label": "Fingerprint", "value": database_fp, "help": "Loaded database"},
        ]
    )

    scenario_json = json.dumps(scenario, indent=2).encode("utf-8")
    tasks_csv = tasks_frame(scenario["tasks"]).to_csv(index=False).encode("utf-8")
    resources_csv = assignments_frame(scenario["resource_assignments"]).to_csv(index=False).encode("utf-8")
    milestones_csv = milestones_frame(scenario["milestones"]).to_csv(index=False).encode("utf-8")
    task_cost_csv = tasks_frame(scenario["tasks"]).to_csv(index=False).encode("utf-8")
    cols = st.columns(5)
    cols[0].download_button("Scenario JSON", scenario_json, "project_msr_active_scenario.json", "application/json", use_container_width=True)
    cols[1].download_button("Tasks CSV", tasks_csv, "project_msr_tasks.csv", "text/csv", use_container_width=True)
    cols[2].download_button("Task costs CSV", task_cost_csv, "project_msr_task_costs.csv", "text/csv", use_container_width=True)
    cols[3].download_button("Resources CSV", resources_csv, "project_msr_resources.csv", "text/csv", use_container_width=True)
    cols[4].download_button("Milestones CSV", milestones_csv, "project_msr_milestones.csv", "text/csv", use_container_width=True)

    st.markdown("#### Integrated Excel export")
    st.caption("The implementation-ready workbook is generated on demand because it contains the complete task, execution-step, input, requirement, tool, deliverable, decision, long-lead, and resource registers.")
    if st.button("Prepare scenario Excel workbook", use_container_width=True, key="prepare_scenario_excel"):
        with st.spinner("Building the complete scenario workbook..."):
            st.session_state["_project_msr_scenario_xlsx"] = _xlsx_bytes(scenario)
    if st.session_state.get("_project_msr_scenario_xlsx"):
        st.download_button(
            "Download prepared scenario Excel",
            st.session_state["_project_msr_scenario_xlsx"],
            "project_msr_active_scenario.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="download_prepared_scenario_excel",
        )

    tabs = st.tabs(["Scenario configuration", "Engineering package registers", "Source register"])
    with tabs[0]:
        st.json(scenario["meta"], expanded=False)
    with tabs[1]:
        frames = engineering_work_package_frames(scenario["tasks"])
        selected = st.selectbox("Register", list(frames))
        st.dataframe(frames[selected], use_container_width=True, hide_index=True, height=620)
    with tabs[2]:
        sources = pd.DataFrame(database.get("sources") or [])
        if not sources.empty:
            st.dataframe(sources, use_container_width=True, hide_index=True, height=620)


def main() -> None:
    if not require_authentication():
        return
    render_sidebar_brand()
    render_logout_control()
    database, source_name = select_database()
    database_fp = _fingerprint(database)
    options = scenario_controls(database)
    try:
        scenario = build_scenario(database, options)
    except ScenarioError as exc:
        st.error(f"Scenario build failed: {exc}")
        st.stop()

    st.sidebar.divider()
    st.sidebar.markdown("### Active scenario")
    st.sidebar.caption(f"Demonstrator · {route_label(database, DEMONSTRATOR_PATH, options.demonstrator_variant)}")
    st.sidebar.caption(f"Commercial · {PATH_DISPLAY_NAMES[options.power_reactor_path]} / {route_label(database, options.power_reactor_path, options.power_reactor_variant)}")
    if options.power_reactor_path == "part57" and options.part57_mode == "current_with_fallback":
        st.sidebar.caption(f"Fallback · {PATH_DISPLAY_NAMES[options.part57_fallback_path]} / {route_label(database, options.part57_fallback_path, options.part57_fallback_variant)}")
    st.sidebar.caption(f"Database v{database.get('meta', {}).get('version')} · {database_fp}")

    chips = [
        f"Demo: {route_label(database, DEMONSTRATOR_PATH, options.demonstrator_variant)}",
        f"Commercial: {PATH_DISPLAY_NAMES[options.power_reactor_path]}",
        f"Target: demonstrator built {scenario['summary']['demonstrator_mechanical_completion_target']}",
    ]
    render_hero(
        "Project-MSR Integrated Development Planner",
        "Scenario-driven engineering, experimental evidence, DOE demonstrator authorization, commercial licensing, resources, financials, construction, startup, and operating optimization.",
        chips=chips,
    )
    top_metrics(scenario)

    page = st.segmented_control("Planner section", NAV_ITEMS, default="Overview", label_visibility="collapsed", key="planner_section")
    if page == "Overview":
        overview_tab(database, scenario, options)
    elif page == "Pathway comparison":
        comparison_tab(database, database_fp)
    elif page == "Licensing plan":
        licensing_tab(database, scenario, options)
    elif page == "Pathway graph":
        pathway_graph_tab(database, scenario, options)
    elif page == "Schedule":
        schedule_tab(scenario)
    elif page == "Work packages":
        work_packages_tab(scenario)
    elif page == "Resources":
        resources_tab(scenario)
    elif page == "Financials":
        financials_tab(database, scenario)
    elif page == "Cost basis":
        cost_basis_tab(database, scenario)
    elif page == "Experiments":
        experiments_tab(scenario)
    elif page == "Implementation":
        implementation_tab(database, scenario)
    elif page == "Risks & gates":
        risks_gates_tab(scenario)
    elif page == "Data & export":
        data_export_tab(database, scenario, source_name, database_fp)


if __name__ == "__main__":
    main()
