#!/usr/bin/env python3
# feedback.py  –  Mòdul de Retroalimentació  • puzzleBot
# =========================================================
# Supervisa, en segon pla, tots els sensors “digitals” del robot:
#   • 3 finals de carrera (X-, Y-, Z-)  – normally-closed
#   • Presòstat / reed de buit (opcional)
#   • Botó d’emergència (obligatori)
#
# Genera callbacks i enregistra LOG cada vegada que canvia l’estat.
#
# Ús bàsic des de controller.py
# ─────────────────────────────
#   fb = Feedback()
#   fb.on_home        = lambda eje: print(f"{eje} HOME")
#   fb.on_vacuum_lost = lambda:   print("ALERTA: buit perdut")
#   fb.on_estop       = lambda:   sys.exit("E-STOP!")
#   fb.start()        # fils en segon pla
#   ...
#   fb.close()
# =========================================================

from __future__ import annotations
import time, threading
from dataclasses import dataclass
from pathlib import Path
import RPi.GPIO as GPIO
from gpiozero import DigitalInputDevice

# ──────────────────────────────────────────────────────────
@dataclass
class Pins:
    # finals de carrera (NC → GND quan ESTÀ a home)
    X_MIN: int = 5
    Y_MIN: int = 25
    Z_MIN: int = 24

    # presòstat de buit (NC → GND quan hi HA buit)
    VAC_OK: int | None = 14      # None si no n’hi ha

    # emergència (NC → GND quan el botó NO està premut)
    ESTOP: int = 3               # pin 5 físic (I²C-SCL), té pull-up HW

# carpeta de log
LOG_FILE = Path("/tmp/puzzlebot_fb.log")

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# ──────────────────────────────────────────────────────────
class Feedback:
    """Fil de monitorització / callbacks dels sensors."""

    # Callbacks públics (el Controller els assigna)
    on_home:          callable = lambda eje: None
    on_vacuum_lost:   callable = lambda: None
    on_estop:         callable = lambda: None

    _running = False

    def __init__(self, pins: Pins = Pins()):
        self.pins = pins
        self.x = DigitalInputDevice(self.pins.X_MIN, pull_up=True)
        self.y = DigitalInputDevice(self.pins.Y_MIN, pull_up=True)
        self.z = DigitalInputDevice(self.pins.Z_MIN, pull_up=True)

        self.vac = (
            DigitalInputDevice(self.pins.VAC_OK, pull_up=True)
            if self.pins.VAC_OK is not None else None
        )
        self.estop = DigitalInputDevice(self.pins.ESTOP, pull_up=True)

        # darrers estats
        self._last_stop = {"X": self.x.value, "Y": self.y.value, "Z": self.z.value}
        self._last_vac  = self.vac.value if self.vac else 1
        self._last_es   = self.estop.value

    # ──────────────── public API ──────────────────────────
    def start(self):
        if self._running: return
        self._running = True
        self._th = threading.Thread(target=self._loop, daemon=True)
        self._th.start()

    def close(self):
        self._running = False
        if hasattr(self, "_th"): self._th.join(timeout=0.5)
        GPIO.cleanup([
            self.pins.X_MIN, self.pins.Y_MIN, self.pins.Z_MIN,
            *( () if self.vac is None else (self.pins.VAC_OK,) ),
            self.pins.ESTOP
        ])

    # ───────────── bucle de monitorització ────────────────
    def _loop(self):
        self._log("Feedback thread start")
        while self._running:
            self._check_stoppers()
            self._check_vacuum()
            self._check_estop()
            time.sleep(0.01)        # 100 Hz de polling

    # ───────────── detectors individuals ────────────────
    def _check_stoppers(self):
        for eje, dev in (("X", self.x), ("Y", self.y), ("Z", self.z)):
            if dev.value != self._last_stop[eje]:
                self._last_stop[eje] = dev.value
                if dev.value == 0:     # s’ha PREMUT (arribat home)
                    self._log(f"{eje} stopper HIT")
                    self.on_home(eje)

    def _check_vacuum(self):
        if not self.vac: return
        if self.vac.value != self._last_vac:
            self._last_vac = self.vac.value
            if self.vac.value:         # 1 = sense buit
                self._log("Vacuum LOST")
                self.on_vacuum_lost()

    def _check_estop(self):
        if self.estop.value != self._last_es:
            self._last_es = self.estop.value
            if self.estop.value:       # 1 = botó premut
                self._log("E-STOP pressed")
                self.on_estop()

    # ───────────── utilitat de log ───────────────────────
    def _log(self, txt: str):
        print("[FB]", txt)
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        LOG_FILE.write_text(f"[{time.strftime('%H:%M:%S')}] {txt}\n", append=True)

# ──────────────────────────────────────────────────────────
# Auto-test bàsic
# ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    fb = Feedback()

    fb.on_home        = lambda eje: print(f">>> HOME {eje}")
    fb.on_vacuum_lost = lambda:     print(">>> VAC LOST")
    fb.on_estop       = lambda:     sys.exit("EMERGÈNCIA!")

    print("Feedback en marxa. Prem Ctrl-C per sortir.")
    fb.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        fb.close()
        print("Tancat correctament.")
