#!/usr/bin/env python3
# planner.py  –  Mòdul de Planificació  • puzzleBot
# =========================================================
# Entrada  (desde el PC o desde el Mòdul de Resolució):
#   • puzzle_resuelto  → matriz NxM con el ID correcto de cada pieza
#   • pos_inicial      → matriz NxM con el ID que hay antes de empezar
#   • pos_final        → matriz NxM con la casilla destino de cada ID
#   • rotaciones       → matriz NxM con el ángulo (0-270) para cada ID
#
# Salida:
#   ▸ lista “plan” de movimientos en orden optimizado (greedy NN):
#       [
#          {"src_col": 3, "src_row": 0,
#           "dst_col": 1, "dst_row": 2,
#           "rot": 180},
#           ...
#       ]
#
# El ControlSystem ejecutará la lista uno a uno.
# =========================================================

from __future__ import annotations
import json
from dataclasses import dataclass
from math import hypot
from pathlib import Path
from typing import List, Tuple

import numpy as np

# ──────────────────────────────────────────────────────────
#   MODELOS DE DATOS
# ──────────────────────────────────────────────────────────
@dataclass
class Move:
    src_col: int
    src_row: int
    dst_col: int
    dst_row: int
    rot: int          # en grados 0, 90, 180, 270

    def as_dict(self):
        return {
            "src_col": self.src_col, "src_row": self.src_row,
            "dst_col": self.dst_col, "dst_row": self.dst_row,
            "rot":      self.rot
        }

# ──────────────────────────────────────────────────────────
#   FUNCIONES AUXILIARES
# ──────────────────────────────────────────────────────────
def _coords(matrix: np.ndarray, piece_id: int) -> Tuple[int, int]:
    """Devuelve (col,row) donde aparece piece_id en matrix."""
    pos = np.where(matrix == piece_id)
    return int(pos[1][0]), int(pos[0][0])     # (x, y)

def _nearest(current: Tuple[int, int], targets: List[Tuple[int,int]]):
    """Devuelve índice del objetivo más cercano a current."""
    cx, cy = current
    dists = [hypot(tx-cx, ty-cy) for tx,ty in targets]
    return int(np.argmin(dists))

# ──────────────────────────────────────────────────────────
#   GENERADOR DE PLAN
# ──────────────────────────────────────────────────────────
def generate_plan(puzzle_resuelto: np.ndarray,
                  pos_inicial:   np.ndarray,
                  pos_final:     np.ndarray,
                  rotaciones:    np.ndarray) -> List[dict]:
    """
    Devuelve lista de Move en orden “ruta más corta” greedy.
    """
    plan: List[Move] = []
    # 1) Construir lista completa de movimientos pendientes
    pending: List[Tuple[Tuple[int,int], Tuple[int,int], int]] = []
    for piece_id in np.unique(puzzle_resuelto):
        sx, sy = _coords(pos_inicial, piece_id)
        dx, dy = _coords(pos_final,   piece_id)
        if (sx, sy) != (dx, dy):              # ya está en su sitio? => saltar
            rot = int(rotaciones[sy, sx])
            pending.append(((sx, sy), (dx, dy), rot))

    # 2) Greedy — siempre ir al source más cercano
    cursor = (0, 0)                           # brazo parte del home (0,0)
    while pending:
        idx = _nearest(cursor, [src for src,_,_ in pending])
        src, dst, rot = pending.pop(idx)
        plan.append(Move(src[0], src[1], dst[0], dst[1], rot))
        cursor = dst                          # nueva posición del brazo

    return [mv.as_dict() for mv in plan]

# ──────────────────────────────────────────────────────────
#   UTILIDAD DE LÍNEA DE COMANDOS  (para depurar)
#   $ python3 planner.py puzzle.json > plan.json
# ──────────────────────────────────────────────────────────
def _load_np(file: Path) -> np.ndarray:
    return np.array(json.loads(file.read_text()))

if __name__ == "__main__":
    import argparse, sys
    ap = argparse.ArgumentParser(description="Genera plan greedy.")
    ap.add_argument("json", help="fichero JSON con matrices",
                    type=Path)
    args = ap.parse_args()

    data = json.loads(args.json.read_text())
    plan = generate_plan(np.array(data["puzzle_resuelto"]),
                         np.array(data["pos_inicial"]),
                         np.array(data["pos_final"]),
                         np.array(data["rotaciones"]))
    json.dump(plan, sys.stdout, indent=2)
    sys.stdout.write("\n")
