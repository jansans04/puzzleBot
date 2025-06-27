#!/usr/bin/env python3
# movement.py ─ Mòdul de Moviment  • puzzleBot
# =========================================================
# Controla:
#   ▸ Dos NEMA-17 para eje X  (drivers STEP/DIR)
#   ▸ Un NEMA-17 para eje Y
#   ▸ Un 28BYJ-48 (ULN2003)   para eje Z
#   ▸ Bomba de vacío          (TB6612 o relé)
#   ▸ Servo SG-90/MG-90S      para rotación de pieza
#   ▸ 3 finales de carrera (X-, Y-, Z-) para homing
#
# Todas las constantes hardware se agrupan en CONFIG.
# =========================================================

from __future__ import annotations
import time
from dataclasses import dataclass
import RPi.GPIO as GPIO
from gpiozero import OutputDevice, DigitalInputDevice, PWMOutputDevice

# ──────────────────────────────────────────────────────────
# CONFIG ─ adapta SOLO este bloque a tu hardware
# ──────────────────────────────────────────────────────────
@dataclass
class CONFIG:
    # Eje X ─ 2 NEMA-17 en paralelo
    DIR_X1, STEP_X1 = 27, 17
    DIR_X2, STEP_X2 = 23, 22
    STOP_X_MIN      = 5          # normally-closed → GND cuando está “home”
    MICROSTEP_X     = 16
    PITCH_X_MM      = 8          # mm / vuelta del husillo

    # Eje Y ─ 1 NEMA-17
    DIR_Y, STEP_Y   = 6, 16
    STOP_Y_MIN      = 25
    MICROSTEP_Y     = 16
    PITCH_Y_MM      = 8

    # Eje Z ─ 28BYJ-48
    COILS_Z         = (8,7,12,13)   # IN1-IN4
    STOP_Z_MIN      = 24
    STEP_DELAY_Z    = 0.001         # s
    #                      32 × 64 / “full-step”  = 2048
    STEPS_REV_Z     = 2048

    # Servo
    SERVO_PIN       = 18
    SERVO_FREQ      = 50

    # Bomba ─ TB6612 (default)  • si usas relé activo-bajo, pon PUMP_USE_RELAY=True
    PUMP_USE_RELAY  = False
    PWMA, AIN1, AIN2, STBY = 19, 26, 20, 21   # puente-H
    RELAY_IN        = 4                       # solo si PUMP_USE_RELAY = True

    # Velocidades
    F_STEP_DELAY    = 0.0006     # delay base para aceleración (≈ 1.6 kHz máx)
    LIMIT_FREQ      = 0.00005    # retardo mínimo seguro (20 kHz máx)

# ──────────────────────────────────────────────────────────
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# ──────────────────────────────────────────────────────────
#                                                          #
#       CLASES DE ACTUADOR DE BAJO NIVEL                   #
#                                                          #
# ──────────────────────────────────────────────────────────
def _ramp_delay(step_idx: int, total: int, base: float, floor: float) -> float:
    """Perfil trapezoidal lineal: acelera mitad, frena mitad."""
    half = total // 2
    if step_idx < half:
        k = 1 - (step_idx / half)          # 1 → 0
    else:
        k = (step_idx - half) / half       # 0 → 1
    return floor + k * (base - floor)


class DualStepper:
    """Dos drivers STEP/DIR que deben moverse en paralelo (eje X)."""

    def __init__(self, dir_a, step_a, dir_b, step_b,
                 steps_per_mm: float,
                 stop_pin: int | None = None):
        self.dir_a, self.step_a = dir_a, step_a
        self.dir_b, self.step_b = dir_b, step_b
        for p in (dir_a, step_a, dir_b, step_b):
            GPIO.setup(p, GPIO.OUT, initial=GPIO.LOW)
        self.steps_per_mm = steps_per_mm
        self.stop = DigitalInputDevice(stop_pin, pull_up=True) if stop_pin else None

    # ───────────────────────────────────────
    def move_mm(self, mm: float):
        steps = int(abs(mm) * self.steps_per_mm)
        self.move_steps(steps, forward=mm > 0)

    def move_steps(self, steps: int, forward=True):
        GPIO.output(self.dir_a, GPIO.HIGH if forward else GPIO.LOW)
        GPIO.output(self.dir_b, GPIO.HIGH if forward else GPIO.LOW)
        for i in range(steps):
            d = _ramp_delay(i, steps, CONFIG.F_STEP_DELAY, CONFIG.LIMIT_FREQ)
            GPIO.output(self.step_a, GPIO.HIGH)
            GPIO.output(self.step_b, GPIO.HIGH)
            time.sleep(d)
            GPIO.output(self.step_a, GPIO.LOW)
            GPIO.output(self.step_b, GPIO.LOW)
            time.sleep(d)

    def home(self, backoff_mm: float = 2.0):
        if not self.stop:
            raise RuntimeError("No hay pin de stopper configurado.")
        # avance lento hasta que el stopper abra (recordar: NC → 1 cuando pulsa)
        GPIO.output(self.dir_a, GPIO.LOW)
        GPIO.output(self.dir_b, GPIO.LOW)
        while self.stop.value:  # 1 => NO pulsado
            GPIO.output(self.step_a, GPIO.HIGH)
            GPIO.output(self.step_b, GPIO.HIGH)
            time.sleep(0.002)
            GPIO.output(self.step_a, GPIO.LOW)
            GPIO.output(self.step_b, GPIO.LOW)
            time.sleep(0.002)
        # alejarse un poco
        self.move_mm(backoff_mm)


class SingleStepper:
    """Driver único STEP/DIR (eje Y)."""

    def __init__(self, dir_pin, step_pin, steps_per_mm, stop_pin=None):
        self.dir = dir_pin
        self.step = step_pin
        for p in (dir_pin, step_pin):
            GPIO.setup(p, GPIO.OUT, initial=GPIO.LOW)
        self.steps_per_mm = steps_per_mm
        self.stop = DigitalInputDevice(stop_pin, pull_up=True) if stop_pin else None

    def _pulse(self, delay):
        GPIO.output(self.step, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(self.step, GPIO.LOW)
        time.sleep(delay)

    def move_mm(self, mm: float):
        steps = int(abs(mm) * self.steps_per_mm)
        self.move_steps(steps, forward=mm > 0)

    def move_steps(self, steps: int, forward=True):
        GPIO.output(self.dir, GPIO.HIGH if forward else GPIO.LOW)
        for i in range(steps):
            d = _ramp_delay(i, steps, CONFIG.F_STEP_DELAY, CONFIG.LIMIT_FREQ)
            self._pulse(d)

    def home(self, backoff_mm=2):
        if not self.stop:
            raise RuntimeError("No hay pin stopper.")
        GPIO.output(self.dir, GPIO.LOW)
        while self.stop.value:
            self._pulse(0.002)
        self.move_mm(backoff_mm)


class BYJ48:
    """28BYJ-48 en full-step."""

    _SEQ = ((1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1))

    def __init__(self, coil_pins: tuple[int,int,int,int], stop_pin: int):
        self.coils = [OutputDevice(p) for p in coil_pins]
        self.stop = DigitalInputDevice(stop_pin, pull_up=True)

    def _set_phase(self, ph):
        for c,v in zip(self.coils, ph): c.value = v

    def move_rev(self, rev: float, up=True):
        steps = int(rev * CONFIG.STEPS_REV_Z)
        seq   = self._SEQ if up else tuple(reversed(self._SEQ))
        for i in range(steps):
            self._set_phase(seq[i & 3])
            time.sleep(CONFIG.STEP_DELAY_Z)

    def home(self, backoff_rev=0.05):
        while self.stop.value:
            self._set_phase(self._SEQ[3])  # paso hacia abajo
            time.sleep(CONFIG.STEP_DELAY_Z)
        self.move_rev(backoff_rev, up=True)


class Servo:
    def __init__(self, pin: int):
        GPIO.setup(pin, GPIO.OUT)
        self.pwm = GPIO.PWM(pin, CONFIG.SERVO_FREQ)
        self.pwm.start(self._duty(90))

    @staticmethod
    def _duty(deg: float):
        return 2.5 + deg/180*10

    def rotate(self, deg: float):
        self.pwm.ChangeDutyCycle(self._duty(deg))
        time.sleep(0.8)


class Pump:
    def __init__(self):
        if CONFIG.PUMP_USE_RELAY:
            GPIO.setup(CONFIG.RELAY_IN, GPIO.OUT, initial=GPIO.HIGH)
        else:
            GPIO.setup(CONFIG.STBY, GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(CONFIG.AIN1, GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(CONFIG.AIN2, GPIO.OUT, initial=GPIO.LOW)
            self.pwm = PWMOutputDevice(CONFIG.PWMA, frequency=1000)

    def on(self):
        if CONFIG.PUMP_USE_RELAY:
            GPIO.output(CONFIG.RELAY_IN, GPIO.LOW)     # relé activo-bajo
        else:
            GPIO.output(CONFIG.STBY, GPIO.HIGH)
            GPIO.output(CONFIG.AIN1, GPIO.HIGH)
            GPIO.output(CONFIG.AIN2, GPIO.LOW)
            self.pwm.value = 1.0

    def off(self):
        if CONFIG.PUMP_USE_RELAY:
            GPIO.output(CONFIG.RELAY_IN, GPIO.HIGH)
        else:
            self.pwm.value = 0
            GPIO.output(CONFIG.STBY, GPIO.LOW)

# ──────────────────────────────────────────────────────────
#                                                          #
#           WRAPPER DE ALTO NIVEL                          #
#                                                          #
# ──────────────────────────────────────────────────────────
class MovementSystem:
    """Interface única para el resto del software (Control / Planner)."""

    def __init__(self):
        # Pasos/mm
        spmm_x = 200*CONFIG.MICROSTEP_X / CONFIG.PITCH_X_MM
        spmm_y = 200*CONFIG.MICROSTEP_Y / CONFIG.PITCH_Y_MM

        self.x = DualStepper(CONFIG.DIR_X1, CONFIG.STEP_X1,
                             CONFIG.DIR_X2, CONFIG.STEP_X2,
                             spmm_x, CONFIG.STOP_X_MIN)

        self.y = SingleStepper(CONFIG.DIR_Y, CONFIG.STEP_Y,
                               spmm_y, CONFIG.STOP_Y_MIN)

        self.z = BYJ48(CONFIG.COILS_Z, CONFIG.STOP_Z_MIN)
        self.servo = Servo(CONFIG.SERVO_PIN)
        self.pump  = Pump()

    # métodos de confort ------------------------------------
    def home_all(self):
        self.z.home()
        self.y.home()
        self.x.home()

    def move_xyz(self, dx_mm: float, dy_mm: float, dz_rev: float = 0.0):
        if dz_rev > 0:  self.z.move_rev(dz_rev, up=True)
        if dz_rev < 0:  self.z.move_rev(-dz_rev, up=False)
        if dx_mm:       self.x.move_mm(dx_mm)
        if dy_mm:       self.y.move_mm(dy_mm)

    # acciones pick & place ---------------------------------
    def pick(self):
        self.z.move_rev(2, up=False)
        self.pump.on()
        time.sleep(0.3)
        self.z.move_rev(2, up=True)

    def place(self):
        self.z.move_rev(2, up=False)
        self.pump.off()
        time.sleep(0.2)
        self.z.move_rev(2, up=True)

    # limpieza ----------------------------------------------
    def clean(self):
        GPIO.cleanup()
        print("GPIO limpio.")

# ──────────────────────────────────────────────────────────
#    AUTO-TEST INTERACTIVO
# ──────────────────────────────────────────────────────────
if __name__ == '__main__':
    bot = MovementSystem()
    try:
        print("Homing…")
        bot.home_all()

        while True:
            cmd = input("\nComando [x mm / y mm / up / dn / pick / place / servo deg / quit] > ").strip().lower()
            if cmd == "quit":
                break
            elif cmd.startswith("x"):
                bot.x.move_mm(float(cmd.split()[1]))
            elif cmd.startswith("y"):
                bot.y.move_mm(float(cmd.split()[1]))
            elif cmd == "up":
                bot.z.move_rev(1, up=True)
            elif cmd == "dn":
                bot.z.move_rev(1, up=False)
            elif cmd == "pick":
                bot.pick()
            elif cmd == "place":
                bot.place()
            elif cmd.startswith("servo"):
                bot.servo.rotate(float(cmd.split()[1]))
            else:
                print("Comando no reconocido.")
    except KeyboardInterrupt:
        pass
    finally:
        bot.clean()
