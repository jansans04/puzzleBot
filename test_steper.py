import RPi.GPIO as GPIO
import time

DIR = 23   # GPIO 23 (Pin 16)
STEP = 18  # GPIO 18 (Pin 12)
STEPS = 200  # 1 volta

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)

# 🔁 Girar sentit horari
print("Gira en sentit horari")
GPIO.output(DIR, GPIO.HIGH)
for _ in range(STEPS):
    GPIO.output(STEP, GPIO.HIGH)
    time.sleep(0.001)
    GPIO.output(STEP, GPIO.LOW)
    time.sleep(0.001)

time.sleep(1)

# 🔁 Girar sentit antihorari
print("Gira en sentit antihorari")
GPIO.output(DIR, GPIO.LOW)
for _ in range(STEPS):
    GPIO.output(STEP, GPIO.HIGH)
    time.sleep(0.001)
    GPIO.output(STEP, GPIO.LOW)
    time.sleep(0.001)

GPIO.cleanup()
print("Fet!")
