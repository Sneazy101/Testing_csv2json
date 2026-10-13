import os
import re
import shlex
import shutil
import subprocess
import sys
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "test_data" / "test_files"
EXPECTED_DIR = Path.cwd() / "test_data" / "expected_files"


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
        Path.cwd() / filename_primary,
    ]
    if filename_fallback:
        candidates.extend(
            [
                DATA_DIR / filename_fallback,
                SCRIPT_DIR / filename_fallback,
                Path.cwd() / filename_fallback,
            ]
        )

    for path in candidates:
        if path.is_file():
            return str(path.resolve())

    return str((DATA_DIR / filename_primary).resolve())


def find_expected_file(config_num):
    """Searches for the expected output file corresponding to the configuration."""
    candidates = [
        EXPECTED_DIR / f"expected_{config_num}.json",
        EXPECTED_DIR / f"expected{config_num}.json",
        EXPECTED_DIR / f"output_{config_num}.json",
        EXPECTED_DIR / f"config_{config_num}.json",
        EXPECTED_DIR / f"{config_num}.json",
        EXPECTED_DIR / f"expected_{config_num}.txt",
        SCRIPT_DIR / "test_data" / "expected_files" / f"expected_{config_num}.json",
        SCRIPT_DIR / "test_data" / "expected_files" / f"{config_num}.json",
    ]
    for path in candidates:
        if path.is_file():
            return path
    # Default fallback path for error reporting
    return EXPECTED_DIR / f"expected_{config_num}.json"


def run_acts_tests(acts_file_name, csv2json_bin):
    acts_file = resolve_file(acts_file_name)
    input_csv1 = resolve_file("test_data1.csv")
    input_csv2 = resolve_file("test_data_dailect.csv", "test_data_dialect.csv")
    input_csv3 = resolve_file(
        "test_data_dailect_2.csv", "test_data_dialect_2.csv"
    )

    try:
        with open(acts_file, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        sys.exit(f"Error: Could not find the ACTS file at '{acts_file}'.")

    configs = content.split("-------------------------------------")

    passed_count = 0
    total_tests = 0

        for config in configs:
            if "Configuration #" not in config:
                continue

        config_num_match = re.search(r"Configuration #(\d+):", config)
        if not config_num_match:
            continue
        config_num = config_num_match.group(1)

        dialect_mode = 0  # 0: comma, 1: semicolon, 2: colon
        cli_args = []

        for line in config.strip().split("\n"):
            line = line.strip()
            if "=" in line and not line.startswith("Configuration"):
                parts = line.split("=", 2)
                if len(parts) >= 3:
                    param_name = parts[1].strip()
                    val = parts[2].strip()

                    if param_name == "delimiter":
                        if ";" in val:
                            dialect_mode = 1
                        elif ":" in val:
                            dialect_mode = 2

                    if val != "null":
                        cli_args.extend(shlex.split(val))

        if dialect_mode == 1:
            input_csv = input_csv2
        elif dialect_mode == 2:
            input_csv = input_csv3
        else:
            input_csv = input_csv1

        csv_name = Path(input_csv).name
        command_display = f"{' '.join(cli_args)} {csv_name}".strip()

        total_tests += 1
        print(f"Test # {config_num}")
        print(f"command checked : {command_display}")

        if not Path(input_csv).is_file():
            print("Failed\n")
            continue

        expected_path = find_expected_file(config_num)
        if not expected_path.is_file():
            print("Failed\n")
            continue

        cmd = [csv2json_bin, "--in", input_csv] + cli_args

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=str(SCRIPT_DIR)
            )

            with open(expected_path, "r", encoding="utf-8") as f:
                expected_output = f.read()

            actual_output = result.stdout

            # .strip() prevents newline discrepancies (\r\n vs \n) from triggering false negatives
            if result.returncode == 0 and actual_output.strip() == expected_output.strip():
                print("Passed")
                passed_count += 1
            else:
                print("Failed")

        except Exception:
            print("Failed")

        print()

    print(f"Total Tests Passed : {passed_count}/{total_tests}")


if __name__ == "__main__":
    acts_file = "csv2json_tests-nist.txt"
    csv2json_path = find_csv2json()
    run_acts_tests(acts_file, csv2json_path)