import subprocess
import shlex
import re
import shutil
import sys
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_CSV = SCRIPT_DIR / "test_data" / "test_files" / "people-10000.csv"
EMPTY_CSV = str(SCRIPT_DIR / "test_data" / "test_files" / "empty.csv")
TEMP_DIR = str(SCRIPT_DIR / "test_data" / "test_files" / "temp_dir")

COL_FOR_CONVERSION = {
    "--numeric": "Index",
    "--boolean": "HasPets",
}

def find_csv2json(override_path=None):
    path = shutil.which(override_path or "csv2json")
    if not path:
        sys.exit("Error: 'csv2json' executable not found. Please ensure it is installed and in your PATH.")
    return path

def run_acts_tests(acts_file, input_csv, csv2json):
    # Read the generated ACTS test suite
    try:
        with open(acts_file, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find the ACTS file '{acts_file}'.")
        return

    #pass over empty CSV test case if the test says so
    input_files = {
        "valid_data": input_csv,
        "empty_file": EMPTY_CSV,
    }
    open(EMPTY_CSV, "w").close() #create emtpy csv file for testing
    passed = 0
    failed = []

    try:

        # Split the document by the separator lines
        configs = content.split("-------------------------------------")

        for config in configs:
            if "Configuration #" not in config:
                continue

            # Extract the configuration number
            config_num_match = re.search(r'Configuration #(\d+):', config)
            if not config_num_match:
                continue
            config_num = config_num_match.group(1)

            #create fresh temp folder for each test case to avoid file conflicts
            shutil.rmtree(TEMP_DIR, ignore_errors=True)
            os.makedirs(TEMP_DIR, exist_ok=True)

            # Initialize the base command and default input file
            cmd = [csv2json]
            file_for_case = input_csv

            # Parse the parameter lines for this configuration
            for line in config.strip().split('\n'):
                line = line.strip()

                # Look for lines formatted like "1 = OutputType=--out-dir temp.json"
                if '=' in line and not line.startswith('Configuration'):
                    # Split at the first two equals signs
                    parts = line.split('=', 2)

                    if len(parts) >= 3:
                        name = parts[1].strip()
                        val = parts[2].strip()

                        if name == "input_file_stat":
                            file_for_case = input_files.get(val, input_csv)

                        # Ignore 'null' values entirely
                        elif val != 'null':
                            # shlex.split handles spaces in arguments correctly
                            # e.g., turning "-D  -a" into ['-D', '-a']
                            # or "--out-name {Index}-{User Id}" into ['--out-name', '{Index}-{User Id}']
                            for token in shlex.split(val):
                                cmd.append(token)
                                #for type conversion
                                if token in COL_FOR_CONVERSION:
                                    cmd.append(COL_FOR_CONVERSION[token])

            if "--out-dir" in cmd:
                i = cmd.index("--out-dir")
                if i + 1 < len(cmd):
                    cmd[i+1] = TEMP_DIR  # Redirect output to the temporary directory
            
            cmd.extend(["--in", file_for_case])
            print(f"=== Running Configuration #{config_num} ===")
            print(f"Executing: {' '.join(cmd)}")

            try:
                # Execute the command with subprocess
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

                print(f"Return Code: {result.returncode}")

                if result.stdout:
                    # Truncating stdout to 300 characters to prevent terminal flooding
                    print(f"Output (truncated): {result.stdout[:300]}...")

                if result.stderr:
                    print(f"Error Output:\n{result.stderr}")

                if result.returncode == 0:
                    passed += 1
                else:
                    failed.append(config_num)

            except Exception as e:
                print(f"An unexpected execution error occurred: {e}")
                failed.append(config_num)

            print("\n")
    finally:
        Path(EMPTY_CSV).unlink(missing_ok=True)  # remove empty CSV file after tests
        shutil.rmtree(TEMP_DIR, ignore_errors=True)  # remove temp directory after tests

    total = passed + len(failed)
    print("=== Test Summary ===")
    print(f"Total Configurations Tested: {total}")
    print(f"Passed: {passed}")
    if failed:
        print(f"Failed Configurations: {', '.join(failed)}")

if __name__ == "__main__":
    # Target files stored as variables
    input_file = str(INPUT_CSV)
    acts_file = str(SCRIPT_DIR / "test_data" / "test_files" / "csv2json-nist-test.txt")

    csv2json = find_csv2json()
    run_acts_tests(acts_file, input_file, csv2json)