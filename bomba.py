pi@raspberrypi:~/Desktop/puzzleBot $ cat stepper.py
#!/usr/bin/env python3
# test_fullstep_28byj48.py
# Raspberry Pi  --- ULN2003  (+5 V al motor, GND común)
# BCM 8  → IN1   (LED A)
# BCM 7  → IN2   (LED B)
# BCM 12 → IN3   (LED C)
# BCM 13 → IN4   (LED D)

import RPi.GPIO as GPIO
import time

COILS = [8, 7, 12, 13]        # pines BCM en el mismo orden físico
STEP_DELAY = 0.25             # 250 ms: visible a simple vista

FULL_STEP = [
    [1, 0, 0, 0],  # A
    [0, 1, 0, 0],  # B
    [0, 0, 1, 0],  # C
    [0, 0, 0, 1],  # D
]

def setup():
    GPIO.setmode(GPIO.BCM)
    for pin in COILS:
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

def loop():
    while True:
        for phase in FULL_STEP:          # horario
            for pin, val in zip(COILS, phase):
                GPIO.output(pin, val)
            time.sleep(STEP_DELAY)

def cleanup():
    GPIO.output(COILS, GPIO.LOW)
    GPIO.cleanup()

if __name__ == "__main__":
    try:
        setup()
        loop()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()
pi@raspberrypi:~/Desktop/puzzleBot $ cat servo.py
#!/usr/bin/env python3
# servo_test.py  - Gira un servo 180° con RPi.GPIO y PWM a 50 Hz

import RPi.GPIO as GPIO
import time

SERVO_PIN = 18          # BCM 18  (pin físico 12)
FREQ      = 50          # 50 Hz → periodo 20 ms

# Anchos de pulso típicos (SG-90):
# 0°  ≈ 0.5 ms → duty  2.5 %
# 90° ≈ 1.5 ms → duty  7.5 %
# 180°≈ 2.5 ms → duty 12.5 %

ANGLE_2_DUTY = lambda a: 2.5 + (a / 180.0) * 10.0

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SERVO_PIN, GPIO.OUT)
    pwm = GPIO.PWM(SERVO_PIN, FREQ)
    pwm.start(ANGLE_2_DUTY(90))   # posición inicial 90°
    return pwm

def sweep(pwm):
    for angle in (0, 90, 180, 90, 0):
        pwm.ChangeDutyCycle(ANGLE_2_DUTY(angle))
        print(f"→ {angle}°")
        time.sleep(1.2)           # espera a que llegue

def cleanup(pwm):
    pwm.stop()
    GPIO.cleanup()

if __name__ == "__main__":
    try:
        pwm = setup()
        sweep(pwm)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup(pwm)
pi@raspberrypi:~/Desktop/puzzleBot $ cat main.py
from posicionador import ir_a, limpiar

try:
    print("Moviendo a (10, 5)...")
    ir_a(10, 5)

    print("Moviendo a (0, 0)...")
    ir_a(0, 0)

except KeyboardInterrupt:
    print("\nInterrumpido por el usuario")

finally:
    limpiar()
    print("GPIO limpio. Programa terminado.")
pi@raspberrypi:~/Desktop/puzzleBot $ cat posicionador.py
import RPi.GPIO as GPIO
from configuracio import *
from control_motor import setup_motor, mover_pasos, mover_y

# Posición actual del robot
pos_actual = {"x": 0.0, "y": 0.0}

# Inicializar GPIO
GPIO.setmode(GPIO.BCM)
setup_motor(DIR_X1, STEP_X1)
setup_motor(DIR_X2, STEP_X2)
setup_motor(DIR_Y, STEP_Y)
def ir_a(x_dest, y_dest):
    global pos_actual
    dy = y_dest-pos_actual["y"]
    # Calcular desplazamiento
    dx = x_dest - pos_actual["x"]
    pasos_y = int(abs(dx)*PASOS_POR_MM_Y)
    pasos_x = int(abs(dx) * PASOS_POR_MM_X)
    dir_y = dy > 0
    dir_x = dx > 0

    # Mover motores X1 y X2 sincronizados
    #mover_pasos(DIR_X1, STEP_X1, DIR_X2, STEP_X2, pasos_x, dir_x)

    # Mover motor Y
    mover_y(DIR_Y, STEP_Y, pasos_y, dir_y)
    # Actualizar posición
    pos_actual["x"] = x_dest
    pos_actual["y"] = y_dest
def limpiar():
    GPIO.cleanup()
pi@raspberrypi:~/Desktop/puzzleBot $ cat configuracio.py
# ------------ EJE X ------------
DIR_X1  = 27   # físico 13
STEP_X1 = 17   # físico 11

DIR_X2  = 23   # físico 16
STEP_X2 = 22   # físico 15

DIR_Y = 24
STEP_Y = 25

# Configuración física (ajustar cuando sepas los valores reales)
PASOS_POR_MM_X = 400     # Ejemplo: 3200 pasos por vuelta / 8mm por vuelta
PASOS_POR_MM_Y = 400

# Delay entre pasos (controla velocidad)
STEP_DELAY = 0.001  # 1 ms entre flancos

# Microstepping configurado (opcional)
MICROSTEPPING = 16  # 1/16 de paso
pi@raspberrypi:~/Desktop/puzzleBot $ cat control_motor.py
#!/usr/bin/env python3
# bomba_tb6612.py  –  Enciende la bomba 5 s, apaga 5 s en bucle.

import RPi.GPIO as GPIO
import time

PWMA  = 19          # PWM hardware
AIN1  = 26
AIN2  = 20
STBY  = 21
FREQ  = 20000       # 20 kHz, fuera de audio

GPIO.setmode(GPIO.BCM)
GPIO.setup([AIN1, AIN2, STBY], GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(PWMA, GPIO.OUT)
pwm = GPIO.PWM(PWMA, FREQ)
pwm.start(0)        # duty 0 % (parada)

def bomba(on: bool):
    if on:
        GPIO.output(STBY, GPIO.HIGH)
        GPIO.output(AIN1, GPIO.HIGH)   # AIN1=1, AIN2=0 → sentido 1
        GPIO.output(AIN2, GPIO.LOW)
        pwm.ChangeDutyCycle(100)       # 100 % = plena velocidad
    else:
        pwm.ChangeDutyCycle(0)
        GPIO.output(STBY, GPIO.LOW)    # opcional: dormir el driver

try:
    while True:
        print("Bomba ON")
        bomba(True)
        time.sleep(5)
        print("Bomba OFF")
        bomba(False)
        time.sleep(5)
except KeyboardInterrupt:
    pass
finally:
    pwm.stop()
    GPIO.cleanup()
