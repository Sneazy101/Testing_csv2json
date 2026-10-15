import sys
import shutil
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "test_data" / "test_files"
ACTS_DIR = SCRIPT_DIR / "ACTS_config"
EXPECTED_DIR = Path.cwd() / "test_data" / "expected_output"


def find_csv2json(override_path=None):
    path = shutil.which(override_path or "csv2json")
    if not path:
        sys.exit(
            "Error: 'csv2json' executable not found. Please ensure it is installed and in your PATH."
        )
    return path


def resolve_file(filename_primary, filename_fallback=None):
    """Searches for a file in DATA_DIR, SCRIPT_DIR, and CWD."""
    candidates = [
        DATA_DIR / filename_primary,
        SCRIPT_DIR / filename_primary,
        ACTS_DIR / filename_primary,
        Path.cwd() / filename_primary,
    ]
    if filename_fallback:
        candidates.extend(
            [
                DATA_DIR / filename_fallback,
                SCRIPT_DIR / filename_fallback,
                ACTS_DIR / filename_primary,
                Path.cwd() / filename_fallback,
            ]
        )

    for path in candidates:
        if path.is_file():
            return str(path.resolve())

    return str((DATA_DIR / filename_primary).resolve())
