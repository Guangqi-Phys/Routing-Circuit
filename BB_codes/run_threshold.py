import os
import subprocess

# Directory containing the test scripts
test_dir = '/Users/guangqi/Library/CloudStorage/Dropbox/APhD_workspace/BB code/qft_circ/test/threshold'

# List all Python files in the test directory
test_files = [f for f in os.listdir(test_dir) if f.endswith('.py')]

# Run each test file
for test_file in test_files:
    test_path = os.path.join(test_dir, test_file)
    print(f'Running {test_file}...')
    subprocess.run(['python3', test_path])