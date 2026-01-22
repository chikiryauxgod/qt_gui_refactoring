# Hardware controller implementation
from src.ports.ihardware_controller import IHardwareController
from src.electoerosion import Electroerosion
from src.robot import Robot
from src.pico import Pico

class HardwareController(IHardwareController):
    def __init__(self, erode=None):
        self.erode = erode or Electroerosion()
        self.robot = self.erode.robot if self.erode.robot else Robot()
        self.pico = self.erode.erosion if self.erode.erosion else Pico()
        self.state_pump_one = False
        self.state_pump_two = False

    def set_coord_pos(self, x, y, z):
        self.erode.set_coord_pos(x, y, z)
        self.robot.current_x = x
        self.robot.current_y = y
        self.robot.current_z = z

    def set_joint_pos(self, joints):
        self.robot.set_joint_pos(joints)

    def set_erosion(self, state):
        self.pico.erosion(1 if state else 0)

    def set_water(self, state):
        self.pico.pump_in(1 if state else 0)
        self.pico.pump_out(1 if state else 0)

    def pump_control_one(self):
        self.state_pump_one = not self.state_pump_one
        self.pico.pump_in(1 if self.state_pump_one else 0)

    def pump_control_two(self):
        self.state_pump_two = not self.state_pump_two
        self.pico.pump_out(1 if self.state_pump_two else 0)

    def set_speed(self, v):
        self.robot.set_speed(v)

    def emergency_stop(self):
        self.robot.emergency_stop()
