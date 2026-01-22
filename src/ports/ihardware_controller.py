class IHardwareController:
    def set_coord_pos(self, x, y, z): pass
    def set_joint_pos(self, joints): pass
    def set_erosion(self, state): pass
    def set_water(self, state): pass
    def pump_control_one(self): pass
    def pump_control_two(self): pass
    def set_speed(self, v): pass
    def emergency_stop(self): pass