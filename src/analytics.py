from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from typing import Any

import pandas as pd


def _date(value: Any) -> pd.Timestamp:
    return pd.to_datetime(value, errors="coerce")


def tasks_frame(tasks: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for task in tasks:
        schedule = task.get("schedule") or {}
        cost = task.get("cost") or {}
        resources = task.get("resources") or {}
        execution = task.get("execution") or {}
        package = task.get("engineering_work_package") or {}
        implementation = task.get("implementation_plan") or {}
        rows.append(
            {
                "WBS ID": task.get("id"),
                "Task": task.get("name"),
                "Concept": task.get("concept"),
                "Stream ID": task.get("stream_id"),
                "Execution Stream": task.get("execution_stream"),
                "Phase": task.get("phase"),
                "Task Scope": task.get("task_scope"),
                "Responsible Role": task.get("responsible_role"),
                "Start": _date(schedule.get("start")),
                "Finish": _date(schedule.get("finish")),
                "Duration (months)": float(schedule.get("duration_months") or 0.0),
                "Predecessors": ", ".join(schedule.get("predecessors") or []),
                "Critical": bool(schedule.get("critical")),
                "Gate": schedule.get("gate"),
                "Labor Cost ($000)": float(cost.get("labor_kusd") or 0.0),
                "Direct Non-Labor Before Risk ($000)": float(cost.get("direct_non_labor_before_risk_kusd") or 0.0),
                "Risk Allowance ($000)": float(cost.get("risk_allowance_kusd") or 0.0),
                "Non-Labor Cost ($000)": float(cost.get("non_labor_kusd") or 0.0),
                "Direct Task Cost ($000)": float(cost.get("total_kusd") or 0.0),
                "Allocated Program Package Share ($000)": float(cost.get("allocated_program_package_kusd") or 0.0),
                "Fully Burdened Task View ($000)": float(cost.get("fully_burdened_task_view_kusd") or cost.get("total_kusd") or 0.0),
                "Total Cost ($000)": float(cost.get("total_kusd") or 0.0),
                "Low Estimate ($000)": float(cost.get("low_kusd") or 0.0),
                "High Estimate ($000)": float(cost.get("high_kusd") or 0.0),
                "Prior Total Cost ($000)": float((cost.get("prior_estimate") or {}).get("total_kusd") or 0.0),
                "Estimate Delta ($000)": float((cost.get("estimate_change") or {}).get("total_delta_kusd") or 0.0),
                "Estimate Change (%)": (cost.get("estimate_change") or {}).get("total_change_pct"),
                "Estimate Class": cost.get("estimate_class"),
                "Estimate Method": cost.get("estimate_method"),
                "Basis of Estimate ID": cost.get("basis_of_estimate_id"),
                "Planned Labor Hours": float(cost.get("planned_labor_hours") or 0.0),
                "Blended Loaded Rate ($000/FTE-year)": float(cost.get("blended_loaded_rate_kusd_per_fte_year") or 0.0),
                "FTE-years": float(resources.get("fte_years") or 0.0),
                "Average FTE": float(resources.get("avg_fte") or 0.0),
                "Work Type": resources.get("work_type"),
                "Pathway Specific": bool(task.get("pathway_specific")),
                "Scenario Route": task.get("scenario_route") or "Shared program baseline",
                "Optional": bool(task.get("optional")),
                "Purpose": package.get("objective") or execution.get("purpose") or task.get("description"),
                "Description": task.get("description"),
                "Engineering Domain": package.get("primary_domain"),
                "Supporting Domains": ", ".join(package.get("supporting_domains") or []),
                "Work Pattern": package.get("work_pattern"),
                "Engineering Ready": bool(execution.get("engineering_ready") or package),
                "Entry Criteria Count": len(package.get("entry_criteria") or []),
                "Controlled Inputs Count": len(package.get("controlled_inputs") or []),
                "Procedure Steps Count": len(package.get("execution_procedure") or []),
                "Requirements Count": len(package.get("requirements_and_guidance") or []),
                "Tools Count": len(package.get("toolchain") or []),
                "Outputs Count": len(package.get("deliverable_register") or []),
                "Deliverables": "\n".join(execution.get("deliverables_and_records") or []),
                "Acceptance Criteria": "\n".join(execution.get("acceptance_exit_criteria") or []),
                "Regulatory Basis": task.get("regulatory_basis"),
                "Implementation Ready": bool(implementation),
                "Implementation Readiness": implementation.get("implementation_readiness"),
                "Implementation Summary": implementation.get("implementation_summary"),
                "Implementation Steps Count": len(implementation.get("implementation_steps") or []),
                "Procurement Actions Count": len(implementation.get("procurement_and_contracting_actions") or []),
                "Long-Lead Items Count": len(implementation.get("long_lead_items") or []),
                "Decision Points Count": len(implementation.get("decision_points") or []),
                "Linked Playbooks": ", ".join(implementation.get("linked_playbooks") or []),
            }
        )
    frame = pd.DataFrame(rows)
    if not frame.empty:
        frame = frame.sort_values(["Start", "Stream ID", "WBS ID"], kind="stable").reset_index(drop=True)
    return frame


def assignments_frame(assignments: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for row in assignments:
        rows.append(
            {
                "Assignment ID": row.get("assignment_id"),
                "WBS ID": row.get("task_id"),
                "Concept": row.get("concept"),
                "Role ID": row.get("role_id"),
                "Role": row.get("role"),
                "Work Type": row.get("work_type"),
                "Start": _date(row.get("start")),
                "Finish": _date(row.get("finish")),
                "Average FTE": float(row.get("avg_fte") or 0.0),
                "FTE-years": float(row.get("fte_years") or 0.0),
                "Loaded Rate ($000/FTE-year)": float(row.get("loaded_rate_kusd_per_fte_year") or 0.0),
                "Labor Cost ($000)": float(row.get("labor_cost_kusd") or 0.0),
                "Scenario Route": row.get("scenario_route") or ("Route-specific" if row.get("route_specific") else "Shared program baseline"),
            }
        )
    frame = pd.DataFrame(rows)
    if not frame.empty:
        frame = frame.sort_values(["Role", "Start", "WBS ID"], kind="stable").reset_index(drop=True)
    return frame


def annual_financial_frame(scenario: dict[str, Any]) -> pd.DataFrame:
    years = sorted(
        set(scenario.get("annual_cost_kusd", {}))
        | set(scenario.get("annual_labor_kusd", {}))
        | set(scenario.get("annual_non_labor_kusd", {}))
    )
    return pd.DataFrame(
        [
            {
                "Year": int(year),
                "Labor Cost ($000)": float(scenario.get("annual_labor_kusd", {}).get(year, 0.0)),
                "Non-Labor Cost ($000)": float(scenario.get("annual_non_labor_kusd", {}).get(year, 0.0)),
                "Total Cost ($000)": float(scenario.get("annual_cost_kusd", {}).get(year, 0.0)),
            }
            for year in years
        ]
    )


def annual_staffing_frame(scenario: dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"Year": int(year), "FTE": float(value)}
            for year, value in sorted(scenario.get("annual_fte_years", {}).items())
        ]
    )


def role_summary_frame(assignments: list[dict[str, Any]]) -> pd.DataFrame:
    frame = assignments_frame(assignments)
    if frame.empty:
        return frame
    return (
        frame.groupby(["Role ID", "Role", "Work Type"], dropna=False, as_index=False)
        .agg(
            Assignments=("Assignment ID", "count"),
            **{"FTE-years": ("FTE-years", "sum"), "Labor Cost ($000)": ("Labor Cost ($000)", "sum")},
        )
        .sort_values("FTE-years", ascending=False)
        .reset_index(drop=True)
    )


def work_type_summary_frame(assignments: list[dict[str, Any]]) -> pd.DataFrame:
    frame = assignments_frame(assignments)
    if frame.empty:
        return frame
    out = (
        frame.groupby("Work Type", dropna=False, as_index=False)
        .agg(**{"FTE-years": ("FTE-years", "sum"), "Labor Cost ($000)": ("Labor Cost ($000)", "sum")})
        .sort_values("FTE-years", ascending=False)
    )
    total = out["FTE-years"].sum()
    out["Share"] = out["FTE-years"] / total if total else 0.0
    return out


def stream_summary_frame(tasks: list[dict[str, Any]], assignments: list[dict[str, Any]]) -> pd.DataFrame:
    task_df = tasks_frame(tasks)
    assignment_df = assignments_frame(assignments)
    if task_df.empty:
        return pd.DataFrame()
    task_summary = (
        task_df.groupby(["Stream ID", "Execution Stream"], dropna=False, as_index=False)
        .agg(
            Activities=("WBS ID", "count"),
            Start=("Start", "min"),
            Finish=("Finish", "max"),
            **{
                "Labor Cost ($000)": ("Labor Cost ($000)", "sum"),
                "Non-Labor Cost ($000)": ("Non-Labor Cost ($000)", "sum"),
                "Total Cost ($000)": ("Total Cost ($000)", "sum"),
            },
        )
    )
    if assignment_df.empty:
        task_summary["FTE-years"] = 0.0
        return task_summary
    task_to_stream = task_df.set_index("WBS ID")["Execution Stream"].to_dict()
    assignment_df["Execution Stream"] = assignment_df["WBS ID"].map(task_to_stream)
    fte = assignment_df.groupby("Execution Stream", dropna=False, as_index=False)["FTE-years"].sum()
    return task_summary.merge(fte, on="Execution Stream", how="left").fillna({"FTE-years": 0.0})


def route_cost_frame(tasks: list[dict[str, Any]]) -> pd.DataFrame:
    frame = tasks_frame(tasks)
    if frame.empty:
        return frame
    return (
        frame.groupby(["Scenario Route", "Pathway Specific"], as_index=False)
        .agg(
            Activities=("WBS ID", "count"),
            **{
                "Labor Cost ($000)": ("Labor Cost ($000)", "sum"),
                "Non-Labor Cost ($000)": ("Non-Labor Cost ($000)", "sum"),
                "Total Cost ($000)": ("Total Cost ($000)", "sum"),
                "FTE-years": ("FTE-years", "sum"),
            },
        )
        .sort_values("Total Cost ($000)", ascending=False)
    )


def category_cost_frame(tasks: list[dict[str, Any]], route_only: bool = False) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for task in tasks:
        if route_only and not task.get("pathway_specific"):
            continue
        cost = task.get("cost") or {}
        rows.append(
            {
                "Category": cost.get("category") or cost.get("subcategory") or "Uncategorized",
                "Labor Cost ($000)": float(cost.get("labor_kusd") or 0.0),
                "Non-Labor Cost ($000)": float(cost.get("non_labor_kusd") or 0.0),
                "Total Cost ($000)": float(cost.get("total_kusd") or 0.0),
                "Activities": 1,
            }
        )
    if not rows:
        return pd.DataFrame()
    return (
        pd.DataFrame(rows)
        .groupby("Category", as_index=False)
        .sum(numeric_only=True)
        .sort_values("Total Cost ($000)", ascending=False)
    )


def milestones_frame(milestones: list[dict[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame(milestones)
    if frame.empty:
        return frame
    frame["Baseline Date"] = pd.to_datetime(frame["Baseline Date"], errors="coerce")
    return frame.sort_values(["Baseline Date", "Milestone ID"]).reset_index(drop=True)


def risks_frame(risks: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for risk in risks:
        rows.append(
            {
                "Risk ID": risk.get("Risk ID") or risk.get("risk_id"),
                "Concept": risk.get("Concept") or risk.get("concept"),
                "Category": risk.get("Category") or risk.get("category"),
                "Risk": risk.get("Risk Statement") or risk.get("risk"),
                "Likelihood": risk.get("Likelihood") or risk.get("likelihood"),
                "Impact": risk.get("Impact") or risk.get("consequence"),
                "Score": risk.get("Score") or risk.get("score"),
                "Level": risk.get("Level") or risk.get("level"),
                "Owner": risk.get("Owner") or risk.get("owner"),
                "Mitigation": risk.get("Mitigation / Preventive Action") or risk.get("response"),
                "Trigger": risk.get("Trigger") or risk.get("trigger"),
                "Status": risk.get("Status") or risk.get("status"),
                "Pathway": risk.get("pathway") or "Common",
            }
        )
    return pd.DataFrame(rows)


def quarterly_staffing_frame(assignments: list[dict[str, Any]]) -> pd.DataFrame:
    """Approximate average active FTE by calendar quarter from assignment spans."""
    rows: list[dict[str, Any]] = []
    for assignment in assignments:
        start = pd.to_datetime(assignment.get("start"), errors="coerce")
        finish = pd.to_datetime(assignment.get("finish"), errors="coerce")
        if pd.isna(start) or pd.isna(finish):
            continue
        avg_fte = float(assignment.get("avg_fte") or 0.0)
        periods = pd.period_range(start=start, end=finish, freq="Q")
        for period in periods:
            q_start = period.start_time.normalize()
            q_finish = period.end_time.normalize()
            overlap_start = max(start.normalize(), q_start)
            overlap_finish = min(finish.normalize(), q_finish)
            if overlap_finish < overlap_start:
                continue
            fraction = ((overlap_finish - overlap_start).days + 1) / ((q_finish - q_start).days + 1)
            rows.append(
                {
                    "Quarter": str(period),
                    "Quarter Start": q_start,
                    "Role": assignment.get("role"),
                    "Role ID": assignment.get("role_id"),
                    "Work Type": assignment.get("work_type"),
                    "FTE": avg_fte * fraction,
                }
            )
    if not rows:
        return pd.DataFrame()
    return (
        pd.DataFrame(rows)
        .groupby(["Quarter", "Quarter Start", "Role", "Role ID", "Work Type"], as_index=False)["FTE"]
        .sum()
        .sort_values(["Quarter Start", "Role"])
    )


def dependency_edges_frame(tasks: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for task in tasks:
        for predecessor in task.get("schedule", {}).get("predecessors") or []:
            rows.append({"Predecessor": predecessor, "Successor": task["id"]})
    return pd.DataFrame(rows)


def engineering_work_package_frames(tasks: list[dict[str, Any]]) -> dict[str, pd.DataFrame]:
    summaries: list[dict[str, Any]] = []
    inputs: list[dict[str, Any]] = []
    procedures: list[dict[str, Any]] = []
    requirements: list[dict[str, Any]] = []
    tools: list[dict[str, Any]] = []
    outputs: list[dict[str, Any]] = []
    verification: list[dict[str, Any]] = []
    interfaces: list[dict[str, Any]] = []
    risks: list[dict[str, Any]] = []
    for task in tasks:
        package = task.get("engineering_work_package") or {}
        common = {
            "WBS ID": task.get("id"),
            "Task": task.get("name"),
            "Concept": task.get("concept"),
            "Scenario Route": task.get("scenario_route") or "Shared program baseline",
            "Execution Stream": task.get("execution_stream"),
            "Phase": task.get("phase"),
        }
        summaries.append({
            **common,
            "Engineering Domain": package.get("primary_domain"),
            "Work Pattern": package.get("work_pattern"),
            "Objective": package.get("objective"),
            "Entry Criteria": "\n".join(package.get("entry_criteria") or []),
            "Definition of Done": "\n".join(package.get("definition_of_done") or []),
            "Quality Records": "\n".join(package.get("quality_records") or []),
        })
        for row in package.get("controlled_inputs") or []:
            inputs.append({**common, **row})
        for row in package.get("execution_procedure") or []:
            procedures.append({**common, **row})
        for row in package.get("requirements_and_guidance") or []:
            requirements.append({**common, **row})
        for row in package.get("toolchain") or []:
            tools.append({**common, **row})
        for row in package.get("deliverable_register") or []:
            flat = {**common, **row}
            flat["minimum_contents"] = "\n".join(row.get("minimum_contents") or [])
            outputs.append(flat)
        for row in package.get("verification_and_validation") or []:
            verification.append({**common, **row})
        for row in package.get("interfaces") or []:
            interfaces.append({**common, **row})
        for row in package.get("risks_and_controls") or []:
            risks.append({**common, **row})
    return {
        "Work Package Summary": pd.DataFrame(summaries),
        "Controlled Inputs": pd.DataFrame(inputs),
        "Execution Procedure": pd.DataFrame(procedures),
        "Requirements Guidance": pd.DataFrame(requirements),
        "Toolchain": pd.DataFrame(tools),
        "Deliverable Register": pd.DataFrame(outputs),
        "Verification Plan": pd.DataFrame(verification),
        "Interfaces": pd.DataFrame(interfaces),
        "Task Risk Controls": pd.DataFrame(risks),
    }


def implementation_plan_frames(tasks: list[dict[str, Any]]) -> dict[str, pd.DataFrame]:
    summaries: list[dict[str, Any]] = []
    steps: list[dict[str, Any]] = []
    authorizations: list[dict[str, Any]] = []
    long_leads: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    field_work: list[dict[str, Any]] = []
    contingencies: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    for task in tasks:
        plan = task.get("implementation_plan") or {}
        common = {
            "WBS ID": task.get("id"),
            "Task": task.get("name"),
            "Concept": task.get("concept"),
            "Execution Stream": task.get("execution_stream"),
            "Scenario Route": task.get("scenario_route") or "Shared program baseline",
        }
        summaries.append({
            **common,
            "Implementation Readiness": plan.get("implementation_readiness"),
            "Implementation Summary": plan.get("implementation_summary"),
            "Delivery Strategy": str(plan.get("delivery_strategy") or {}),
            "Make Buy Partner": str(plan.get("make_buy_partner_decision") or {}),
            "Procurement Actions": "\n".join(plan.get("procurement_and_contracting_actions") or []),
            "Implementation Records": "\n".join(plan.get("implementation_records") or []),
            "Open Decisions": "\n".join(str(item) for item in (plan.get("open_decisions") or [])),
            "Linked Playbooks": ", ".join(plan.get("linked_playbooks") or []),
            "Quality Score": plan.get("implementation_quality_score"),
        })
        for row in plan.get("implementation_steps") or []:
            flat = {**common, **row}
            for field in ["supporting_roles", "required_inputs", "tools_equipment", "outputs_and_records"]:
                flat[field] = "\n".join(row.get(field) or [])
            steps.append(flat)
        for row in plan.get("authorizations_and_prerequisites") or []:
            authorizations.append({**common, **row})
        for row in plan.get("long_lead_items") or []:
            long_leads.append({**common, **row})
        for row in plan.get("decision_points") or []:
            decisions.append({**common, **row})
        for row in plan.get("field_lab_or_vendor_activities") or []:
            field_work.append({**common, **row})
        for row in plan.get("fallbacks_and_contingencies") or []:
            contingencies.append({**common, **row})
        for row in plan.get("implementation_source_basis") or []:
            sources.append({**common, **row})
    return {
        "Implementation Summary": pd.DataFrame(summaries),
        "Implementation Steps": pd.DataFrame(steps),
        "Implementation Authorizations": pd.DataFrame(authorizations),
        "Implementation Long Leads": pd.DataFrame(long_leads),
        "Implementation Decisions": pd.DataFrame(decisions),
        "Implementation Field Work": pd.DataFrame(field_work),
        "Implementation Contingencies": pd.DataFrame(contingencies),
        "Implementation Sources": pd.DataFrame(sources),
    }

def scenario_export_tables(scenario: dict[str, Any]) -> dict[str, pd.DataFrame]:
    tables = {
        "Tasks": tasks_frame(scenario["tasks"]),
        "Resource Assignments": assignments_frame(scenario["resource_assignments"]),
        "Annual Financials": annual_financial_frame(scenario),
        "Annual Staffing": annual_staffing_frame(scenario),
        "Role Summary": role_summary_frame(scenario["resource_assignments"]),
        "Milestones": milestones_frame(scenario["milestones"]),
        "Risks": risks_frame(scenario["risks"]),
        "Dependencies": dependency_edges_frame(scenario["tasks"]),
    }
    tables.update(engineering_work_package_frames(scenario["tasks"]))
    tables.update(implementation_plan_frames(scenario["tasks"]))
    return tables
