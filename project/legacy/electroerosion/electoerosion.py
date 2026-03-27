import argparse
import math
import sys
import numpy as np

from time import sleep
from datetime import datetime

from ikpy.inverse_kinematics import inverse_kinematic_optimization

import robot
import pico

from chain import my_chain
from gcode_proc import gcode_proc
from log import Log

SLEEP_TIMES = {
    'emulated': {
        'pump_in': 60,
        'pump_out': 60,
        'pump_15s': 15,
        'erosion': 0,
        'erosion_up': 0,
        'safe_finish': 60,
    },
    'work': {
        'pump_in': 60,
        'pump_out': 60,
        'pump_15s': 15,
        'erosion': 10,
        'erosion_up': 10,
        'safe_finish': 60,
    },
    'test' : {
        'pump_in': 0,
        'pump_out': 0,
        'pump_15s': 0,
        'erosion': 0,
        'erosion_up': 0,
        'safe_finish': 0,
    }
}

ARGS = [
    ('-X',  '--X',  float, 430, 'Начальная позиция по оси X (мм).'),
    ('-Y',  '--Y',  float,   0, 'Начальная позиция по оси Y (мм).'),
    ('-Z',  '--Z',  float, 277, 'Начальная позиция по оси Z (мм).'),

    ('-XS', '--XS', float,   0, 'Калиброванная позиция по оси X (мм).'),
    ('-YS', '--YS', float,   0, 'Калиброванная позиция по оси Y (мм).'),
    ('-ZS', '--ZS', float,   0, 'Калиброванная позиция по оси Z (мм).'),

    ('-DE', '--DE', float,   0, 'Диаметр электрода (мм).'),

    ('-f',  '--input-file', str, '', 'Входной файл G-code.'),
    ('-s',  '--speed', int, 10, 'Скорость в процентах.'),
    ('-m',  '--mode',  str, 'test', 'Режим работы: work (рабочий), test (тестовый), emulated (эмулируемый)'),
]

class Electroerosion():

    def init_robot(self, port, outfile, queue):
        try:
            r = robot.Robot(port=port, outfile=outfile, queue=queue)
        except Exception:
            r = robot.Robot(port=None, outfile=outfile, queue=queue)
            self.log('Работа в режиме эмуляции манипулятора')

        return r


    def init_erosion(self, port, outfile, queue):
        try:
            p = pico.Pico(port=port, outfile=outfile, queue=queue)
            self.is_emulated = False
        except Exception:
            p = pico.Pico(port=None,  outfile=outfile, queue=queue)
            self.is_emulated = True
            self.mode = 'emulated'
            self.log('Работа в режиме эмуляции эрозии')

        return p

    def __init__(self,
                 d_e=2,
                 X=0, Y=0, Z=0,
                 XS=0, YS=0, ZS=0,
                 robot_port='/dev/ttyUSB0',
                 erosion_port='/dev/ttyACM0',
                 outfile=sys.stderr, queue=None):

        self.log = Log()

        self.date = datetime.now()
        self.log(f"Дата/время начала работ: {self.date}")

        self.queue = queue

        self.d_e = d_e

        self.X_0, self.Y_0, self.Z_0 = X, Y, Z
        self.XS, self.YS, self.ZS = XS, YS, ZS

        self.initial_angles = [0, 0, 0, 0, 0, 0, 0, 0]
        self.chain = my_chain
        self.path = 0

        self.robot = self.init_robot(robot_port, outfile, queue)
        self.erosion = self.init_erosion(erosion_port, outfile, queue)

        self.log("Инициализация завершена успешно")


    def set_coord_pos(self, x=None, y=None, z=None):
        self.log(f"Устанавливаем позицию: {(x, y, z)}...")
        x = self.X if x is None else x
        y = self.Y if y is None else y
        z = self.Z if z is None else z
        target = np.array([
            [1, 0, 0, x/1000],
            [0, 1, 0, y/1000],
            [0, 0, 1, z/1000],
            [0, 0, 0, 1]
        ])
        ik = inverse_kinematic_optimization(
            self.chain,
            target,
            self.initial_angles,
            orientation_mode="all"
        )
        joints = [round(x,10) for x in np.degrees(ik)][1:7]

        self.log(f"Положение суставов: {joints}")
        
        return self.robot.set_joint_pos(joints)


    def calc_z_scale(self):
        return 0.001


    def safe_finish(self):
        try:
            self.log("Начинаем безопасное завершение работы...")
            self.log(f"Прошли путь: {self.path}")
            self.log("Поднимаем электрод")
            self.erosion.position('up')
            sleep(SLEEP_TIMES[self.mode]['safe_finish'])
            self.log("Откачиваем воду")

            self.erosion.pump_in(0)
            self.erosion.pump_out(1)
            sleep(SLEEP_TIMES[self.mode]['safe_finish'])
            self.erosion.pump_out(0)

            self.piko_turn_off()
            self.go_to_home_positon()
            self.log("Конец безопасного завершения работы.")
        except KeyboardInterrupt:
            self.safe_finish()


    def __call__(self, input_file=None, speed=10, mode='test', params=None):
        self.mode = mode
        self.speed = speed
        assert input_file, 'Файл не передан'
        if params:
            self.d_e = params['d_e']
            print(self.d_e, file=sys.stderr)
            self.X_0, self.Y_0, self.Z_0 = params['X'], params['Y'], params['Z']
            self.XS, self.YS, self.ZS = params['XS'], params['YS'], params['ZS']
        print(self.X_0, self.Y_0, self.Z_0, file=sys.stderr)
        print(self.XS, self.YS, self.ZS, file=sys.stderr)
        z_scale = self.calc_z_scale()
        code, vectors = gcode_proc(input_file)
        try:
            self.robot.set_speed(speed)
            self.log('Накачиваем воду.')
            if mode != 'test':
                self.erosion.pump_in(1)
                sleep(SLEEP_TIMES[mode]['pump_in'])
                self.erosion.pump_out(1)
            x0, y0, _z0 = self.X_0, self.Y_0, self.Z_0
            self.path = 0
            for x1, y1, line_depth, e, _ in vectors:
                x1 = x1 + self.X_0 - self.XS
                y1 = y1 + self.Y_0 - self.YS
                z1 = ((-line_depth) * z_scale) + self.Z_0 - self.ZS
                if e:
                    points = self._divide_line(((x0, y0), (x1, y1)), self.d_e)
                    for p in points:
                        (_,_),(x,y) = p
                        self.set_coord_pos(x, y, z1)
                        dx = x1 - x0
                        dy = y1 - y0
                        length = math.hypot(dx, dy)
                        self.path += length
                        if mode == 'work':
                            self.to_erode()
                else:
                    self.set_coord_pos(x1, y1, z1)
                x0, y0, _z0 = x1, y1, z1
        except KeyboardInterrupt:
            self.log('Прервано пользователем')
            self.safe_finish()

        self.safe_finish()
        
 
    def _divide_line(self, line, d):
        (x0, y0), (x1, y1) = line
        dx = x1 - x0
        dy = y1 - y0
        length = math.hypot(dx, dy)
        try:
            n = round(length / d)
     
            segments = []
            for k in range(n + 1):
                t = k / n
                x = round(x0 + dx * t,2)
                y = round(y0 + dy * t,2)
                segments.append((x, y))
     
            divided_lines = []
            for i in range(n):
                line = (segments[i], segments[i + 1])
                divided_lines.append(line)
        except ZeroDivisionError:
            divided_lines = [line]
        return divided_lines

    def go_to_home_positon(self):
        #встаём в изначальную позицию
        self._rotate_by_joints(0,0,0,0,0,0)

        print("[INFO] Встали в домашнюю позицию", file=sys.stderr)
    
    def turn_on_pump(self):
        self.erosion.pump_in(1), print(6, self.q.get())
        sleep(SLEEP_TIMES[self.mode]['pump_15s'])
        self.erosion.pump_in(0), print(6, self.q.get())

    def turn_off_pump(self):
        self.erosion.pump_out(1), print(8, self.q.get())
        sleep(SLEEP_TIMES[self.mode]['pump_15s'])

    def piko_turn_off(self):
        self.erosion.erosion(0)
        self.erosion.reset()

    def to_erode(self):
        print("[INFO] начали эрозию")
        self.erosion.erosion(1)
        sleep(SLEEP_TIMES[self.mode]['erosion'])

        for _ in range(10):
            self.erosion.position("down")
            sleep(0.2)
            self.erosion.position("middle")
            sleep(0.1)
            
        print("[INFO] пошли вверх")
        self.erosion.position("up")
        self.erosion.pump_out(0)
        sleep(SLEEP_TIMES[self.mode]['erosion_up'])
        self.erosion.pump_out(1)

    def _rotate_by_joints(self, j0, j1, j2, j3, j4, j5):
        self.robot.set_joint_pos((j0, j1, j2, j3, j4, j5))


if __name__ == '__main__':
    parser = argparse.ArgumentParser() # ???

    for a_short, a_long, a_type, a_value, a_help in ARGS:
        parser.add_argument(a_short, a_long, type=a_type, default=a_value, help=a_help)

    args = parser.parse_args()
    d_e = args.DE
    X = args.X
    Y = args.Y
    Z = args.Z
    XS = args.XS
    YS = args.YS
    ZS = args.ZS

    input_file = args.input_file
    speed = args.speed
    mode = args.mode
    erode = Electroerosion(d_e, X, Y, Z, XS, YS, ZS)
    erode(input_file, speed, mode)
    
    

