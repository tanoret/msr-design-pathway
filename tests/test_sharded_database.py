from __future__ import annotations

import json
from pathlib import Path

from src.data_loader import DEFAULT_DATABASE, load_database
from src.database_sharding import (
    GITHUB_SAFE_FILE_LIMIT_BYTES,
    SHARDED_DATABASE_FORMAT,
    canonical_semantic_sha256,
    file_sha256,
)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def _manifest() -> dict:
    return json.loads(Path(DEFAULT_DATABASE).read_text(encoding="utf-8"))


def test_manifest_uses_plain_uncompressed_json_shards() -> None:
    manifest = _manifest()
    assert manifest["format"] == SHARDED_DATABASE_FORMAT
    assert manifest["storage"].startswith("plain UTF-8 JSON shards")
    assert "no gzip" in manifest["storage"]
    assert all(str(part["path"]).endswith(".json") for part in manifest["parts"])
    assert not any(str(part["path"]).endswith((".gz", ".zip", ".bin")) for part in manifest["parts"])
    assert manifest["record_counts"] == {
        "shared_tasks": 841,
        "route_tasks": 96,
        "resource_roles": 30,
        "resource_assignments": 3138,
    }


def test_every_repository_database_part_is_integral_and_below_github_safe_limit() -> None:
    manifest = _manifest()
    for part in manifest["parts"]:
        path = DATA_DIR / part["path"]
        assert path.exists()
        assert path.suffix == ".json"
        assert path.stat().st_size < GITHUB_SAFE_FILE_LIMIT_BYTES
        assert path.stat().st_size == int(part["size_bytes"])
        assert file_sha256(path) == part["sha256"]


def test_sharded_database_is_complete_and_matches_manifest_digest(database: dict) -> None:
    manifest = _manifest()
    assert len(database["tasks"]) == manifest["record_counts"]["shared_tasks"]
    route_tasks = sum(
        len(stage)
        for module in database["pathway_modules"].values()
        for stage in module.values()
    )
    assert route_tasks == manifest["record_counts"]["route_tasks"]
    assert len(database["resources"]["roles"]) == manifest["record_counts"]["resource_roles"]
    assert len(database["resources"]["assignments"]) == manifest["record_counts"]["resource_assignments"]
    assert canonical_semantic_sha256(database) == manifest["canonical_semantic_sha256"]


def test_default_loader_returns_complete_database_without_monolithic_file(database: dict) -> None:
    assert not (DATA_DIR / "project_msr_database.json").exists()
    loaded = load_database(DEFAULT_DATABASE)
    assert loaded == database
    assert loaded["meta"]["version"] == "4.2.0"
    assert loaded["project"]["name"] == "Project-MSR"
