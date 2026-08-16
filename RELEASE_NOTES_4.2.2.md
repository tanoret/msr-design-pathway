# Project-MSR Planner 4.2.2 release notes

Release date: 2026-08-16

## Purpose

Version 4.2.2 resolves GitHub's rejection of the former 184 MB monolithic planning database while preserving the complete Project-MSR dataset and application behavior.

## Complete uncompressed database

The repository now stores the database as plain UTF-8 JSON:

- `data/project_msr_database.manifest.json`
- `data/project_msr_database.core.json`
- `data/project_msr_database.tasks.001.json`
- `data/project_msr_database.tasks.002.json`
- `data/project_msr_database.tasks.003.json`
- `data/project_msr_database.tasks.004.json`

The largest file is approximately 44 MB. No field or record has been removed, summarized, gzipped, minified, binary-encoded, or fetched from an external service.

The reconstructed database is semantically identical to the v4.2.0 monolithic database. Both produce the canonical semantic SHA-256:

```text
554ff077c2b6bb7ad3948a1ab0f65fca018190e9ea6b5f0d95379170e0bf4f51
```

## Loader and deployment changes

- The application loads the manifest and reconstructs all database collections in their original order.
- Every JSON part is checked against its declared file size and SHA-256 checksum.
- The read-only database uses Streamlit's resource cache so one in-process copy is shared across sessions.
- The monolithic database path is ignored by Git.
- `scripts/reconstruct_database.py` recreates the complete large JSON file locally.
- `scripts/shard_database.py` regenerates the GitHub-safe files from a monolithic source.
- `docs/GITHUB_STREAMLIT_DEPLOYMENT.md` provides clean-history commands for a repository whose first push was rejected.

## Planning content retained

- 841 shared engineering and program activities
- 96 route-specific licensing and authorization activities
- 937 complete Engineering Work Packages
- 3,138 shared resource assignments
- 30 resource roles
- all costs, schedules, annual profiles, milestones, risks, test matrices, licensing pathways, sources, and exports

## Validation

The release passes schema validation, database-integrity validation, semantic-equivalence verification, per-shard checksum checks, all supported scenario builds, Python compilation, application smoke flows, and 48 automated tests.
