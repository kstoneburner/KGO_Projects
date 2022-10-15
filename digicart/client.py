import sys
import socket

print("Launching Client")
# specify Host and Port
HOST = '172.24.132.148'
PORT = 8001
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"Hello, world")
    data = s.recv(1024)

print(f"Received {data!r}")