import sys
import wormhole
from wormhole.cli import public_relay
from twisted.internet.defer import ensureDeferred
from twisted.internet.task import react
import os

async def send_file(reactor, file_path):
    """Send a file using Magic Wormhole."""
    appid = "lothar.com/example"
    relay_url = public_relay.RENDEZVOUS_RELAY

    w = wormhole.create(appid, relay_url, reactor)
    w.allocate_code()

    code = await w.get_code()
    print(f"code: {code}",flush=True)

    await w.get_versions()

    # File handling
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    # Send file metadata
    w.send_message(f"{file_name},{file_size}".encode("utf-8"))
    print(f"Sending file: {file_name} ({file_size} bytes)")

    # Send file data
    with open(file_path, "rb") as f:
        file_data = f.read()
        w.send_message(file_data)  # Send as a message

    print("File sent successfully!")
    await w.close()

async def receive_file(reactor, code):
    """Receive a file using Magic Wormhole."""
    appid = "lothar.com/example"
    relay_url = public_relay.RENDEZVOUS_RELAY

    w = wormhole.create(appid, relay_url, reactor)
    w.set_code(code)

    # Get file metadata
    msg = await w.get_message()
    file_name, file_size = msg.decode("utf-8").split(",")
    file_size = int(file_size)

    print(f"Receiving file: {file_name}",flush=True)

    # Receive file data
    file_data = await w.get_message()

    # Save file
    with open(file_name, "wb") as f:
        f.write(file_data)

    print(f"File received: {file_name} ({len(file_data)} bytes)")
    await w.close()

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "send":
        file_path = sys.argv[2]
        react(lambda reactor: ensureDeferred(send_file(reactor, file_path)))
    elif len(sys.argv) > 2 and sys.argv[1] == "receive":
        code = sys.argv[2]
        react(lambda reactor: ensureDeferred(receive_file(reactor, code)))
    else:
        print("Usage:")
        print("  Sender: python script.py send <file_path>")
        print("  Receiver: python script.py receive <code>")
