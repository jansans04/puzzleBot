#!/usr/bin/env python3
# normalize_pieces.py
#
# Rota cada pieza al múltiplo de 90 ° “correcto”, recorta el exceso de lienzo
# y guarda las piezas normalizadas.  Exporta una función `normalizar()` para
# poder llamarla desde otros módulos y, al mismo tiempo, conserva el
# funcionamiento por línea de comandos.
#
# Uso CLI:
#   python normalize_pieces.py -i out_piezas -o pieces
#
# La función normalizar() devuelve un dict {nombre_png: angulo_aplicado}

from __future__ import annotations
import os
import glob
import argparse
import json
from pathlib import Path
from typing import Dict, Tuple

import cv2
import numpy as np


# ────────────────────────────────────────────────
def normalize_image(img: np.ndarray) -> Tuple[np.ndarray, float]:
    """
    Rota la pieza para alinearla verticalmente (múltiplos de 90°) y recorta
    la zona transparente sobrante.
    Devuelve (imagen_normalizada, ángulo_aplicado_en_grados).
    """
    # — separar canal alfa —
    if img.shape[2] == 4:
        bgr, alpha = img[:, :, :3], img[:, :, 3]
    else:
        bgr = img
        alpha = np.full(bgr.shape[:2], 255, dtype=np.uint8)

    # — máscara binaria —
    _, mask = cv2.threshold(alpha, 10, 255, cv2.THRESH_BINARY)
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return img, 0.0

    cnt = max(cnts, key=cv2.contourArea)
    rect = cv2.minAreaRect(cnt)
    angle = rect[-1]

    # Ajustar para que el lado mayor quede horizontal
    if rect[1][0] < rect[1][1]:
        angle += 90

    # — evitar recortes durante la rotación —
    h, w = bgr.shape[:2]
    diag = int(np.sqrt(h**2 + w**2))
    pad_y, pad_x = (diag - h) // 2, (diag - w) // 2
    bgr_pad = cv2.copyMakeBorder(bgr, pad_y, pad_y, pad_x, pad_x,
                                 cv2.BORDER_CONSTANT, value=(255, 255, 255))
    alpha_pad = cv2.copyMakeBorder(alpha, pad_y, pad_y, pad_x, pad_x,
                                   cv2.BORDER_CONSTANT, value=0)

    # — rotar —
    center = (bgr_pad.shape[1] // 2, bgr_pad.shape[0] // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    bgr_rot = cv2.warpAffine(bgr_pad, M, (bgr_pad.shape[1], bgr_pad.shape[0]),
                             flags=cv2.INTER_CUBIC, borderValue=(255, 255, 255))
    alpha_rot = cv2.warpAffine(alpha_pad, M, (alpha_pad.shape[1], alpha_pad.shape[0]),
                               flags=cv2.INTER_NEAREST, borderValue=0)

    # — recortar a la pieza —
    ys, xs = np.where(alpha_rot > 10)
    if ys.size == 0 or xs.size == 0:
        merged = cv2.merge([bgr_rot, alpha_rot])
    else:
        y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
        merged = cv2.merge([bgr_rot[y0:y1+1, x0:x1+1],
                            alpha_rot[y0:y1+1, x0:x1+1]])

    return merged, angle


# ────────────────────────────────────────────────
def normalizar(in_dir: str = "out_piezas", out_dir: str = "pieces") -> Dict[str, float]:
    """
    Normaliza todas las PNG de `in_dir` y las guarda en `out_dir`.
    Devuelve un dict {nombre_archivo: ángulo_aplicado}.
    """
    in_path = Path(in_dir)
    out_path = Path(out_dir)
    out_path.mkdir(exist_ok=True)

    rotaciones: Dict[str, float] = {}

    for fichero in sorted(glob.glob(str(in_path / "*.png"))):
        img = cv2.imread(fichero, cv2.IMREAD_UNCHANGED)
        if img is None:
            print(f"⚠️  No se pudo leer {fichero}")
            continue

        norm, ang = normalize_image(img)
        nombre = os.path.basename(fichero)
        destino = out_path / nombre
        cv2.imwrite(str(destino), norm)
        rotaciones[nombre] = ang
        print(f"✔︎ {nombre:20} → rot {ang:6.2f}°   guardado en {destino}")

    # Resumen
    print("\nResumen de rotaciones:")
    for n, a in rotaciones.items():
        print(f"  · {n:<20} {a:6.2f}°")

    return rotaciones


# ───────────────────────── CLI ───────────────────────────────
def _parse_args():
    p = argparse.ArgumentParser(
        description="Normaliza la orientación de las piezas al múltiplo de 90°"
    )
    p.add_argument("-i", "--input",  default="out_piezas",
                   help="Carpeta con las piezas originales")
    p.add_argument("-o", "--output", default="pieces",
                   help="Carpeta donde guardar las piezas normalizadas")
    p.add_argument("--save-json", action="store_true",
                   help="Guardar fichero rotations.json con los ángulos")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    rot = normalizar(args.input, args.output)

    if args.save_json:
        json_path = Path(args.output) / "rotations.json"
        with open(json_path, "w") as f:
            json.dump(rot, f, indent=2)
        print(f"\n💾  Rotaciones guardadas en {json_path}")
