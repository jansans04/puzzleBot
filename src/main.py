#!/usr/bin/env python3
"""
main.py  –  Entrypoint puzzleBot (Raspberry Pi)

▪ Sense arguments         → Mode ONLINE (socket amb el PC).
▪ --offline plan.json     → Executa el plan localment (tests).

Tots els paràmetres d’IP, ports, pins… es llegeixen de config.py.
"""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from config   import CFG
from feedback import Feedback
from control  import ControlSystem
import socket_client_pi          # client online (ja implementat)

# ──────────────────────────────────────────────────────────
def run_offline(plan_file: Path):
    """Executa la llista de moviments sense necessitat de PC."""
    if not plan_file.exists():
        sys.exit(f"Plan {plan_file} no trobat")

    plan = json.loads(plan_file.read_text())

    fb   = Feedback()
    ctrl = ControlSystem(fb)     # Control rep un objecte Feedback

    # callbacks bàsics
    fb.on_estop = lambda: sys.exit(">>> E-STOP premut")
    fb.start()

    ctrl.queue.put(plan)         # encolem la llista sencera
    for status in ctrl.run_iter():
        print("[STATUS]", status)

    fb.close()
    print("Plan finalitzat OK")


def run_online():
    """Mode normal: connecta amb el PC i espera el plan."""
    socket_client_pi.main()      # delega tota la feina al client


# ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="PuzzleBot main – executa plans de moviment"
    )
    ap.add_argument("--offline", metavar="plan.json",
                    help="executa el plan localment, sense socket")
    args = ap.parse_args()

    try:
        if args.offline:
            run_offline(Path(args.offline))
        else:
            run_online()
    except KeyboardInterrupt:
        print("\nInterromput per l’usuari")
