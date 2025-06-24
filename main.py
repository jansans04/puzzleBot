#!/usr/bin/env python3
"""
main.py – Orquestador complet del pipeline de puzzling
=====================================================

Ara adapta tots els càlculs de posicions i dimensions a centímetres utilitzant
la fórmula de càmera pinhole:

    size_real = pixels * (sensor_size_mm / resolution_px) * (distance_mm / focal_mm)

On:  ▸ sensor_size_mm   – amplada/altura física del sensor (mm)
      ▸ resolution_px     – resolució del sensor en el mateix eix (px)
      ▸ distance_mm       – distància de la càmera a l'objecte (mm)
      ▸ focal_mm          – distància focal (mm)

Configura els valors a la secció «Paràmetres de càmera».

Fluxe:
    1) Segmentar → obté llista de PNG i centres (posicions inicials)
    2) Normalitzar orientació
    3) Resoldre el puzzle (greedy borders)
    4) Combinar angles (normalització + solver)
    5) Calcular posicions destí (top‑left) i convertir‑les a cm
    6) Guardar dos fitxers JSON:
         • solution_greedy.json   → resultat complet (matriu, score, etc.)
         • piezas_info.json       → {rotacions, pos_inicial_cm, pos_desti_cm}

Uso:
    $ python main.py
"""
from __future__ import annotations

from pathlib import Path
import json
from pprint import pformat
from typing import Dict, Tuple

import cv2  # per llegir amplades i alçades

# ─── Paràmetres de càmera (ADAPTA'LS al teu setup!) ────────────────
SENSOR_WIDTH_MM: float   = 6.4   # amplada física del sensor (mm)
SENSOR_HEIGHT_MM: float  = 4.8   # alçada física del sensor (mm)
FOCAL_LENGTH_MM: float   = 4.3   # distància focal (mm)
DISTANCE_OBJ_MM: float   = 600.0 # distància càmera‑objecte (mm)

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

def px_to_cm(px: float, mm_per_px: float) -> float:
    """Converteix *px* a centímetres utilitzant l'escala mm_per_px."""
    return (px * mm_per_px) / 10.0  # 10 mm → 1 cm


def calcular_escales_mm_per_px(img_w_px: int, img_h_px: int) -> Tuple[float, float]:
    """Retorna (mm_per_px_x, mm_per_px_y) segons la pinhole camera model."""
    mm_per_px_x = (SENSOR_WIDTH_MM  / img_w_px) * (DISTANCE_OBJ_MM / FOCAL_LENGTH_MM)
    mm_per_px_y = (SENSOR_HEIGHT_MM / img_h_px) * (DISTANCE_OBJ_MM / FOCAL_LENGTH_MM)
    return mm_per_px_x, mm_per_px_y


def carregar_dimensions(idx2name: Dict[int, str]) -> Dict[int, Tuple[int, int]]:
    """Retorna {idx: (width_px, height_px)} llegint cada PNG de NORM_DIR."""
    dims: Dict[int, Tuple[int, int]] = {}
    for idx, fname in idx2name.items():
        p = Path(fname)
        if not p.is_absolute():
            p = NORM_DIR / p
        img = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)
        if img is None:
            raise FileNotFoundError(f"No es pot obrir la peça: {p}")
        h, w = img.shape[:2]
        dims[idx] = (w, h)
    return dims


def calcular_pos_dest(matrix, dims_px) -> Dict[int, Tuple[int, int]]:
    """A partir de la matriu del solver i les dimensions calcula posicions destí (px).

    L'origen (0,0) és la cantonada superior esquerra del puzzle.
    Cada peça es col·loca a la seva *top‑left* sumant amplades a X i l'alçada
    màxima de la fila a Y.
    """
    pos_desti_px: Dict[int, Tuple[int, int]] = {}
    y_offset = 0
    for row in matrix:
        x_offset = 0
        row_heights = []
        for idx, _ in row:
            pos_desti_px[idx] = (x_offset, y_offset)
            w_px, h_px = dims_px[idx]
            x_offset += w_px
            row_heights.append(h_px)
        if row_heights:
            y_offset += max(row_heights)
    return pos_desti_px


def convertir_a_cm(
    original_px: Dict[int, Tuple[int, int]],
    mm_per_px_x: float,
    mm_per_px_y: float,
) -> Dict[int, Tuple[float, float]]:
    """Converteix {idx: (x_px, y_px)} → {idx: (x_cm, y_cm)}."""
    return {
        idx: (
            px_to_cm(coord_px[0], mm_per_px_x),
            px_to_cm(coord_px[1], mm_per_px_y),
        )
        for idx, coord_px in original_px.items()
    }


def main() -> None:
    # ==================================================================
    # 0) Escala mm/px global – cal la resolució de la imatge d'entrada
    # ------------------------------------------------------------------
    img0 = cv2.imread(str(IN_IMG), cv2.IMREAD_UNCHANGED)
    if img0 is None:
        raise FileNotFoundError(f"No es pot obrir la imatge inicial: {IN_IMG}")
    img_h_px, img_w_px = img0.shape[:2]
    mm_per_px_x, mm_per_px_y = calcular_escales_mm_per_px(img_w_px, img_h_px)

    # 1) Segmentació ----------------------------------------------------
    print("\n🧩 1. Segmentando piezas …")
    rutas_png, posiciones_px = segmentar(str(IN_IMG), str(SEG_DIR))
    print("   Posiciones (centros) de las piezas [px]:")
    print(pformat(posiciones_px, indent=4))

    # 2) Normalització --------------------------------------------------
    print("\n🔄 2. Normalizando orientación …")
    rot_norm = normalizar(str(SEG_DIR), str(NORM_DIR))  # {filename: angle}

    # 3) Solver ---------------------------------------------------------
    print("\n🤖 3. Resolviendo puzzle Greedy …")
    matrix, score, idx2name = solve_greedy(str(NORM_DIR))  # idx2name: idx→filename

    # 4) Combinar angles ------------------------------------------------
    total_rot: Dict[str, float] = {}
    for row in matrix:
        for idx, rot_greedy in row:
            fname = idx2name[idx]
            ang_norm = rot_norm.get(fname, 0.0)
            total_rot[fname] = (ang_norm + rot_greedy) % 360

    # 4.1) Diccionaris sol·licitats ------------------------------------
    rotacions: Dict[int, float] = {idx: total_rot[idx2name[idx]] for idx in idx2name}
    pos_inicial_px: Dict[int, Tuple[int, int]] = posiciones_px  # ja és id→(x,y)

    # 4.2) Dimensions i posicions destí ---------------------------------
    dims_px = carregar_dimensions(idx2name)
    pos_desti_px = calcular_pos_dest(matrix, dims_px)

    # ---------- Convertim TOT a centímetres ----------
    dims_cm: Dict[int, Tuple[float, float]] = {
        idx: (
            px_to_cm(w_px, mm_per_px_x),
            px_to_cm(h_px, mm_per_px_y),
        )
        for idx, (w_px, h_px) in dims_px.items()
    }

    pos_inicial_cm = convertir_a_cm(pos_inicial_px, mm_per_px_x, mm_per_px_y)
    pos_desti_cm   = convertir_a_cm(pos_desti_px,   mm_per_px_x, mm_per_px_y)

    print("\n📐  Posiciones destino (top‑left) [cm]:")
    print(pformat(pos_desti_cm, indent=4))

    # 5) Guardar JSON complet ------------------------------------------
    print(f"\n💾  Guardando matriz, posiciones y rotaciones en {FULL_JSON_PATH}")
    with FULL_JSON_PATH.open('w') as f:
        json.dump({
            "matrix": matrix,
            "positions_px": posiciones_px,
            "positions_cm": pos_inicial_cm,
            "rotations_normalize": rot_norm,
            "rotations_total": total_rot,
            "pos_desti_px": pos_desti_px,
            "pos_desti_cm": pos_desti_cm,
            "dims_px": dims_px,
            "dims_cm": dims_cm,
            "score": score,
            "camera_params": {
                "sensor_width_mm": SENSOR_WIDTH_MM,
                "sensor_height_mm": SENSOR_HEIGHT_MM,
                "focal_length_mm": FOCAL_LENGTH_MM,
                "distance_object_mm": DISTANCE_OBJ_MM,
            },
        }, f, indent=2)

    # 5.1) Guardar JSON simplificat ------------------------------------
    print(f"💾  Guardando rotacions, posicions inicials i destí en {INFO_JSON_PATH}")
    with INFO_JSON_PATH.open('w') as f:
        json.dump({
            "rotacions": rotacions,
            "pos_inicial_cm": pos_inicial_cm,
            "pos_desti_cm": pos_desti_cm,
        }, f, indent=2)

    # Resum per consola -------------------------------------------------
    print("\n✅  Proceso terminado.")
    print("   Rotaciones totales por pieza:")
    for k in sorted(total_rot):
        print(f"   • {k:<20} → {total_rot[k]:6.2f}°")


if __name__ == "__main__":
    main()
