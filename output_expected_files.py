import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from common import *

def run_acts_tests(acts_file_name, csv2json_bin):
    # Ensure the output directory exists
    EXPECTED_DIR.mkdir(parents=True, exist_ok=True)

    acts_file = resolve_file(acts_file_name)
    input_csv1 = resolve_file("test_data1.csv")
    input_csv2 = resolve_file("test_data_dialect.csv", "test_data_dialect.csv")
    input_csv3 = resolve_file(
        "test_data_dialect_2.csv", "test_data_dialect_2.csv"
    )

    # Pre-flight check
    for label, path_str in [
        ("Comma CSV", input_csv1),
        ("Semicolon CSV", input_csv2),
        ("Colon CSV", input_csv3),
    ]:
        if not Path(path_str).is_file():
            print(f"Warning: {label} file not found at: {path_str}")

    try:
        with open(acts_file, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        sys.exit(f"Error: Could not find the ACTS file at '{acts_file}'.")

    configs = content.split("-------------------------------------")

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

        if not Path(input_csv).is_file():
            print(
                f"Skipping Configuration #{config_num}: Target CSV does not exist: {input_csv}\n"
            )
            continue

        cmd = [csv2json_bin, "--in", input_csv] + cli_args

        print(f"=== Running Configuration #{config_num} ===")
        print(f"Executing: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=str(SCRIPT_DIR)
            )

            print(f"Return Code: {result.returncode}")

            output_file = EXPECTED_DIR / f"config_{config_num}.json"

            if result.returncode == 0:
                with open(output_file, "w", encoding="utf-8") as out_f:
                    out_f.write(result.stdout)
                print(f"Saved JSON output to: {output_file}")
            else:
                print(
                    f"Command failed (Return Code {result.returncode}). Output not saved."
                )

            if result.stderr:
                print(f"Error Output:\n{result.stderr}")

        except Exception as e:
            print(f"An unexpected execution error occurred: {e}")

        print("\n")


if __name__ == "__main__":
    acts_file = "csv2json_tests-nist.txt"
    csv2json_path = find_csv2json()
    run_acts_tests(acts_file, csv2json_path)
