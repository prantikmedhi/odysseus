"""Shared test configuration — ensure project root is on sys.path and stub heavy deps."""
import sys
import os
import types
import importlib.util
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def _has_module(mod_name: str) -> bool:
    try:
        return importlib.util.find_spec(mod_name) is not None
    except (ImportError, ValueError):
        return False


# Stub optional dependencies only when they are not installed. Do not replace
# real FastAPI/Starlette/Pydantic modules: route tests import their subpackages.
for mod_name in [
    "sqlalchemy", "sqlalchemy.orm", "sqlalchemy.types", "sqlalchemy.ext", "sqlalchemy.ext.declarative",
    "sqlalchemy.ext.hybrid", "sqlalchemy.sql", "sqlalchemy.sql.expression",
    "sqlalchemy.sql.sqltypes", "sqlalchemy.engine", "bcrypt", "pyotp",
    "httpx", "fastapi", "fastapi.responses", "fastapi.routing", "fastapi.datastructures",
    "starlette", "starlette.responses", "starlette.middleware", "starlette.middleware.base",
    "pydantic",
]:
    if mod_name not in sys.modules and not _has_module(mod_name):
        _stub = types.ModuleType(mod_name)
        # Give it a MagicMock-like behavior for attributes
        class _StubAttr:
            def __getattr__(self, name):
                if name in ("__path__", "__spec__", "__file__"):
                    raise AttributeError(name)
                return MagicMock()
        
        # Actually, types.ModuleType is better. We can just set __path__ if needed.
        if mod_name in ("sqlalchemy", "fastapi", "starlette"):
            _stub.__path__ = []
        
        # Use a custom __getattr__ to return MagicMocks for everything else
        _stub_mock = MagicMock()
        sys.modules[mod_name] = _stub_mock
        # Wait, the previous version used MagicMock and it failed on __spec__.
        # Let's try to set __spec__ explicitly if it's a MagicMock.
        if not hasattr(_stub_mock, "__spec__"):
             _stub_mock.__spec__ = None
        if mod_name in ("sqlalchemy", "fastapi", "starlette"):
             _stub_mock.__path__ = []

if "src.database" not in sys.modules:
    _db = types.ModuleType("src.database")
    _db.SessionLocal = MagicMock()
    _db.ModelEndpoint = MagicMock()
    sys.modules["src.database"] = _db
