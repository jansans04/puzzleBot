# Pines GPIO
DIR_X1 = 23     # Dirección motor X1
DIR_X2 = 24     # Dirección motor X2 (si es independiente)
DIR_Y = 27      # Dirección motor Y

STEP_X1 = 18    # Paso motor X1
STEP_X2 = 25    # Paso motor X2 (si es independiente)
STEP_Y = 22     # Paso motor Y

# Configuración física (ajustar cuando sepas los valores reales)
PASOS_POR_MM_X = 400     # Ejemplo: 3200 pasos por vuelta / 8mm por vuelta
PASOS_POR_MM_Y = 400

# Delay entre pasos (controla velocidad)
STEP_DELAY = 0.001  # 1 ms entre flancos

# Microstepping configurado (opcional)
MICROSTEPPING = 16  # 1/16 de paso
