import subprocess

file_path = "uploads/my_file.txt"

# Start subprocess in the background
process = subprocess.Popen(
    ["python", "script.py", "send", file_path], 
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
)

# Extract the code
code_line = None
for _ in range(10):  # Read first 10 lines, assuming code appears early
    output = process.stdout.readline().strip()
    if output.startswith("code: "):
        code_line = output.split("code: ")[1]
        break

if code_line:
    print(f"Extracted Code: {code_line}")
else:
    print("No code found.")

# Keep the process running in the background (do NOT use `process.wait()`)
# process.wait()  # Wait for the process to finish