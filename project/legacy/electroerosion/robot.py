import sys

import numpy as np 

from chain import my_chain

from ikpy.utils.geometry import from_transformation_matrix, to_transformation_matrix
from ikpy.inverse_kinematics import inverse_kinematic_optimization

from log import Log

class RobotCalibration():
    k = np.array([
        90 /     -152.0,
        44 /     70.0,
        90 /    182.5,
        90 /     -113.5,
        90 /  -115550.0,
        90 /      90.0,
    ])

    def units_to_degrees(self, units=(0, 0, 0, 0, 0, 0)):
        return [ round(x,4) for x in np.array(units) * self.k ]

    def degrees_to_units(self, degrees=(0, 0, 0, 0, 0, 0)):
        return [ round(x,4) for x in np.array(degrees) / self.k ]


class RobotState():
    def __init__(self, joints=(0, 0, 0, 0, 0, 0), v=0, operation='', error=None):
        self.joints = joints
        self.v = v
        self.operation = operation
        self.error = error
        self.mins = (-90, -50, -60, -90, -90, -180)
        self.maxs = ( 90,  60,  60,  90,  90,  180)
    

class Robot():
    def __init__(self, port='/dev/ttyUSB0', timeout=10000, outfile=sys.stderr, queue=None):
        from port import Port

        self.port = Port(port=port, outfile=sys.stderr, queue=None)
        self.calibration = RobotCalibration()
        self.state = RobotState()
        self.timeout = timeout

    def __repr__(self):
        return f"Robot({self.port})"

    def set_speed(self, v):
        try:
            assert 1 <= v <= 100, f'Speed not in 1 <= {v} <= 100!'
            self.port.set_speed(v)
            self.state.v = v
            self.state.operation = f'set_speed(v={v})'
            self.state.error = None
        except AssertionError as e:
            self.state.error = str(e)
            raise e
        
    def get_speed(self):
        return self.state.v

    def set_joint_pos(self, joints=(0, 0, 0, 0, 0, 0)):
        try:
            for j_min, j, j_max in zip(self.state.mins, joints, self.state.maxs):
                assert j_min <= j <= j_max, f'Joint not in {j_min} <= {j} <= {j_max}!'
            joints_u = self.calibration.degrees_to_units(joints)
            j1, j2, j3, j4, j5, j6 = joints_u
            self.port.G00(j1, j2, j3, j4, j5, j6)
            self.port.is_ready(self.timeout)
            self.state.joints = joints
            self.state.operation = f'set_joint_pos(joints={joints})'
            self.state.error = None
        except AssertionError as e:
            self.state.error = str(e)
            raise e

    def get_joint_pos(self):
        return self.state.joints

    def is_ready(self):
        return self.state.error is None

    def rot2eul(self, R):
        beta = -np.arcsin(R[2,0])
        alpha = np.arctan2(R[2,1]/np.cos(beta),R[2,2]/np.cos(beta))
        gamma = np.arctan2(R[1,0]/np.cos(beta),R[0,0]/np.cos(beta))

        return [ np.degrees(x) for x in [alpha, beta, gamma] ]

    def eul2rot(self, alpha, beta, gamma):
        alpha = np.radians(alpha)
        beta = np.radians(beta)
        gamma = np.radians(gamma)

        Rx = np.array([ [1, 0, 0],
                        [0, np.cos(alpha), -np.sin(alpha)],
                        [0, np.sin(alpha), np.cos(alpha)]])

        Ry = np.array([ [np.cos(beta), 0, np.sin(beta)],
                        [0, 1, 0],
                        [-np.sin(beta), 0, np.cos(beta)]])

        Rz = np.array([ [np.cos(gamma), -np.sin(gamma), 0],
                        [np.sin(gamma), np.cos(gamma), 0],
                        [0, 0, 1]])

        R = Rz @ (Ry @ Rx)

        return R

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()

    ARGS = [
        # Параметры позиционирования инструмента в миллиметрах
        ('-X',  '--X',  float,  430, 'Положение инструмента по оси X (в миллиметрах)'),
        ('-Y',  '--Y',  float,    0, 'Положение инструмента по оси Y (в миллиметрах)'),
        ('-Z',  '--Z',  float,  277, 'Положение инструмента по оси Z (в миллиметрах)'),

        # Параметры поворота инструмента в градусах
        ('-rX', '--rX', float,    0, 'Угол поворота инструмента вокруг оси X (в градусах)'),
        ('-rY', '--rY', float,    0, 'Угол поворота инструмента вокруг оси Y (в градусах)'),
        ('-rZ', '--rZ', float,    0, 'Угол поворота инструмента вокруг оси Z (в градусах)'),
        ('-rot','--rot',  str, 'all', 'Ось поворота инструмента (возможные значения: all/x/y/z)'),

        # Параметры положения шарниров (суставов) в градусах
        ('-j0', '--j0', float,    0, 'Положение звена №0 (в градусах)'),
        ('-j1', '--j1', float,    0, 'Положение звена №1 (в градусах)'),
        ('-j2', '--j2', float,    0, 'Положение звена №2 (в градусах)'),
        ('-j3', '--j3', float,    0, 'Положение звена №3 (в градусах)'),
        ('-j4', '--j4', float,    0, 'Положение звена №4 (в градусах)'),
        ('-j5', '--j5', float,    0, 'Положение звена №5 (в градусах)'),

        # Параметр скорости выполнения операции
        ('-s', '--speed', int,   10, 'Скорость движения (в процентах от максимальной)')
    ]

    log = Log()
    try:
        robot = Robot()
    except Exception:
        log('[INFO] работа в режиме эмуляции')
        robot = Robot(port=None)

    for a_short, a_long, a_type, a_value, a_help in ARGS:
        parser.add_argument(a_short, a_long, type=a_type, default=a_value, help=a_help)
    
    args = parser.parse_args()
    print(args)

    j0, j1, j2, j3, j4, j5 = args.j0, args.j1, args.j2, args.j3, args.j4, args.j5

    X, Y, Z = args.X / 1000, args.Y / 1000, args.Z / 1000
    rX, rY, rZ = args.rX, args.rY, args.rZ
    rot = args.rot
    speed = args.speed
    
    rotate = robot.eul2rot(rX, rY, rZ)
    target_frame = to_transformation_matrix([X, Y, Z], rotate)
    print(target_frame)
    
    initial_joint_angels = [0, 0, 0, 0, 0, 0, 0, 0]   
    robot.set_speed(speed)

    if sum([j0, j1, j2, j3, j4, j5]):
        print('joints')
        pk = my_chain.forward_kinematics([0,j0, j1, j2, j3, j4, j5,0])
        V, R = from_transformation_matrix(pk)
        A = robot.rot2eul(R)
        print(V, A)
        robot.set_joint_pos([j0, j1, j2, j3, j4, j5])
        
    else:
        print('coordinates')
        #ik = my_chain.inverse_kinematics([X,Y,Z], [rX,rY,rZ], rot)
        ik = inverse_kinematic_optimization(my_chain, target_frame, initial_joint_angels, orientation_mode="all",optimizer="least_squares")
        print(ik)
        fk = my_chain.forward_kinematics(ik)
        vector, rotate = from_transformation_matrix(fk)
        print("vector: ", vector)
        print("rotate: ", robot.rot2eul(rotate))
        print("fk: ", fk)
        #j0, j1, j2, j3, j4, j5 = [ round(np.degrees(x),2) for x in ik ][1:7]
        joints = [round(x,10) for x in np.degrees(ik)][1:7]
        print("joints: ", joints)
        robot.set_joint_pos(joints)
        pk = my_chain.forward_kinematics([0,j0, j1, j2, j3, j4, j5,0])
        V, R = from_transformation_matrix(pk)
        A = robot.rot2eul(R)
        print(V, A)
    print(robot.get_joint_pos())
    
