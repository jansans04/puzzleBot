"""
motion_executor.py – Executor d'accions pick‑and‑place per al robot cartesiano
==========================================================================

Aquest mòdul implementa una capa prima d'alt nivell que rep dues taules
(dicionaris) amb les posicions inicials i destí de cada peça i genera les
ordres concretes per als controladors de moviment (G‑code, Step/Dir, etc.).

La lògica segueix exactament el flux requerit:
    1. Moure a la posició de la peça.
    2. Baixar l'eix Z fins a alçada de recollida.
    3. Activar succió i esperar estabilització.
    4. Aplicar la rotació indicada.
    5. Pujar Z fins a alçada segura.
    6. Moure a la posició destí.
    7. Baixar Z per deixar la peça.
    8. Desactivar succió.
    9. Pujar Z a alçada segura.

Abstracció de capa de control
-----------------------------
El mòdul no depèn directament de la implementació del maquinari: utilitza una
interfície mínima (`BaseController`) que qualsevol driver (G‑code via USB, API
CAN de Duet/Clipper, pigpio directe, etc.) pot implementar.


"""
from __future__ import annotations

import time
import threading
from dataclasses import dataclass, field
from typing import Dict, Tuple, Sequence, Optional, Iterable

Position = Tuple[float, float]  # (x, y) en mil·límetres


class BaseController:
    """Interfície mínima que ha d'implementar el driver físic."""

    # --- Moviment lineal -------------------------------------------------
    def move_linear(self, *, x: float | None = None, y: float | None = None,
                    z: float | None = None, feedrate: float = 1500.0) -> None:  # noqa: D401
        """Mou els eixos especificats a velocitat (mm/min)."""
        raise NotImplementedError

    # --- Ventosa ----------------------------------------------------------
    def set_vacuum(self, on: bool) -> None:  # noqa: D401
        """Activa o desactiva la succió."""
        raise NotImplementedError

    # --- Servomotor de rotació -------------------------------------------
    def rotate_tool(self, angle_deg: float) -> None:  # noqa: D401
        """Gira la ventosa a l'angle especificat (0‑360°)."""
        raise NotImplementedError

    # --- Utilitats -------------------------------------------------------
    def dwell(self, seconds: float) -> None:  # noqa: D401
        """Pausa durant *seconds* segons (blocking)."""
        time.sleep(seconds)


class GCodeController(BaseController):
    """Driver senzill que envia G‑code a un firmware (GRBL, Klipper, Duet…)."""

    def __init__(self, port: str, baudrate: int = 115200):
        import serial  # Lazy per evitar dep. si no s'utilitza
        self.ser = serial.Serial(port, baudrate, timeout=1)
        self._lock = threading.Lock()

    # Utilities -----------------------------------------------------------
    def _send(self, line: str) -> None:
        """Envia una línia de G‑code i espera l'OK."""
        with self._lock:
            self.ser.write((line + "\n").encode())
            self.ser.flush()
            self.ser.readline()  # Bloqueja fins a rebre 'ok\n'

    # Implementació de BaseController ------------------------------------
    def move_linear(self, *, x: float | None = None, y: float | None = None,
                    z: float | None = None, feedrate: float = 1500.0) -> None:
        cmd = "G0"  # G0 ràpid (canvia a G1 si vols control de feedrate precis)
        if x is not None:
            cmd += f" X{x:.3f}"
        if y is not None:
            cmd += f" Y{y:.3f}"
        if z is not None:
            cmd += f" Z{z:.3f}"
        cmd += f" F{feedrate:.0f}"
        self._send(cmd)

    def set_vacuum(self, on: bool) -> None:
        self._send("M8" if on else "M9")  # M8/M9 refrigerant → repurpose

    def rotate_tool(self, angle_deg: float) -> None:
        # Exemple amb M280 (Servo): canal 0, angle directament
        angle_deg = angle_deg % 360
        self._send(f"M280 P0 S{angle_deg:.1f}")


@dataclass
class MotionExecutor:
    ctrl: BaseController
    pick_z: float = -10.0          # Alçada Z per recollir la peça (mm relatiu)
    place_z: float = -10.0         # Alçada Z per deixar la peça (mm)
    safe_z: float = 5.0            # Alçada Z segura per a translacions XY (mm)
    feed_xy: float = 3000.0        # Velocitat XY en mm/min
    feed_z: float = 800.0          # Velocitat Z en mm/min
    vacuum_delay: float = 0.2      # Segons per estabilitzar succió

    # --- API pública ------------------------------------------------------
    def execute(self,
                pos_ini: Dict[str, Position],
                pos_dest: Dict[str, Position],
                rotations: Optional[Dict[str, float]] = None,
                order: Optional[Sequence[str]] = None) -> None:
        """Executa el pick‑and‑place de totes les peces.

        :param pos_ini:  {id → (x, y)} posicions inicials.
        :param pos_dest: {id → (x, y)} destins.
        :param rotations: {id → angle_deg} (opcional) rotació per a cada peça.
        :param order: llista explícita d'ids per l'ordre d'execució.
        """
        if order is None:
            # Ordena per id si l'usuari no dona ordre explícita
            order = sorted(pos_ini.keys())
        missing = [i for i in order if i not in pos_dest]
        if missing:
            raise KeyError(f"Destination position missing for ids: {missing}")

        for piece_id in order:
            self._pick(piece_id, pos_ini[piece_id])
            theta = (rotations or {}).get(piece_id, 0.0)
            self.ctrl.rotate_tool(theta)
            self._place(piece_id, pos_dest[piece_id])

    # --- Operacions internes --------------------------------------------
    def _pick(self, piece_id: str, pos: Position) -> None:
        x, y = pos
        # 1. Moure XY a sobre de la peça a alçada segura
        self.ctrl.move_linear(x=x, y=y, z=self.safe_z, feedrate=self.feed_xy)
        # 2. Baixar Z fins pick_z
        self.ctrl.move_linear(z=self.pick_z, feedrate=self.feed_z)
        # 3. Activar succió i esperar
        self.ctrl.set_vacuum(True)
        self.ctrl.dwell(self.vacuum_delay)
        # 4. Pujar Z a safe_z
        self.ctrl.move_linear(z=self.safe_z, feedrate=self.feed_z)

    def _place(self, piece_id: str, pos: Position) -> None:
        x, y = pos
        # 5. Moure XY al destí amb la peça ja col·locada a safe_z
        self.ctrl.move_linear(x=x, y=y, z=self.safe_z, feedrate=self.feed_xy)
        # 6. Baixar Z fins place_z
        self.ctrl.move_linear(z=self.place_z, feedrate=self.feed_z)
        # 7. Desactivar succió per deixar la peça
        self.ctrl.set_vacuum(False)
        # 8. Pujar Z a safe_z per allunyar-se
        self.ctrl.move_linear(z=self.safe_z, feedrate=self.feed_z)

    # --- Helpers ---------------------------------------------------------
    def set_safe_z(self, z: float) -> None:
        """Permet modificar l'alçada segura en temps d'execució (p.ex. calibració)."""
        self.safe_z = z
