import os
import subprocess
import shlex
import re
import csv
import shutil
import sys
import random
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

SAMPLE_ROWS = 30
TEST_CSV = "test_input.csv"
NUMERIC_COL = "Index"
FILE_DELIMITER = {"semicolon": ";", "colon": ":"}
OUT_DIR = "temp"
DIMSEP_HEADERS = {
    "dot": ["name.first", "name.last", "address.street"],
}

# parameter values
FLAGS = {
    "delimiter": {"colon": ["-d", ":"], "semicolon": ["-d", ";"]},
    "dimensional_separator": {"dot": ["-D", "."]},
    "array_processing": {"enabled": ["-a"]},
    "output_format": {"folded": ["-F"], "jsonl": ["--jsonl"]},
    "remove_empty": {"strings_only": ["--remove-empty-strings"],
                     "object_only": ["--remove-empty-objects"]},
    "output_dest": {"out_dir": ["--out-dir", OUT_DIR],
                    "out_dir_and_name": ["--out-dir", OUT_DIR, "--out-name", "result"]},
    "type_conversion": {"numeric_only": ["--numeric"], "boolean_only": ["--boolean"]},
}

#find the csv2json executable
def find_csv2json(override_path=None):
    path = shutil.which(override_path or "csv2json")
    if not path:
        sys.exit("Error: 'csv2json' executable not found. Please ensure it is installed and in your PATH.")
    return path

#read the ACTS test file and return its content
def read_test_file(acts_file):
    try:
        with open(acts_file, newline="", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        sys.exit(f"Error: Could not find the ACTS file '{acts_file}'.")
    return content

#read sample data and return header and rows
def read_source_csv(input_csv):
    with open(input_csv, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)
    return header, rows

def write_sample_csv(case, test_csv, src_header, sample_rows):
    with open(test_csv, "w", newline="", encoding="utf-8") as f:
        if case["input_file_stat"] != "empty_file":
            extra = DIMSEP_HEADERS.get(case["dimensional_separator"], [])
            header = src_header + extra
            rows = [row + [""] * len(extra) for row in sample_rows]
            delimiter = FILE_DELIMITER.get(case["delimiter"], ",")
            writer = csv.writer(f, delimiter=delimiter, lineterminator="\n")
            writer.writerow(header)
            writer.writerows(rows)
    return test_csv

def run_acts_tests(acts_file, input_csv, csv2json):
    acts_output = read_test_file(acts_file)
    header, rows = read_source_csv(input_csv)

    # turn the test file into list of test cases
    lines = [l for l in acts_output.splitlines() if l.strip() and not l.startswith("#")]
    cases = list(csv.DictReader(lines))

    counts = {}
    for n, case in enumerate(cases, start=1):
        shutil.rmtree(OUT_DIR, ignore_errors=True)
        os.makedirs(OUT_DIR)

        #pick random sample of rows for this test case
        random.seed(n)  # For reproducible results
        sample_rows = random.sample(rows, min(SAMPLE_ROWS, len(rows)))
        test_file = write_sample_csv(case, TEST_CSV, header, sample_rows)

        # Initialize the base command
        cmd = [csv2json]

        for param, values in FLAGS.items():
            cmd += values.get(case[param], [])
        cmd += ["--in", test_file]

        print(f"========= Running Configuration #{n} =========")
        print(f"Executing: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10,
                                    encoding="utf-8", errors="replace")

            if result.stdout:
                # Truncating stdout to 300 characters to prevent terminal flooding
                print(f"Output (truncated): {result.stdout[:300]}...")

            if result.stderr:
                print(f"Error Output:\n{result.stderr}")

            if result.returncode == 101 or "panicked" in result.stderr:
                verdict = "PANIC"
            elif result.returncode != 0:
                verdict = "ERROR"
            else:
                verdict = "OK"

        except subprocess.TimeoutExpired:
            verdict = "TIMEOUT"
        except Exception as e:
            print(f"An unexpected execution error occurred: {e}")
            verdict = "EXCEPTION"

        print(f"Verdict: {verdict}\n")
        counts[verdict] = counts.get(verdict, 0) + 1

    print("Summary:", counts)


if __name__ == "__main__":
    # Target files stored as variables
    input_file = "people-10000.csv"
    acts_file = "acts_out.csv"

    csv2json = find_csv2json()
    run_acts_tests(acts_file, input_file, csv2json)