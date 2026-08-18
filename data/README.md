# Project-MSR data

The complete Project-MSR v4.3.0 database is stored as **plain, uncompressed UTF-8 JSON shards** so every repository file remains below GitHub's per-file limit.

## Contents

- `project_msr_database.manifest.json` - ordered manifest, counts, sizes, per-file hashes, and semantic checksum.
- `project_msr_database.core.json` - all top-level collections except the shared task array.
- `project_msr_database.tasks.001.json` onward - all shared tasks in original order.
- `project_msr_database.schema.json` - Draft 2020-12 JSON Schema.
- `task_cost_audit_v4_2.csv` - v4.2 bottom-up cost audit retained because v4.3 does not change the accounting estimate.
- `implementation_task_audit_v4_3.csv` - 937-row implementation-readiness, step, decision, long-lead, playbook, and hold-point register.

Nothing has been removed or reduced. The database includes **841** shared activities, **96** route activities, **3138** shared assignments, **30** roles, **11** implementation playbooks, and **25** chemistry/processing experiments, **8** program-level closure items, and **21** bespoke high-consequence execution packages. All **937** activities include an Engineering Work Package, bottom-up task-cost basis, and implementation plan.

## Reconstruct one monolithic file

```bash
python scripts/reconstruct_database.py
```

The generated `data/project_msr_database.full.json` is intentionally ignored by Git because it exceeds GitHub's per-file limit.

## Rebuild shards

```bash
python scripts/shard_database.py data/project_msr_database.full.json --application-version 4.3.0
```

Sharding changes only storage layout; it does not gzip, encode, minify, summarize, or remove data.
