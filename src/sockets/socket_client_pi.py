#!/usr/bin/env python3
# socket_client_pi.py  –  corre a la Raspberry

import json, socket, threading, time
from control import ControlSystem        # importem el teu mòdul de Control

HOST, PORT = "192.168.1.50", 5000        # IP/port del PC

def send(sock, obj):
    sock.sendall(json.dumps(obj).encode() + b"\n")

def recv(sock):
    data = b""
    while not data.endswith(b"\n"):
        data += sock.recv(4096)
    return json.loads(data)

def listener(ctrl: ControlSystem, sock):
    """Escolta ordres PLAN del PC i les passa al controlador."""
    while True:
        msg = recv(sock)
        if msg.get("type") == "PLAN":
            ctrl.queue.put(msg["data"])          # encola el pla
        else:
            print("Missatge desconegut:", msg)

def main():
    ctrl = ControlSystem()          # ja conté MovementSystem i Feedback
    sock = socket.create_connection((HOST, PORT), timeout=10)
    send(sock, {"type": "HELLO", "who":"puzzlePi"})
    threading.Thread(target=listener, args=(ctrl,sock), daemon=True).start()

    try:
        for status in ctrl.run_iter():           # iterador que produeix estat
            send(sock, {"type": "STATUS", "status": status})
    except Exception as e:
        send(sock, {"type": "STATUS", "status": "ERROR", "msg": str(e)})
    finally:
        sock.close()

if __name__ == "__main__":
    main()
