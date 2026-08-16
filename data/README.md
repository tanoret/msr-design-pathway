# Project-MSR data

The complete Project-MSR planning database is stored as **plain, uncompressed UTF-8 JSON shards** so every repository file remains below GitHub's 100 MB per-file limit.

## Database files

- `project_msr_database.manifest.json` - ordered manifest, record counts, file sizes, SHA-256 checksums, and the canonical semantic checksum for the complete logical database.
- `project_msr_database.core.json` - every top-level database collection except the shared `tasks` array.
- `project_msr_database.tasks.001.json` through `project_msr_database.tasks.004.json` - the complete shared task array in original order.
- `project_msr_database.schema.json` - JSON Schema for the reconstructed database.
- `task_cost_audit_v4_2.csv` - flat task-by-task cost register.

No field, task, resource assignment, cost record, engineering work package, licensing module, milestone, risk, test matrix, source, or supporting collection has been removed or summarized. The Streamlit loader reconstructs the same in-memory object that was previously held in the 184 MB monolithic JSON file.

The manifest's canonical semantic SHA-256 is checked by the reconstruction utility and by automated tests. Each shard is also protected by an individual SHA-256 checksum and declared file size.

## Reconstruct one monolithic JSON file

A single large file can be recreated locally when needed:

```bash
python scripts/reconstruct_database.py
```

This writes `data/project_msr_database.full.json`. The reconstructed file is intentionally excluded from Git because it exceeds GitHub's per-file limit.

## Rebuild the shards from a monolithic source

```bash
python scripts/shard_database.py /path/to/project_msr_database.json
```

The sharding process changes only the storage layout. It does not gzip, minify, encode, or reduce the planning content.

The bundled database is version **4.2.0**. It contains **841** shared activities, **96** route activities, **3,138** shared assignments, and **30** resource roles. Every one of the **937** activities carries its complete Engineering Work Package and bottom-up cost basis.
