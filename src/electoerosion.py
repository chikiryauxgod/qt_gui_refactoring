from src.robot import Robot
from src.pico import Pico 

class Electroerosion:
    def __init__(self, filename=None, speed=10, mode="test"):
        self.filename = filename
        self.speed = speed
        self.mode = mode

        self.robot = Robot()
        self.erosion = Pico()

        print(f"[ELECTROEROSION - stub] filename={filename}, speed={speed}, mode={mode}")

    def set_coord_pos(self, x, y, z):
        print(f"[ELECTROEROSION - stub] set_coord_pos({x}, {y}, {z})")
        self.robot.current_x = x
        self.robot.current_y = y
        self.robot.current_z = z

    def start(self):
        print("[ELECTROEROSION - stub] start() called")

    def stop(self):
        print("[ELECTROEROSION - stub] stop() called")
