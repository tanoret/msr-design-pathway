#!/usr/bin/env python3
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'app.py'
s=p.read_text(encoding='utf-8')
s=s.replace('    "Experiments",\n    "Risks & gates",', '    "Experiments",\n    "Implementation",\n    "Risks & gates",',1)
insert_point='\ndef risks_gates_tab(scenario: dict[str, Any]) -> None:\n'
func='''
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

    fuel_tab, chemistry_tab, playbook_tab, register_tab = st.tabs([
        "Fuel supply and procurement", "Chemistry and salt processing", "Other implementation playbooks", "Task execution register"
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
                    render_note(str(value), title=f"Branch {idx+1}")
        phase_rows = []
        for phase in fuel.get("execution_phases") or []:
            phase_rows.append({
                "Phase ID": phase.get("phase_id"),
                "Phase": phase.get("phase"),
                "Window": phase.get("window"),
                "Actions": "\n".join(phase.get("actions") or []),
                "Deliverables": "\n".join(phase.get("deliverables") or []),
                "Release gate": phase.get("gate"),
            })
        if phase_rows:
            st.markdown("#### End-to-end execution sequence")
            st.dataframe(pd.DataFrame(phase_rows), use_container_width=True, hide_index=True, height=620)
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
            render_note(str(decision.get("rule") or ""), title=str(decision.get("question") or "Architecture decision"))
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
        if not view.empty:
            ids = view["WBS ID"].astype(str).tolist()
            selected = st.selectbox("Open implementation-ready task", ids, format_func=lambda tid: f"{tid} · {next(t['name'] for t in implementation_tasks if str(t['id'])==tid)}", key="impl_register_task")
            render_task_detail(next(task for task in implementation_tasks if str(task["id"]) == selected))
'''
if insert_point not in s: raise SystemExit('insert point missing')
s=s.replace(insert_point,func+insert_point,1)
s=s.replace('    elif page == "Experiments":\n        experiments_tab(scenario)\n    elif page == "Risks & gates":', '    elif page == "Experiments":\n        experiments_tab(scenario)\n    elif page == "Implementation":\n        implementation_tab(database, scenario)\n    elif page == "Risks & gates":',1)
p.write_text(s,encoding='utf-8')
print('patched',p)
