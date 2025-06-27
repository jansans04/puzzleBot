#!/usr/bin/env python3
# socket_server_pc.py  –  corre al PC

import json, socket, threading
from pathlib import Path
import numpy as np

from planner import generate_plan
from greedy_solver import solve_puzzle   # el teu “greedy” existent

HOST, PORT = "0.0.0.0", 5000

def send(sock, obj):
    sock.sendall(json.dumps(obj).encode() + b"\n")

def recv(sock):
    data = b""
    while not data.endswith(b"\n"):
        data += sock.recv(4096)
    return json.loads(data)

def handle_client(conn, addr):
    print("Pi connectada:", addr)
    hello = recv(conn)
    if hello.get("type") != "HELLO":
        conn.close(); return

    # ➊ – obtenir l’estat inicial del tauler (càmera o fitxer)
    pos_ini = np.loadtxt("pos_inicial.txt", dtype=int)
    # ➋ – executar solver greedy al PC
    puzzle_resol, pos_final, rot = solve_puzzle(pos_ini)
    # ➌ – generar plan
    plan = generate_plan(puzzle_resol, pos_ini, pos_final, rot)
    send(conn, {"type":"PLAN", "data": plan})

    # ➍ – rebre estats
    while True:
        msg = recv(conn)
        if msg["status"] == "FINISHED":
            print("Seqüència acabada!"); break
        elif msg["status"].startswith("ERROR"):
            print("La Pi reporta error:", msg); break
        else:
            print("Pi:", msg["status"])

    conn.close()

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"Escoltant a {HOST}:{PORT}…")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client,
                             args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
