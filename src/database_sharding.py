from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

SHARDED_DATABASE_FORMAT = "project-msr-sharded-json"
SHARDED_DATABASE_FORMAT_VERSION = 1
DEFAULT_BASE_NAME = "project_msr_database"
DEFAULT_MAX_TASK_SHARD_BYTES = 55_000_000
GITHUB_FILE_LIMIT_BYTES = 100_000_000
GITHUB_SAFE_FILE_LIMIT_BYTES = 90_000_000


def canonical_semantic_sha256(database: dict[str, Any]) -> str:
    """Return a stable, formatting-independent hash without building a second giant byte string."""
    digest = hashlib.sha256()
    encoder = json.JSONEncoder(
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    for chunk in encoder.iterencode(database):
        digest.update(chunk.encode("utf-8"))
    return digest.hexdigest()


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _task_chunks(tasks: list[dict[str, Any]], max_bytes: int) -> list[list[dict[str, Any]]]:
    if max_bytes <= 1_000_000:
        raise ValueError("max_bytes must be greater than 1 MB")

    chunks: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    current_estimate = 256

    for task in tasks:
        task_estimate = len(json.dumps(task, indent=2, ensure_ascii=False).encode("utf-8")) + 8
        if current and current_estimate + task_estimate > max_bytes:
            chunks.append(current)
            current = []
            current_estimate = 256
        current.append(task)
        current_estimate += task_estimate

    if current:
        chunks.append(current)
    return chunks


def write_sharded_database(
    database: dict[str, Any],
    output_dir: str | Path,
    *,
    base_name: str = DEFAULT_BASE_NAME,
    application_version: str = "4.3.0",
    max_task_shard_bytes: int = DEFAULT_MAX_TASK_SHARD_BYTES,
) -> Path:
    """Write a complete database as plain JSON shards plus a manifest.

    The logical database is unchanged. Only the storage layout changes so that
    no repository file exceeds GitHub's 100 MB per-file limit.
    """
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    for stale in destination.glob(f"{base_name}.tasks.*.json"):
        stale.unlink()
    for stale_name in [f"{base_name}.core.json", f"{base_name}.manifest.json"]:
        stale = destination / stale_name
        if stale.exists():
            stale.unlink()

    tasks = list(database.get("tasks") or [])
    top_level_order = list(database.keys())
    core = {key: value for key, value in database.items() if key != "tasks"}

    core_path = destination / f"{base_name}.core.json"
    write_json(core_path, core)

    parts: list[dict[str, Any]] = [
        {
            "path": core_path.name,
            "kind": "core",
            "size_bytes": core_path.stat().st_size,
            "sha256": file_sha256(core_path),
        }
    ]

    chunks = _task_chunks(tasks, max_task_shard_bytes)
    task_offset = 0
    for shard_index, chunk in enumerate(chunks, start=1):
        shard_path = destination / f"{base_name}.tasks.{shard_index:03d}.json"
        shard_payload = {
            "format": "project-msr-task-shard",
            "format_version": 1,
            "database_version": str(database.get("meta", {}).get("version") or ""),
            "shard_index": shard_index,
            "task_start_index": task_offset,
            "task_end_index": task_offset + len(chunk) - 1,
            "task_count": len(chunk),
            "tasks": chunk,
        }
        write_json(shard_path, shard_payload)
        size = shard_path.stat().st_size
        if size >= GITHUB_SAFE_FILE_LIMIT_BYTES:
            raise ValueError(
                f"Generated shard {shard_path.name} is {size:,} bytes; "
                f"reduce max_task_shard_bytes below {max_task_shard_bytes:,}."
            )
        parts.append(
            {
                "path": shard_path.name,
                "kind": "task_shard",
                "shard_index": shard_index,
                "task_start_index": task_offset,
                "task_end_index": task_offset + len(chunk) - 1,
                "task_count": len(chunk),
                "size_bytes": size,
                "sha256": file_sha256(shard_path),
            }
        )
        task_offset += len(chunk)

    route_task_count = sum(
        len(stage)
        for module in (database.get("pathway_modules") or {}).values()
        for stage in module.values()
        if isinstance(stage, list)
    )
    resources = database.get("resources") or {}
    manifest = {
        "format": SHARDED_DATABASE_FORMAT,
        "format_version": SHARDED_DATABASE_FORMAT_VERSION,
        "application_version": application_version,
        "database_version": str(database.get("meta", {}).get("version") or ""),
        "database_name": str(database.get("meta", {}).get("name") or "Project-MSR"),
        "storage": "plain UTF-8 JSON shards; no gzip, binary encoding, or data reduction",
        "top_level_order": top_level_order,
        "canonical_semantic_sha256": canonical_semantic_sha256(database),
        "record_counts": {
            "shared_tasks": len(tasks),
            "route_tasks": route_task_count,
            "resource_roles": len(resources.get("roles") or []),
            "resource_assignments": len(resources.get("assignments") or []),
        },
        "parts": parts,
    }
    manifest_path = destination / f"{base_name}.manifest.json"
    write_json(manifest_path, manifest)
    return manifest_path
