import RPi.GPIO as GPIO
import time
from configuracio import STEP_DELAY

def setup_motor(dir_pin, step_pin):
    GPIO.setup(dir_pin, GPIO.OUT)
    GPIO.setup(step_pin, GPIO.OUT)

def mover_pasos(dir_pin, step_pin, pasos, sentido):
    GPIO.output(dir_pin, GPIO.HIGH if sentido else GPIO.LOW)
    for _ in range(pasos):
        GPIO.output(step_pin, GPIO.HIGH)
        time.sleep(STEP_DELAY)
        GPIO.output(step_pin, GPIO.LOW)
        time.sleep(STEP_DELAY)
