#!/usr/bin/env python3
# segment_pieces.py
#
# Extrae cada pieza de un puzzle sobre fondo negro y las guarda como PNG RGBA.
# Pensado para usarse tanto como módulo importable (función `segmentar`)
# como desde la línea de comandos.
#
# Uso CLI:
#   python segment_pieces.py -i in/puzzle_con_piezas.png -o out_piezas --save-debug
#
# La función `segmentar()` devuelve una lista con las rutas de los PNG generados.

from __future__ import annotations
import os
from pathlib import Path
from typing import List

import cv2
import numpy as np
import argparse


# ──────────────────────────────────────────────────────────────
def segmentar(img_path: str, out_dir: str = "out_piezas", save_debug: bool = False) -> List[str]:
    """
    Segmenta la imagen `img_path` (piezas sobre fondo negro), guarda cada pieza
    en `out_dir` y devuelve la lista completa de rutas PNG creadas.

    Parámetros
    ----------
    img_path : str
        Ruta a la imagen 'puzzle_con_piezas.png'.
    out_dir : str
        Carpeta de salida para las piezas. Se crea si no existe.
    save_debug : bool
        Si es True, se guarda también una imagen 'contornos_detectados.png'
        con los contornos dibujados (útil para depurar sin abrir ventanas).
    """
    # ─── 1. Cargar imagen ─────────────────────────────────────
    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise FileNotFoundError(f"No se pudo leer la imagen: {img_path}")

    # ─── 2. Crear máscara binaria ─────────────────────────────
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)

    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.dilate(mask, kernel, iterations=1)

    # ─── 3. Encontrar contornos ───────────────────────────────
    contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # ─── 4. Guardar imagen con contornos (opcional) ───────────
    if save_debug:
        debug = img.copy()
        cv2.drawContours(debug, contornos, -1, (0, 255, 0), 2)
        debug_path = Path(out_dir).with_name("contornos_detectados.png")
        debug_path.parent.mkdir(exist_ok=True)
        cv2.imwrite(str(debug_path), debug)

    # ─── 5. Extraer piezas + recopilar posiciones ─────────────
    os.makedirs(out_dir, exist_ok=True)
    rutas: List[str] = []
    posiciones: Dict[int, Tuple[int, int]] = {}

    for i, cont in enumerate(contornos):
        x, y, w, h = cv2.boundingRect(cont)
        pieza = img[y : y + h, x : x + w]
        pieza_mask = mask[y : y + h, x : x + w]

        pieza_rgba = cv2.cvtColor(pieza, cv2.COLOR_BGR2BGRA)
        pieza_rgba[:, :, 3] = pieza_mask

        fname = Path(out_dir) / f"piece_{i}.png"
        cv2.imwrite(str(fname), pieza_rgba)
        rutas.append(str(fname))

        # Centro de la pieza (coordenadas en la imagen original)
        xc = int(x + w / 2)
        yc = int(y + h / 2)
        posiciones[i] = (xc, yc)
    return rutas, posiciones

# ───────────────────────── CLI ───────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Segmenta las piezas de un puzzle sobre fondo negro."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Ruta a in/puzzle_con_piezas.png"
    )
    parser.add_argument(
        "-o", "--output", default="out_piezas", help="Carpeta donde guardar las piezas"
    )
    parser.add_argument(
        "--save-debug",
        action="store_true",
        help="Guardar imagen con los contornos detectados",
    )

    args = parser.parse_args()
    segmentar(args.input, args.output, args.save_debug)
