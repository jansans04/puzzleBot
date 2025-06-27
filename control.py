#!/usr/bin/env python3
# control.py ─ Mòdul de Control  • puzzleBot
# =========================================================
# • Establece un socket con el PC (host/port en CONFIG).
# • Recibe un JSON con la lista de movimientos pick/place
#   (source_x, source_y, dest_x, dest_y, rotation_deg).
# • Orquesta el MovementSystem: homing, pick, servo-giro,
#   place, gestiona errores y responde al PC.
#
#  ⚠  Depende de movement.py  (debe estar en el mismo dir
#     o en PYTHONPATH).
# =========================================================

import json
import socket
import time
from dataclasses import dataclass, asdict
from pathlib import Path

from movement import MovementSystem   # del módulo creado antes

# ──────────────────────────────────────────────────────────
@dataclass
class CONFIG:
    HOST                = "192.168.1.50"   # IP del PC
    PORT                = 5000
    CELL_MM             = 30.0             # mm por casilla
    ORIGIN_X_MM         = 10.0             # mm desde X home
    ORIGIN_Y_MM         = 10.0             # mm desde Y home
    LOG_FILE            = Path("/tmp/puzzlebot_log.txt")

# ──────────────────────────────────────────────────────────
class ControlSystem:
    def __init__(self):
        self.bot = MovementSystem()

    # --------------- socket helpers -----------------------
    def _connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((CONFIG.HOST, CONFIG.PORT))
        self.sock = s
        self._log("Socket conectado con PC")

    def _send(self, obj):
        msg = json.dumps(obj).encode() + b"\n"
        self.sock.sendall(msg)

    def _recv(self):
        data = b""
        while not data.endswith(b"\n"):
            chunk = self.sock.recv(4096)
            if not chunk:
                raise ConnectionError("Conexión cerrada")
            data += chunk
        return json.loads(data)

    # --------------- utilidades ---------------------------
    def _grid_to_mm(self, col: int, row: int):
        x_mm = CONFIG.ORIGIN_X_MM + col * CONFIG.CELL_MM
        y_mm = CONFIG.ORIGIN_Y_MM + row * CONFIG.CELL_MM
        return x_mm, y_mm

    def _log(self, txt: str):
        print(txt)
        CONFIG.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with CONFIG.LOG_FILE.open("a") as f:
            f.write(f"[{time.strftime('%H:%M:%S')}] {txt}\n")

    # --------------- flujo principal ----------------------
    def run(self):
        try:
            self._connect()
            self._send({"status": "READY"})
            plan = self._recv()            # espera lista movimientos
            self._log(f"Plan recibido: {len(plan)} movimientos")

            self.bot.home_all()
            self._send({"status": "HOMED"})

            for idx, mv in enumerate(plan, 1):
                self._execute_move(idx, mv)
                self._send({"status": "DONE", "move": idx})

            self._send({"status": "FINISHED"})
            self._log("Todas las piezas colocadas")

        except Exception as e:
            self._log(f"ERROR: {e}")
            try:
                self._send({"status": "ERROR", "msg": str(e)})
            except Exception:
                pass
        finally:
            self.bot.clean()

    def _execute_move(self, idx: int, mv: dict):
        """
        mv = {
          "src_col": 4, "src_row": 2,
          "dst_col": 1, "dst_row": 0,
          "rot":      90            # deg
        }
        """
        self._log(f"Move {idx}: {mv}")
        sx, sy = self._grid_to_mm(mv["src_col"], mv["src_row"])
        dx, dy = self._grid_to_mm(mv["dst_col"], mv["dst_row"])

        # pick
        self.bot.move_xyz(sx, sy)      # plano XY
        self.bot.pick()

        # girar pieza
        self.bot.servo.rotate(mv["rot"])

        # place
        self.bot.move_xyz(dx - sx, dy - sy)
        self.bot.place()

        # volver servo a 0°
        self.bot.servo.rotate(0)


# ──────────────────────────────────────────────────────────
#               EJECUCIÓN DIRECTA
# ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    ctl = ControlSystem()
    ctl.run()
