from planificacio_moviment import MotionExecutor, GCodeController

pos_ini  = {'p1': (10, 10)}
pos_dest = {'p1': (100, 80)}
rot      = {'p1': 90}

ctrl = GCodeController('/dev/ttyUSB0', baudrate=250000)
exec = MotionExecutor(ctrl)
exec.execute(pos_ini, pos_dest, rotations=rot)
