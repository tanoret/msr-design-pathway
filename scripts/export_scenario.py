#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import DEFAULT_DATABASE, _load_database_uncached
from src.pathway_engine import EXECUTABLE_POWER_PATHS, POWER_PATHS, ScenarioOptions, build_scenario


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(
        description="Build and export a Project-MSR scenario without launching Streamlit."
    )
    command.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    command.add_argument("--output", type=Path, default=Path("project_msr_active_scenario.json"))
    command.add_argument("--demonstrator", choices=["launchpad_usa", "launchpad_inl"], default="launchpad_usa")
    command.add_argument("--power-path", choices=POWER_PATHS, default="part53")
    command.add_argument("--power-variant", default="col", help="Path-specific variant key, such as cp_ol, straight_col, col, or foak_standardized.")
    command.add_argument("--part57-mode", choices=["current_with_fallback", "hypothetical_final_rule"], default="current_with_fallback")
    command.add_argument("--fallback-path", choices=EXECUTABLE_POWER_PATHS, default="part53")
    command.add_argument("--fallback-variant", default="col")
    command.add_argument("--labor-factor", type=float, default=1.0)
    command.add_argument("--non-labor-factor", type=float, default=1.0)
    command.add_argument("--power-shift-months", type=int, default=0)
    return command


def main() -> int:
    args = parser().parse_args()
    database = _load_database_uncached(args.database)
    options = ScenarioOptions(
        demonstrator_variant=args.demonstrator,
        power_reactor_path=args.power_path,
        power_reactor_variant=args.power_variant,
        part57_mode=args.part57_mode,
        part57_fallback_path=args.fallback_path,
        part57_fallback_variant=args.fallback_variant,
        labor_factor=args.labor_factor,
        non_labor_factor=args.non_labor_factor,
        power_schedule_shift_months=args.power_shift_months,
    )
    scenario = build_scenario(database, options)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(scenario, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    summary = scenario["summary"]
    print(f"Wrote {args.output}")
    print(f"Demonstrator: DOE Launch Pad / {summary['demonstrator_variant']}")
    print(f"Commercial route: {summary['power_reactor_path']} / {summary['power_reactor_variant']}")
    if summary.get("part57_fallback_path"):
        print(f"Executable fallback: {summary['part57_fallback_path']} / {summary['part57_fallback_variant']}")
    print(f"Tasks: {summary['active_task_count']:,}")
    print(f"Assignments: {summary['assignment_count']:,}")
    print(f"FTE-years: {summary['fte_years']:,.1f}")
    print(f"Route-specific cost ($000): {summary['route_specific_cost_kusd']:,.1f}")
    print(f"Total program cost ($000): {summary['total_cost_kusd']:,.1f}")
    print(f"Demonstrator mechanical completion: {summary['demonstrator_mechanical_completion_target']}")
    print(f"Commercial operation: {summary['power_commercial_operation_date']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
