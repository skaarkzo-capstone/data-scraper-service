import subprocess

# Runs a subprocess for the given module and arguments.
def run_subprocess(module_path, *args):
    command = ["python", "-m", module_path, *args]
    print(f"Running command: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    print(f"Subprocess completed with return code {result.returncode}")
    if result.stdout:
        print("Output:", result.stdout)
    if result.stderr:
        print("Error:", result.stderr)
    return result
