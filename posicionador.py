import RPi.GPIO as GPIO
from configuracio import *
from control_motor import setup_motor, mover_pasos

# Posición actual del robot
pos_actual = {"x": 0.0, "y": 0.0}

# Inicializar GPIO
GPIO.setmode(GPIO.BCM)
setup_motor(DIR_X1, STEP_X1)
setup_motor(DIR_X2, STEP_X2)
setup_motor(DIR_Y, STEP_Y)

def ir_a(x_dest, y_dest):
    global pos_actual

    # Calcular desplazamiento
    dx = x_dest - pos_actual["x"]
    dy = y_dest - pos_actual["y"]

    pasos_x = int(abs(dx) * PASOS_POR_MM_X)
    pasos_y = int(abs(dy) * PASOS_POR_MM_Y)

    dir_x = dx > 0
    dir_y = dy > 0

    # Mover motores X1 y X2 sincronizados
    mover_pasos(DIR_X1, STEP_X1, pasos_x, dir_x)
    mover_pasos(DIR_X2, STEP_X2, pasos_x, dir_x)

    # Mover motor Y
    mover_pasos(DIR_Y, STEP_Y, pasos_y, dir_y)

    # Actualizar posición
    pos_actual["x"] = x_dest
    pos_actual["y"] = y_dest

def limpiar():
    GPIO.cleanup()
