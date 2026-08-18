#!/usr/bin/env python3
"""Exercise app control flow in build environments where Streamlit is unavailable.

This is not a renderer. It supplies deterministic widget values and verifies that all
application tabs can execute without Python exceptions against the bundled database.
"""
from __future__ import annotations

import functools
import os
import sys
import types
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("PROJECT_MSR_PASSWORD", "smoke-test-password-4-2-1")


class _RerunRequested(RuntimeError):
    pass


class _Context:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def __getattr__(self, name: str):
        if name == "column_config":
            return _ColumnConfig()
        return _Widget(name)


class _ColumnConfig:
    def __getattr__(self, name: str):
        return lambda *args, **kwargs: {"type": name, "args": args, "kwargs": kwargs}


class _Widget:
    def __init__(self, name: str):
        self.name = name

    def __call__(self, *args: Any, **kwargs: Any):
        if self.name in {"cache_data", "cache_resource"}:
            def decorator(func):
                return functools.lru_cache(maxsize=None)(func)
            return decorator
        if self.name in {"columns", "tabs"}:
            spec = args[0] if args else kwargs.get("spec", 1)
            length = len(spec) if isinstance(spec, (list, tuple)) else int(spec)
            return [_Context() for _ in range(length)]
        if self.name in {"expander", "form", "container", "empty"}:
            return _Context()
        if self.name in {"selectbox", "radio", "segmented_control"}:
            options = args[1] if len(args) > 1 else kwargs.get("options", [])
            if self.name == "segmented_control":
                requested = os.environ.get("PROJECT_MSR_SMOKE_PAGE")
                if requested and requested in list(options):
                    return requested
                default = kwargs.get("default")
                return default if default is not None else (list(options)[0] if options else None)
            index = kwargs.get("index", 0)
            return list(options)[index] if options else None
        if self.name == "multiselect":
            return kwargs.get("default", []) or []
        if self.name == "slider":
            if "value" in kwargs:
                return kwargs["value"]
            return args[3] if len(args) > 3 else args[2] if len(args) > 2 else None
        if self.name == "checkbox":
            return kwargs.get("value", False)
        if self.name == "text_input":
            if kwargs.get("key") == "_project_msr_password":
                return os.environ.get("PROJECT_MSR_PASSWORD", "smoke-test-password-4-2-1")
            return kwargs.get("value", "")
        if self.name == "form_submit_button":
            return True
        if self.name == "button":
            return False
        if self.name == "rerun":
            raise _RerunRequested("Streamlit rerun requested")
        if self.name == "file_uploader":
            return None
        if self.name == "stop":
            raise RuntimeError("st.stop called during smoke test")
        return None


class _FakeStreamlit(types.ModuleType):
    def __init__(self):
        super().__init__("streamlit")
        self.sidebar = _Context()
        self.column_config = _ColumnConfig()
        self.session_state: dict[str, Any] = {}
        self.secrets: dict[str, Any] = {}
        self.cache_data = _Widget("cache_data")
        self.cache_resource = _Widget("cache_resource")

    def __getattr__(self, name: str):
        if name == "column_config":
            return self.column_config
        return _Widget(name)


sys.modules["streamlit"] = _FakeStreamlit()

import app  # noqa: E402

if os.environ.get("PROJECT_MSR_SMOKE_EMPTY_IMPLEMENTATION") == "1":
    _original_load_database = app.load_database

    def _load_database_without_implementation(*args: Any, **kwargs: Any):
        import copy

        database = copy.deepcopy(_original_load_database(*args, **kwargs))
        for key in [
            "implementation_playbooks",
            "fuel_supply_plan",
            "chemistry_processing_plan",
            "implementation_closure_register",
        ]:
            database.pop(key, None)
        for task in database.get("tasks") or []:
            task.pop("implementation_plan", None)
        for module in (database.get("pathway_modules") or {}).values():
            for stage_tasks in module.values():
                for task in stage_tasks or []:
                    task.pop("implementation_plan", None)
        return database

    app.load_database = _load_database_without_implementation

def run_page(page: str) -> None:
    os.environ["PROJECT_MSR_SMOKE_PAGE"] = page
    for _ in range(3):
        try:
            app.main()
            print(f"Application control-flow smoke test passed: {page}")
            return
        except _RerunRequested:
            continue
    raise RuntimeError(f"Application did not settle after authentication reruns: {page}")


if os.environ.get("PROJECT_MSR_SMOKE_ALL") == "1":
    for page_name in app.NAV_ITEMS:
        run_page(page_name)
else:
    run_page(os.environ.get("PROJECT_MSR_SMOKE_PAGE", "Overview"))
