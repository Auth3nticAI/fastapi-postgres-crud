"""Test bootstrap: put the repo root on sys.path and point the app at a
throwaway SQLite DB before `database`/`main` are imported.
"""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

_tmp = tempfile.mkdtemp(prefix="crud-test-")
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"
