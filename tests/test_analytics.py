from __future__ import annotations

import pytest

from src.analytics import (
    annual_financial_frame,
    role_summary_frame,
    stream_summary_frame,
    work_type_summary_frame,
)
from src.pathway_engine import ScenarioOptions, build_scenario


def test_analytics_reconcile_to_scenario_summary(database: dict) -> None:
    scenario = build_scenario(database, ScenarioOptions())
    annual = annual_financial_frame(scenario)
    role = role_summary_frame(scenario["resource_assignments"])
    work = work_type_summary_frame(scenario["resource_assignments"])
    stream = stream_summary_frame(scenario["tasks"], scenario["resource_assignments"])

    assert annual["Total Cost ($000)"].sum() == pytest.approx(scenario["summary"]["total_cost_kusd"], abs=0.1)
    assert role["FTE-years"].sum() == pytest.approx(scenario["summary"]["fte_years"], abs=0.1)
    assert work["FTE-years"].sum() == pytest.approx(scenario["summary"]["fte_years"], abs=0.1)
    assert stream["Total Cost ($000)"].sum() == pytest.approx(scenario["summary"]["total_cost_kusd"], abs=0.1)
    assert work["Share"].sum() == pytest.approx(1.0, abs=1e-6)
