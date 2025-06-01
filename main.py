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
