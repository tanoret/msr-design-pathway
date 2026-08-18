#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database_sharding import write_sharded_database


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Split the complete Project-MSR database into plain, uncompressed JSON files below GitHub's per-file limit."
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "data")
    parser.add_argument("--application-version", default="4.3.0")
    parser.add_argument("--max-task-shard-bytes", type=int, default=45_000_000)
    args = parser.parse_args()

    database = json.loads(args.input.read_text(encoding="utf-8"))
    manifest = write_sharded_database(
        database,
        args.output_dir,
        application_version=args.application_version,
        max_task_shard_bytes=args.max_task_shard_bytes,
    )
    print(f"Wrote {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
