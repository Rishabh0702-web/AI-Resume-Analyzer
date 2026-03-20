"""MongoDB persistence utilities for backend services.

Configuration:
  - `MONGODB_URI` (preferred) or `MONGO_URI`
  - optional `MONGO_DB_NAME` (default: resume_analyzer)
  - optional `MONGO_COLLECTION_NAME` (default: analysis_results)

If configuration/connection fails, saves are skipped and diagnostics are exposed
via `get_database_status()`.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

try:
    from pymongo import MongoClient
    import certifi
except Exception:
    MongoClient = None
    certifi = None


def _read_dotenv_file() -> dict[str, str]:
    """Read simple KEY=VALUE pairs from project .env if present."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return {}

    data: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip().lstrip("\ufeff")
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip().lstrip("\ufeff")
        value = value.strip().strip('"').strip("'")
        if key:
            data[key] = value
    return data


def _read_streamlit_secret(*keys: str) -> str:
    """Fetch first non-empty key from Streamlit secrets, if available."""
    try:
        import streamlit as st

        for key in keys:
            value = st.secrets.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    except Exception:
        pass
    return ""


def _resolve_setting(*keys: str, default: str = "") -> str:
    """Resolve setting using env vars, Streamlit secrets, then .env fallback."""
    for key in keys:
        value = os.getenv(key)
        if value and value.strip():
            return value.strip()

    secret_value = _read_streamlit_secret(*keys)
    if secret_value:
        return secret_value

    dotenv_data = _read_dotenv_file()
    for key in keys:
        value = dotenv_data.get(key)
        if value and value.strip():
            return value.strip()

    return default.strip()


_uri = _resolve_setting("MONGODB_URI", "MONGO_URI")
_db_name = _resolve_setting("MONGO_DB_NAME", default="resume_analyzer")
_collection_name = _resolve_setting("MONGO_COLLECTION_NAME", default="analysis_results")

_collection = None
_last_error = ""

if MongoClient is None:
    _last_error = "pymongo is not installed in the active Python environment"
elif not _uri:
    _last_error = "MONGODB_URI/MONGO_URI is not set"
else:
    try:
        _tls_kwargs = {}
        if certifi is not None:
            _tls_kwargs["tlsCAFile"] = certifi.where()
        client = MongoClient(_uri, serverSelectionTimeoutMS=5000, **_tls_kwargs)
        # Fail fast so auth/network issues are visible at startup.
        client.admin.command("ping")
        db = client[_db_name]
        _collection = db[_collection_name]
    except Exception as exc:
        _collection = None
        _last_error = str(exc)


def save_result(data: dict[str, Any]) -> bool:
    """Save one analysis result. Returns True on success, False otherwise."""
    if _collection is None:
        return False
    try:
        _collection.insert_one(data)
        return True
    except Exception as exc:
        global _last_error
        _last_error = str(exc)
        return False


def get_database_status() -> dict[str, Any]:
    """Return current MongoDB connection status for UI diagnostics."""
    return {
        "connected": _collection is not None,
        "uri_configured": bool(_uri),
        "db_name": _db_name,
        "collection_name": _collection_name,
        "error": _last_error,
    }