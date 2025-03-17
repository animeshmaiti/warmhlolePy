from flask import Flask, request, jsonify, send_file
import subprocess
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/send", methods=["POST"])
def send():
    file = request.files["file"]
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Run Magic Wormhole as a separate process
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
        return jsonify({"code": code_line})
    else:
        print("No code found.")
        return jsonify({"error": "Failed to send file"}), 500


@app.route("/receive", methods=["POST"])
def receive():
    data = request.get_json()
    code = data.get("code")

    if not code:
        return jsonify({"error": "Code required"}), 400

    # Run Magic Wormhole as a separate process
    result = subprocess.run(["python", "script.py", "receive", code], capture_output=True, text=True)

    # Extract filename from the logs
    file_name = None
    for line in result.stdout.split("\n"):
        if "Receiving file:" in line:
            file_name = line.split(": ")[1].strip()
    print(file_name)
    
    if file_name and os.path.exists(file_name):
        return send_file(file_name, as_attachment=True)

    return jsonify({"error": "Failed to receive file"}), 500


if __name__ == "__main__":
    app.run(debug=True)
