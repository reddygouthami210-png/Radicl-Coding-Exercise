import socket
import sys
import json

HOST = "127.0.0.1"
PORT = 6000

file_path = sys.argv[1]

with open(file_path, "r", encoding="utf-8") as f:
    if file_path.endswith(".json"):
        content = json.dumps(json.load(f))
    else:
        content = f.read().strip()

if not content.endswith("\n"):
    content += "\n"

s = socket.socket()
s.connect((HOST, PORT))
s.sendall(content.encode("utf-8"))
s.close()