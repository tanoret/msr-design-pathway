from __future__ import annotations

import importlib.util
import json
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data" / "project_msr_database.schema.json"

# Graph/data tests do not need a running Streamlit server. Make the optional UI
# dependency importable in constrained build environments.
if importlib.util.find_spec("streamlit") is None:
    fake = types.ModuleType("streamlit")
    fake.sidebar = types.SimpleNamespace()

    def _cache_decorator(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

    fake.cache_resource = _cache_decorator
    fake.cache_data = _cache_decorator
    sys.modules["streamlit"] = fake

from src.data_loader import DEFAULT_DATABASE, load_sharded_database


@pytest.fixture(scope="session")
def database() -> dict:
    return load_sharded_database(DEFAULT_DATABASE, verify_semantic_hash=True)


@pytest.fixture(scope="session")
def schema() -> dict:
    with SCHEMA_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)
