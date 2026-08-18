from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import streamlit as st
except ModuleNotFoundError:  # test/build environments without the UI runtime
    class _StreamlitFallback:
        @staticmethod
        def cache_resource(*args, **kwargs):
            def decorator(func):
                return func
            return decorator

        @staticmethod
        def cache_data(*args, **kwargs):
            def decorator(func):
                return func
            return decorator

    st = _StreamlitFallback()

from .database_sharding import SHARDED_DATABASE_FORMAT, canonical_semantic_sha256, file_sha256

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DEFAULT_DATABASE = DATA_DIR / "project_msr_database.manifest.json"
LEGACY_MONOLITHIC_DATABASE = DATA_DIR / "project_msr_database.json"
REQUIRED_TOP_LEVEL_KEYS = {
    "meta",
    "project",
    "pathways",
    "pathway_modules",
    "tasks",
    "resources",
    "financials",
    "milestones",
    "risks",
    "design_review_gates",
    "test_matrices",
    "sources",
    "data_quality",
}
REQUIRED_PATHWAYS = {"doe_launchpad", "part50", "part52", "part53", "part57"}


class DatabaseValidationError(ValueError):
    """Raised when a database is not compatible with the Project-MSR app."""


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _resolve_part(base_dir: Path, relative_path: str) -> Path:
    candidate = (base_dir / relative_path).resolve()
    base = base_dir.resolve()
    if candidate != base and base not in candidate.parents:
        raise DatabaseValidationError(f"Database part escapes its data directory: {relative_path}")
    return candidate


def _verify_part(path: Path, descriptor: dict[str, Any]) -> None:
    if not path.exists():
        raise DatabaseValidationError(f"Database part is missing: {path.name}")
    expected_size = int(descriptor.get("size_bytes") or 0)
    if expected_size and path.stat().st_size != expected_size:
        raise DatabaseValidationError(
            f"Database part size mismatch for {path.name}: expected {expected_size:,}, found {path.stat().st_size:,}."
        )
    expected_hash = str(descriptor.get("sha256") or "")
    if expected_hash and file_sha256(path) != expected_hash:
        raise DatabaseValidationError(f"Database part checksum mismatch: {path.name}")


def load_sharded_database(manifest_path: str | Path, *, verify_semantic_hash: bool = False) -> dict[str, Any]:
    path = Path(manifest_path)
    manifest = _read_json(path)
    if manifest.get("format") != SHARDED_DATABASE_FORMAT:
        raise DatabaseValidationError(f"Unsupported database manifest format in {path.name}.")
    if int(manifest.get("format_version") or 0) != 1:
        raise DatabaseValidationError(f"Unsupported database manifest version in {path.name}.")

    parts = manifest.get("parts") or []
    core_parts = [part for part in parts if part.get("kind") == "core"]
    task_parts = sorted(
        (part for part in parts if part.get("kind") == "task_shard"),
        key=lambda item: int(item.get("shard_index") or 0),
    )
    if len(core_parts) != 1 or not task_parts:
        raise DatabaseValidationError("The manifest must identify one core part and at least one task shard.")

    base_dir = path.parent
    core_path = _resolve_part(base_dir, str(core_parts[0].get("path") or ""))
    _verify_part(core_path, core_parts[0])
    core = _read_json(core_path)
    if not isinstance(core, dict):
        raise DatabaseValidationError("The database core part must contain a JSON object.")

    tasks: list[dict[str, Any]] = []
    expected_start = 0
    for descriptor in task_parts:
        shard_path = _resolve_part(base_dir, str(descriptor.get("path") or ""))
        _verify_part(shard_path, descriptor)
        shard = _read_json(shard_path)
        shard_tasks = shard.get("tasks") if isinstance(shard, dict) else None
        if not isinstance(shard_tasks, list):
            raise DatabaseValidationError(f"Task shard {shard_path.name} does not contain a tasks array.")
        start_index = int(shard.get("task_start_index") or 0)
        if start_index != expected_start:
            raise DatabaseValidationError(
                f"Task shard sequence error in {shard_path.name}: expected start index {expected_start}, found {start_index}."
            )
        declared_count = int(shard.get("task_count") or 0)
        if declared_count != len(shard_tasks):
            raise DatabaseValidationError(f"Task count mismatch in {shard_path.name}.")
        tasks.extend(shard_tasks)
        expected_start += len(shard_tasks)

    expected_tasks = int((manifest.get("record_counts") or {}).get("shared_tasks") or 0)
    if expected_tasks and len(tasks) != expected_tasks:
        raise DatabaseValidationError(f"Sharded task total mismatch: expected {expected_tasks}, found {len(tasks)}.")

    order = manifest.get("top_level_order") or list(core.keys()) + ["tasks"]
    database: dict[str, Any] = {}
    for key in order:
        if key == "tasks":
            database[key] = tasks
        elif key in core:
            database[key] = core[key]
    for key, value in core.items():
        if key not in database:
            database[key] = value
    if "tasks" not in database:
        database["tasks"] = tasks

    expected_semantic_hash = str(manifest.get("canonical_semantic_sha256") or "")
    if verify_semantic_hash and expected_semantic_hash:
        actual_semantic_hash = canonical_semantic_sha256(database)
        if actual_semantic_hash != expected_semantic_hash:
            raise DatabaseValidationError(
                "The reconstructed database content does not match the manifest semantic checksum."
            )
    return validate_database(database)


def _version_tuple(value: Any) -> tuple[int, int, int]:
    parts: list[int] = []
    for token in str(value or "").split(".")[:3]:
        digits = "".join(char for char in token if char.isdigit())
        parts.append(int(digits or 0))
    return tuple((parts + [0, 0, 0])[:3])


def validate_database(database: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(REQUIRED_TOP_LEVEL_KEYS.difference(database))
    if missing:
        errors.append(f"Missing top-level keys: {', '.join(missing)}")

    pathways = database.get("pathways")
    if not isinstance(pathways, dict):
        errors.append("'pathways' must be an object.")
    else:
        missing_paths = sorted(REQUIRED_PATHWAYS.difference(pathways))
        if missing_paths:
            errors.append(f"Missing pathway definitions: {', '.join(missing_paths)}")

    tasks = database.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        errors.append("'tasks' must be a non-empty array.")
        task_ids: set[str] = set()
    else:
        task_ids = {str(task.get("id")) for task in tasks if isinstance(task, dict) and task.get("id")}
        if len(task_ids) != len(tasks):
            errors.append("Every task must have a unique, non-empty id.")
        for index, task in enumerate(tasks[:50]):
            if not isinstance(task, dict):
                errors.append(f"Task {index} is not an object.")
                continue
            for field in ["name", "concept", "execution_stream", "schedule", "cost", "resources", "execution"]:
                if field not in task:
                    errors.append(f"Task {task.get('id', index)} is missing '{field}'.")

    resources = database.get("resources")
    if not isinstance(resources, dict):
        errors.append("'resources' must be an object.")
    else:
        roles = resources.get("roles") or []
        assignments = resources.get("assignments") or []
        role_ids = {str(role.get("role_id")) for role in roles if isinstance(role, dict) and role.get("role_id")}
        if not {"CNO", "CTO"}.issubset(role_ids):
            errors.append("Resource roles must include CNO and CTO.")
        invalid_assignment_tasks = sorted(
            {
                str(assignment.get("task_id"))
                for assignment in assignments
                if isinstance(assignment, dict) and assignment.get("task_id") not in task_ids
            }
        )
        if invalid_assignment_tasks:
            errors.append(f"Resource assignments reference unknown tasks: {', '.join(invalid_assignment_tasks[:8])}")

    project = database.get("project") or {}
    if project.get("name") != "Project-MSR":
        errors.append("The project name must be 'Project-MSR'.")

    # Version 4.3 introduced execution playbooks and task-level implementation
    # plans. Validate these collections when a 4.3+ database declares them so a
    # mixed application/database deployment fails clearly during loading rather
    # than later inside an interactive tab. Older uploaded databases remain
    # readable and are handled by the UI's compatibility empty state.
    if _version_tuple((database.get("meta") or {}).get("version")) >= (4, 3, 0):
        playbooks = database.get("implementation_playbooks")
        fuel_plan = database.get("fuel_supply_plan")
        chemistry_plan = database.get("chemistry_processing_plan")
        closure_register = database.get("implementation_closure_register")
        if not isinstance(playbooks, dict) or not playbooks:
            errors.append("A v4.3+ database must include non-empty implementation_playbooks.")
        if not isinstance(fuel_plan, dict) or not (fuel_plan.get("execution_phases") or []):
            errors.append("A v4.3+ database must include fuel_supply_plan execution phases.")
        if not isinstance(chemistry_plan, dict) or not (chemistry_plan.get("experiment_matrix") or []):
            errors.append("A v4.3+ database must include the chemistry_processing_plan experiment matrix.")
        if not isinstance(closure_register, list) or not closure_register:
            errors.append("A v4.3+ database must include the implementation_closure_register.")

        route_tasks = [
            task
            for module in (database.get("pathway_modules") or {}).values()
            if isinstance(module, dict)
            for stage in module.values()
            if isinstance(stage, list)
            for task in stage
            if isinstance(task, dict)
        ]
        all_tasks = [task for task in (tasks or []) if isinstance(task, dict)] + route_tasks
        implementation_count = sum(bool(task.get("implementation_plan")) for task in all_tasks)
        expected_count = int((database.get("data_quality") or {}).get("implementation_ready_task_count") or 0)
        if expected_count and implementation_count != expected_count:
            errors.append(
                f"Implementation-plan count mismatch: expected {expected_count}, found {implementation_count}."
            )

    if errors:
        raise DatabaseValidationError(" ".join(errors))
    return database


def _load_database_uncached(path: str | Path = DEFAULT_DATABASE) -> dict[str, Any]:
    database_path = Path(path)
    if database_path.is_dir():
        database_path = database_path / "project_msr_database.manifest.json"
    if database_path.name.endswith(".manifest.json"):
        return load_sharded_database(database_path)
    payload = _read_json(database_path)
    if isinstance(payload, dict) and payload.get("format") == SHARDED_DATABASE_FORMAT:
        return load_sharded_database(database_path)
    if not isinstance(payload, dict):
        raise DatabaseValidationError("The Project-MSR database root must be a JSON object.")
    return validate_database(payload)


def _normalized_database_path(path: str | Path = DEFAULT_DATABASE) -> Path:
    database_path = Path(path)
    if database_path.is_dir():
        database_path = database_path / "project_msr_database.manifest.json"
    return database_path.resolve()


def database_cache_token(path: str | Path = DEFAULT_DATABASE) -> str:
    """Return a content-sensitive token for Streamlit's database cache.

    Streamlit hashes function arguments, not the files a path points to.  The
    manifest checksum is therefore passed into the cached loader so a deployed
    data revision cannot reuse an older in-process database object merely
    because the repository path stayed the same.
    """
    database_path = _normalized_database_path(path)
    if not database_path.exists():
        return f"missing:{database_path}"
    if database_path.name.endswith(".manifest.json"):
        manifest = _read_json(database_path)
        if not isinstance(manifest, dict):
            raise DatabaseValidationError("The Project-MSR manifest root must be a JSON object.")
        return ":".join(
            [
                str(manifest.get("application_version") or ""),
                str(manifest.get("database_version") or ""),
                str(manifest.get("canonical_semantic_sha256") or ""),
                file_sha256(database_path),
            ]
        )
    stat = database_path.stat()
    return f"{stat.st_size}:{stat.st_mtime_ns}:{file_sha256(database_path)}"


# This read-only database is large. cache_resource keeps one shared in-process
# object instead of serializing and copying it for every Streamlit session. The
# cache token ensures repository data revisions invalidate the cached object.
@st.cache_resource(show_spinner=False)
def _load_database_cached(path_string: str, cache_token: str) -> dict[str, Any]:
    del cache_token  # used only as a content-sensitive cache key
    return _load_database_uncached(path_string)


def load_database(path: str | Path = DEFAULT_DATABASE) -> dict[str, Any]:
    database_path = _normalized_database_path(path)
    return _load_database_cached(str(database_path), database_cache_token(database_path))


def clear_database_cache() -> None:
    """Clear the bundled-database cache when supported by the Streamlit runtime."""
    clear = getattr(_load_database_cached, "clear", None)
    if callable(clear):
        clear()


def load_database_bytes(payload: bytes) -> dict[str, Any]:
    database = json.loads(payload.decode("utf-8"))
    if not isinstance(database, dict):
        raise DatabaseValidationError("Uploaded database root must be a JSON object.")
    return validate_database(database)
