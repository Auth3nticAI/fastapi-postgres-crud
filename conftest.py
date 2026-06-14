"""Point the app at a throwaway SQLite DB before `database`/`main` import.
`load_dotenv(override=False)` won't clobber a value already in os.environ.
"""
import os
import tempfile

_tmp = tempfile.mkdtemp(prefix="crud-test-")
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"
