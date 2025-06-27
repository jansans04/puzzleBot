#!/usr/bin/env python3
"""
main.py – Orquestador complet del pipeline de puzzling
=====================================================

Fluxe:
    1) Segmentar → obté llista de PNG i centres (posicions inicials)
    2) Normalitzar orientació
    3) Resoldre el puzzle (greedy borders)
    4) Combinar angles (normalització + solver)
    5) Guardar dos fitxers JSON:
         • solution_greedy.json   → resultat complet (matriu, score, etc.)
         • piezas_info.json       → només {rotacions, pos_inicial}

Usage:
    $ python main.py
"""
from __future__ import annotations

from pathlib import Path
import json
from pprint import pformat

# ─── Mòduls propis ───────────────────────────────────────────
from segment_pieces import segmentar            # 1) Segmentar
from normalize_pieces import normalizar         # 2) Normalitzar
from solve_puzzle_borders import solve_greedy   # 3) Solver

# ─── Paths bàsics (relatius al mateix script) ───────────────
BASE_DIR = Path(__file__).resolve().parent
IN_IMG         = BASE_DIR / "in" / "puzzle_con_piezas.png"
SEG_DIR        = BASE_DIR / "out_piezas"
NORM_DIR       = BASE_DIR / "pieces"
SOLUTION_PNG   = BASE_DIR / "solution_greedy.png"
FULL_JSON_PATH = BASE_DIR / "solution_greedy.json"   # JSON complet
INFO_JSON_PATH = BASE_DIR / "piezas_info.json"       # JSON simplificat

# Assegurem carpetes d'eixida
SEG_DIR.mkdir(exist_ok=True)
NORM_DIR.mkdir(exist_ok=True)

# ─────────────────────────────────────────────────────────────

def main() -> None:
    # 1) Segmentació ----------------------------------------------------
    print("\n🧩 1. Segmentando piezas …")
    rutas_png, posiciones = segmentar(str(IN_IMG), str(SEG_DIR))
    print("   Posiciones (centros) de las piezas:")
    print(pformat(posiciones, indent=4))

    # 2) Normalització --------------------------------------------------
    print("\n🔄 2. Normalizando orientación …")
    rot_norm = normalizar(str(SEG_DIR), str(NORM_DIR))  # {filename: angle}

    # 3) Solver ---------------------------------------------------------
    print("\n🤖 3. Resolviendo puzzle Greedy …")
    matrix, score, idx2name = solve_greedy(str(NORM_DIR))  # idx2name: idx→filename

    # 4) Combinar angles ------------------------------------------------
    total_rot: dict[str, float] = {}
    for row in matrix:
        for idx, rot_greedy in row:
            fname = idx2name[idx]
            ang_norm = rot_norm.get(fname, 0.0)
            total_rot[fname] = (ang_norm + rot_greedy) % 360

    # 4.1) Construir diccionaris sol·licitats ---------------------------
    #    rotacions:    {id: rot_total °}
    #    pos_inicial:  {id: (xc, yc)}  (ja està com 'posiciones')
    rotacions: dict[int, float] = {idx: total_rot[idx2name[idx]] for idx in idx2name}
    pos_inicial: dict[int, tuple[int, int]] = posiciones  # ja en format id→(x,y)

    # 5) Guardar JSON complet ------------------------------------------
    print(f"\n💾  Guardando matriz, posiciones y rotaciones en {FULL_JSON_PATH}")
    with FULL_JSON_PATH.open('w') as f:
        json.dump({
            "matrix": matrix,
            "positions": posiciones,
            "rotations_normalize": rot_norm,
            "rotations_total": total_rot,
            "score": score,
        }, f, indent=2)

    # 5.1) Guardar JSON simplificat ------------------------------------
    print(f"💾  Guardando rotacions i posicions inicials en {INFO_JSON_PATH}")
    with INFO_JSON_PATH.open('w') as f:
        json.dump({
            "rotacions": rotacions,
            "pos_inicial": pos_inicial,
        }, f, indent=2)

    # Resum per consola -------------------------------------------------
    print("\n✅  Proceso terminado.")
    print("   Rotaciones totales por pieza:")
    for k in sorted(total_rot):
        print(f"   • {k:<20} → {total_rot[k]:6.2f}°")


if __name__ == "__main__":
    main()
