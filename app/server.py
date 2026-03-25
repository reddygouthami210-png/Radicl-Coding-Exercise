import socket
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.normalizer import LogNormalizer

HOST = "0.0.0.0"
PORT = 6000


def process_line(line, normalizer):
    line = line.strip()

    if not line:
        return

    try:
        result = normalizer.normalize_line(line)
        if result:
            print(json.dumps(result, separators=(",", ":")))
    except Exception as e:
        print("Error:", e)


def start_server():
    normalizer = LogNormalizer()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)

    print(f"Listening on port {PORT}...")

    while True:
        client, addr = server.accept()
        print(f"Connected: {addr}")

        with client:
            buffer = ""

            while True:
                data = client.recv(1024)

                if not data:
                    if buffer.strip():
                        process_line(buffer, normalizer)
                    break

                buffer += data.decode("utf-8", errors="replace")

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    process_line(line, normalizer)


if __name__ == "__main__":
    start_server()
