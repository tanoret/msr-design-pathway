#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import DEFAULT_DATABASE, load_sharded_database
from src.database_sharding import canonical_semantic_sha256


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reconstruct the complete monolithic Project-MSR JSON database from the plain JSON shards."
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "data" / "project_msr_database.full.json",
        help="Output path. The reconstructed file is intentionally ignored by Git because it exceeds 100 MB.",
    )
    args = parser.parse_args()

    database = load_sharded_database(args.manifest, verify_semantic_hash=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(database, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.output} ({args.output.stat().st_size:,} bytes)")
    print(f"Canonical semantic SHA-256: {canonical_semantic_sha256(database)}")
    print(f"Shared tasks: {len(database['tasks']):,}")
    print(f"Route tasks: {sum(len(stage) for module in database['pathway_modules'].values() for stage in module.values()):,}")
    print(f"Resource assignments: {len(database['resources']['assignments']):,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
