class Robot:
    def __init__(self, *args, **kwargs):
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_z = 0.0

    def emergency_stop(self):
        print("[ROBOT] Emergency stop")

    def start_erosion_process(self, *args, **kwargs):
        print("[ROBOT] start_erosion_process called")

    def stop_erosion_process(self):
        print("[ROBOT] stop_erosion_process called")