import re
import shlex
import subprocess
import sys
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
        SCRIPT_DIR / "test_data" / "expected_output" / f"expected_{config_num}.json",
        SCRIPT_DIR / "test_data" / "expected_output" / f"{config_num}.json",
    ]
    for path in candidates:
        if path.is_file():
            return path
    # Default fallback path for error reporting
    return EXPECTED_DIR / f"expected_{config_num}.json"


def run_acts_tests(acts_file_name, csv2json_bin):
    acts_file = resolve_file(acts_file_name)
    input_csv1 = resolve_file("test_data1.csv")
    input_csv2 = resolve_file("test_data_dialect.csv", "test_data_dialect.csv")
    input_csv3 = resolve_file(
        "test_data_dialect_2.csv", "test_data_dialect_2.csv"
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
                expected_output = test_data_n.csv: Failed : The Program does not support line breaks for data_type intest_data_n.csv
test_data_rn.csv: Failed : The Program does not support line breaks for data_type intest_data_rn.csvf.read()

            actual_output = result.stdout

            # .strip() prevents newline discrepancies (\r\n vs \n) from triggering false negatives
            if result.returncode == 0 and actual_output.strip() == expected_output.strip():
                print("Passed")
                passed_count += 1
            else:
                print("Failed")

        except Exception:
            print("Failed (exception)")

    print(f"Combinotorial Tests Passed : {passed_count}/{total_tests}")

def run_line_ending_test(csv2json_bin):
    expected_path = Path.cwd() / "test_data" / "starter_files" / "test_data1.json"
    if not expected_path.is_file():
        expected_path = SCRIPT_DIR / "test_data" / "starter_files" / "test_data1.json"

    expected = expected_path.read_text(encoding="utf-8")

    test_files_dir = Path.cwd() / "test_data" / "test_files"
    if not test_files_dir.is_dir():
        test_files_dir = SCRIPT_DIR / "test_data" / "test_files"

    for filename in ["test_data_n.csv", "test_data_rn.csv"]:
        csv_file = test_files_dir / filename

        res = subprocess.run(
            [csv2json_bin, "--in", str(csv_file)],
            capture_output=True,
            text=True,
        )

        status = (
            "Passed"
            if res.returncode == 0 and res.stdout == expected
    else "Failed : The Program does not support line breaks for data_type in" + filename
        )
        print(f"{filename}: {status}")

def run_file_output_test(csv2json_bin):
    """Tests if csv2json generates file output using --out-dir and matches test_data1.json."""
    input_csv = Path(resolve_file("test_data1.csv"))

    # Output directory where csv2json will place the generated JSON
    output_dir = DATA_DIR
    generated_json = output_dir / "test_data1.json"

    # Expected baseline file
    expected_path = Path.cwd() / "test_data" / "starter_files" / "test_data1.json"
    if not expected_path.is_file():
        expected_path = SCRIPT_DIR / "test_data" / "starter_files" / "test_data1.json"

    expected_content = expected_path.read_text(encoding="utf-8")

    # Remove any pre-existing output file before running
    if generated_json.is_file():
        generated_json.unlink()

    # Pass --out-dir with the DIRECTORY path, not a filename
    res = subprocess.run(
        [csv2json_bin, "--in", str(input_csv), "--out-dir", str(output_dir)],
        capture_output=True,
        text=True,
        cwd=str(SCRIPT_DIR),
    )

    if not generated_json.is_file():
        print(f"test_data1.json: Failed (File was not created in {output_dir})")
        if res.stderr.strip():
            print(f"  Error: {res.stderr.strip()}")
        return

    actual_content = generated_json.read_text(encoding="utf-8")
    status = (
        "Passed"
        if res.returncode == 0
        and actual_content.strip() == expected_content.strip()
        else "Failed"
    )
    print(f"Test for file output (file output): {status}")

if __name__ == "__main__":
    acts_file = "csv2json_tests-nist.txt"
    csv2json_path = find_csv2json()
    run_acts_tests(acts_file, csv2json_path)
    run_line_ending_test(csv2json_path)
    run_file_output_test(csv2json_path)