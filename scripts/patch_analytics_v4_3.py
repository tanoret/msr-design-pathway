#!/usr/bin/env python3
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'src'/'analytics.py'
s=p.read_text(encoding='utf-8')
# Add plan local
s=s.replace('        package = task.get("engineering_work_package") or {}\n', '        package = task.get("engineering_work_package") or {}\n        implementation = task.get("implementation_plan") or {}\n',1)
needle='                "Regulatory Basis": task.get("regulatory_basis"),\n'
replacement='''                "Regulatory Basis": task.get("regulatory_basis"),
                "Implementation Ready": bool(implementation),
                "Implementation Readiness": implementation.get("implementation_readiness"),
                "Implementation Summary": implementation.get("implementation_summary"),
                "Implementation Steps Count": len(implementation.get("implementation_steps") or []),
                "Procurement Actions Count": len(implementation.get("procurement_and_contracting_actions") or []),
                "Long-Lead Items Count": len(implementation.get("long_lead_items") or []),
                "Decision Points Count": len(implementation.get("decision_points") or []),
                "Linked Playbooks": ", ".join(implementation.get("linked_playbooks") or []),
'''
if needle not in s: raise SystemExit('tasks_frame needle missing')
s=s.replace(needle,replacement,1)
insert_before='\ndef scenario_export_tables(scenario: dict[str, Any]) -> dict[str, pd.DataFrame]:\n'
newfunc='''
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
            "Open Decisions": "\n".join(plan.get("open_decisions") or []),
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
'''
if insert_before not in s: raise SystemExit('insert point missing')
s=s.replace(insert_before,newfunc+insert_before,1)
needle2='    tables.update(engineering_work_package_frames(scenario["tasks"]))\n'
s=s.replace(needle2,needle2+'    tables.update(implementation_plan_frames(scenario["tasks"]))\n',1)
p.write_text(s,encoding='utf-8')
print('patched',p)
