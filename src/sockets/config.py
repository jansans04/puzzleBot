#!/usr/bin/env python3
# config.py  –  Paràmetres globals de puzzleBot
# ======================================================================
# ▸ TOTS els altres mòduls han de fer:
#       from config import CFG
#   i usar CFG.<parametre>
#
# ▸ Pots sobreescriure qualsevol valor amb una variable d’entorn:
#       export PUMP_USE_RELAY=1
#       python3 control.py
# ======================================================================

from __future__ import annotations
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Tuple

# ──────────────────────────────────────────────────────────
def _env_bool(key: str, default=False):
    return bool(int(os.getenv(key, "1" if default else "0")))

def _env(key: str, default, cast):
    return cast(os.getenv(key, default))

# ──────────────────────────────────────────────────────────
@dataclass
class _Hardware:
    # ---------- EIX X (dos NEMA-17) ----------
    DIR_X1:  int = _env("DIR_X1", 27, int)
    STEP_X1: int = _env("STEP_X1", 17, int)
    DIR_X2:  int = _env("DIR_X2", 23, int)
    STEP_X2: int = _env("STEP_X2", 22, int)
    STOP_X_MIN: int = _env("STOP_X_MIN", 5, int)          # NC → GND

    MICROSTEP_X: int = _env("MICROSTEP_X", 16, int)
    PITCH_X_MM:  float = _env("PITCH_X_MM", 8.0, float)   # pas d'husillo

    # ---------- EIX Y (un NEMA-17) ----------
    DIR_Y:  int = _env("DIR_Y", 6, int)
    STEP_Y: int = _env("STEP_Y", 16, int)
    STOP_Y_MIN: int = _env("STOP_Y_MIN", 25, int)

    MICROSTEP_Y: int = _env("MICROSTEP_Y", 16, int)
    PITCH_Y_MM:  float = _env("PITCH_Y_MM", 8.0, float)

    # ---------- EIX Z (28BYJ-48) ----------
    COILS_Z: Tuple[int,int,int,int] = (
        _env("Z_IN1", 8, int),
        _env("Z_IN2", 7, int),
        _env("Z_IN3", 12, int),
        _env("Z_IN4", 13, int),
    )
    STOP_Z_MIN: int = _env("STOP_Z_MIN", 24, int)
    STEPS_REV_Z: int = _env("STEPS_REV_Z", 2048, int)
    STEP_DELAY_Z: float = _env("STEP_DELAY_Z", 0.001, float)  # s

    # ---------- SERVO ----------
    SERVO_PIN: int = _env("SERVO_PIN", 18, int)
    SERVO_FREQ: int = _env("SERVO_FREQ", 50, int)

    # ---------- BOMBA ----------
    PUMP_USE_RELAY: bool = _env_bool("PUMP_USE_RELAY", False)
    # TB6612
    PWMA: int = _env("PWMA", 19, int)
    AIN1: int = _env("AIN1", 26, int)
    AIN2: int = _env("AIN2", 20, int)
    STBY: int = _env("STBY", 21, int)
    # relé
    RELAY_IN: int = _env("RELAY_IN", 4, int)

    # ---------- SENSOR DE BUIT ----------
    VAC_OK: int | None = _env("VAC_OK", 14, int)  # None si no n'hi ha

    # ---------- EMERGÈNCIA ----------
    ESTOP: int = _env("ESTOP", 3, int)            # pin 5 físic (SCL)

# ──────────────────────────────────────────────────────────
@dataclass
class _Motion:
    # Delays de base per a l'acceleració trapezoïdal
    F_STEP_DELAY: float = _env("F_STEP_DELAY", 0.0006, float)
    LIMIT_FREQ:   float = _env("LIMIT_FREQ",   0.00005, float)

# ──────────────────────────────────────────────────────────
@dataclass
class _Network:
    HOST_PC: str = os.getenv("HOST_PC", "192.168.1.50")
    PORT_PC: int = _env("PORT_PC", 5000, int)

# ──────────────────────────────────────────────────────────
@dataclass
class _Workspace:
    CELL_MM:     float = _env("CELL_MM", 30.0, float)      # mida casella
    ORIGIN_X_MM: float = _env("ORIGIN_X_MM", 10.0, float)
    ORIGIN_Y_MM: float = _env("ORIGIN_Y_MM", 10.0, float)

# ──────────────────────────────────────────────────────────
@dataclass
class _Logging:
    LOG_DIR: Path = Path(os.getenv("LOG_DIR", "/tmp"))
    def __post_init__(self):
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
    @property
    def CTRL(self) -> Path: return self.LOG_DIR / "ctrl.log"
    @property
    def FB(self)   -> Path: return self.LOG_DIR / "feedback.log"

# ──────────────────────────────────────────────────────────
@dataclass
class _CFG:
    HW:  _Hardware = field(default_factory=_Hardware)
    MOT: _Motion   = field(default_factory=_Motion)
    NET: _Network  = field(default_factory=_Network)
    WS:  _Workspace= field(default_factory=_Workspace)
    LOG: _Logging  = field(default_factory=_Logging)

    # utilitat ràpida per veure-ho tot
    def dump(self):
        import json, pprint
        pprint.pp(json.loads(json.dumps(asdict(self), indent=2)))

# instància singleton
CFG = _CFG()

# prova ràpida quan s’executa directament
if __name__ == "__main__":
    print("Configuració carregada:")
    CFG.dump()
