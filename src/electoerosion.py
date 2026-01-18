class Electroerosion:
    def __init__(self, filename=None, speed=10, mode="test"):
        self.filename = filename
        self.speed = speed
        self.mode = mode
        self.robot = None
        self.erosion = None
        print(f"[ELECTROEROSION - stub] filename={filename}, speed={speed}, mode={mode}")

    def start(self):
        print("[ELECTROEROSION - stub] start() called")

    def stop(self):
        print("[ELECTROEROSION - stub] stop() called")