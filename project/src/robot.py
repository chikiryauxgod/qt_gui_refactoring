from src.domain.constants import X0, Y0, Z0

class Robot:
    def __init__(self):
        self.current_x = X0
        self.current_y = Y0
        self.current_z = Z0
        self.speed = 0
        self.joints = [0] * 6

    def set_joint_pos(self, joints):
        self.joints = joints
        print(f"[ROBOT - stub] set_joint_pos {joints}")

    def set_speed(self, v):
        self.speed = v
        print(f"[ROBOT - stub] set_speed {v}")

    def emergency_stop(self):
        print("[ROBOT - stub] EMERGENCY STOP")
