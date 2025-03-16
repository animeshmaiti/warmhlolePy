from flask import Flask, request, jsonify, send_file
import os
import threading
import wormhole
from wormhole.cli import public_relay
from twisted.internet.defer import ensureDeferred
from twisted.internet.task import react

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure upload folder exists

async def send_file_async(reactor, file_path, result):
    """Send a file using Magic Wormhole and store the generated code."""
    appid = "lothar.com/example"
    relay_url = public_relay.RENDEZVOUS_RELAY

    w = wormhole.create(appid, relay_url, reactor)
    w.allocate_code()
    code = await w.get_code()
    result["code"] = code  # Store code in result dict

    await w.get_versions()

    # Send file metadata
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    w.send_message(f"{file_name},{file_size}".encode("utf-8"))

    # Send file data
    with open(file_path, "rb") as f:
        file_data = f.read()
        w.send_message(file_data)

    await w.close()

async def receive_file_async(reactor, code, result):
    """Receive a file using Magic Wormhole and store its path."""
    appid = "lothar.com/example"
    relay_url = public_relay.RENDEZVOUS_RELAY

    w = wormhole.create(appid, relay_url, reactor)
    w.set_code(code)

    # Get file metadata
    msg = await w.get_message()
    file_name, file_size = msg.decode("utf-8").split(",")
    file_size = int(file_size)

    # Receive file data
    file_data = await w.get_message()
    save_path = os.path.join(UPLOAD_FOLDER, file_name)

    with open(save_path, "wb") as f:
        f.write(file_data)

    result["file_path"] = save_path  # Store received file path
    await w.close()

@app.route("/send", methods=["POST"])
def send_file_api():
    """Flask endpoint to send a file using Magic Wormhole."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    result = {}
    thread = threading.Thread(target=react, args=(lambda reactor: ensureDeferred(send_file_async(reactor, file_path, result)),))
    thread.start()
    thread.join()  # Wait for the thread to finish

    return jsonify({"code": result.get("code", "Error generating code")})

@app.route("/receive", methods=["POST"])
def receive_file_api():
    """Flask endpoint to receive a file using Magic Wormhole."""
    data = request.get_json()
    code = data.get("code")

    if not code:
        return jsonify({"error": "No code provided"}), 400

    result = {}
    thread = threading.Thread(target=react, args=(lambda reactor: ensureDeferred(receive_file_async(reactor, code, result)),))
    thread.start()
    thread.join()  # Wait for the thread to finish

    file_path = result.get("file_path")
    if file_path:
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"error": "Failed to receive file"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
