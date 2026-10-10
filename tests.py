import subprocess
import shlex
import re
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

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

        # Initialize the base command
        cmd = [csv2json]

        # Parse the parameter lines for this configuration
        for line in config.strip().split('\n'):
            line = line.strip()

            # Look for lines formatted like "1 = OutputType=--out-dir temp.json"
            if '=' in line and not line.startswith('Configuration'):
                # Split at the first two equals signs
                parts = line.split('=', 2)

                if len(parts) >= 3:
                    val = parts[2].strip()

                    # Ignore 'null' values entirely
                    if val != 'null':
                        # shlex.split handles spaces in arguments correctly
                        # e.g., turning "-D  -a" into ['-D', '-a']
                        # or "--out-name {Index}-{User Id}" into ['--out-name', '{Index}-{User Id}']
                        cmd.extend(shlex.split(val))

        cmd.extend(["--in", input_csv])
        print(f"=== Running Configuration #{config_num} ===")
        print(f"Executing: {' '.join(cmd)}")

        try:
            # Execute the command with subprocess
            result = subprocess.run(cmd, capture_output=True, text=True)

            print(f"Return Code: {result.returncode}")

            if result.stdout:
                # Truncating stdout to 300 characters to prevent terminal flooding
                print(f"Output (truncated): {result.stdout[:300]}...")

            if result.stderr:
                print(f"Error Output:\n{result.stderr}")

        except Exception as e:
            print(f"An unexpected execution error occurred: {e}")

        print("\n")


if __name__ == "__main__":
    # Target files stored as variables
    input_file = "people-10000.csv"
    acts_file = "Simple testCase-nist.txt"

    csv2json = find_csv2json()
    run_acts_tests(acts_file, input_file, csv2json)