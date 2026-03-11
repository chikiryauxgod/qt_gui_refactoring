class StateManager:
    def __init__(self, x0, y0, z0, robot):
        self.current_x = x0
        self.current_y = y0
        self.current_z = z0
        self.current_joints = [0] * 6
        self.updating = False
        self.robot = robot

    def sync_from_robot(self):
        self.current_x = self.robot.current_x
        self.current_y = self.robot.current_y
        self.current_z = self.robot.current_z