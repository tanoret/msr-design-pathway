#!/usr/bin/env python3
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'src'/'components.py'
s=p.read_text(encoding='utf-8')
start=s.index('def render_task_detail(')
end=s.find('\ndef ', start+10)
if end < 0: end=len(s)
block=s[start:end]
block=block.replace('    execution = task.get("execution") or {}\n', '    execution = task.get("execution") or {}\n    implementation = task.get("implementation_plan") or {}\n')
block=block.replace('tabs = st.tabs(["Scope", "Inputs", "Execution", "Outputs", "Requirements & tools", "Interfaces & controls", "Cost basis", "Resources"])', 'tabs = st.tabs(["Scope", "Implementation", "Inputs", "Engineering procedure", "Outputs", "Requirements & tools", "Interfaces & controls", "Cost basis", "Resources"])')
# Shift old tab indexes 1..7 upward. Reverse order prevents collisions.
for old,new in [(7,8),(6,7),(5,6),(4,5),(3,4),(2,3),(1,2)]:
    block=block.replace(f'with tabs[{old}]:', f'with tabs[{new}]:')
needle='    with tabs[2]:\n        frame = _records_frame(ewp.get("controlled_inputs") or [], ["input_id", "input", "source_or_owner", "required_maturity", "verification_before_use", "configuration_control"])'
insert='''    with tabs[1]:
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
            _list_markdown(open_decisions)

    with tabs[2]:
        frame = _records_frame(ewp.get("controlled_inputs") or [], ["input_id", "input", "source_or_owner", "required_maturity", "verification_before_use", "configuration_control"])'''
if needle not in block:
    raise SystemExit('needle not found')
block=block.replace(needle,insert)
s=s[:start]+block+s[end:]
p.write_text(s,encoding='utf-8')
print('patched',p)
