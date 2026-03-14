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
from typing import Any

try:
    from pymongo import MongoClient
except Exception:
    MongoClient = None


_uri = (os.getenv("MONGODB_URI") or os.getenv("MONGO_URI") or "").strip()
_db_name = (os.getenv("MONGO_DB_NAME") or "resume_analyzer").strip()
_collection_name = (os.getenv("MONGO_COLLECTION_NAME") or "analysis_results").strip()

_collection = None
_last_error = ""

if MongoClient is None:
    _last_error = "pymongo is not installed in the active Python environment"
elif not _uri:
    _last_error = "MONGODB_URI/MONGO_URI is not set"
else:
    try:
        client = MongoClient(_uri, serverSelectionTimeoutMS=5000)
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