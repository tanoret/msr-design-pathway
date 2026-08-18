# Project-MSR Planner 4.3.1 release notes

Release date: 2026-08-18

Version 4.3.1 is a deployment reliability hotfix for the v4.3 implementation-planning release. The engineering database and execution content are unchanged.

## Corrections

- Database caching now includes the manifest application version, database version, semantic checksum, and manifest file checksum. A new deployment cannot reuse an older cached database object simply because the path is unchanged.
- The Database sidebar includes a **Reload bundled database** control.
- The Implementation section resolves content from both the loaded database and active scenario.
- Empty or older uploaded databases display an explanatory empty state rather than raising a `KeyError`.
- The task execution register also handles databases without v4.3 task-level implementation plans.

## Root cause

The v4.3 application code was deployed with valid v4.3 database shards, but Streamlit's resource cache was keyed only by the unchanged manifest path. A previously cached v4.2 database object could therefore be returned to the v4.3 UI. The UI then attempted to index an empty playbook collection.

## Database

- Database version: 4.3.0
- Shared tasks: 841
- Route tasks: 96
- Implementation playbooks: 11
- Chemistry validation experiments: 25
- Fuel-supply phases: 6
- Implementation closure items: 8

All database content is preserved in plain UTF-8 JSON shards.

## Verification

- JSON Schema and database-integrity checks passed.
- All 54 automated tests passed in split test runs.
- All 13 authenticated application sections passed the control-flow smoke test.
- The Implementation section passed a regression smoke test with all optional v4.3 collections removed.
- The complete database remains unchanged and reconstructs to the v4.3.0 semantic checksum.
