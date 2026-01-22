class Pico:
    def __init__(self, *args, **kwargs):
        self.erosion_state = 0
        self.pump_in_state = 0
        self.pump_out_state = 0

    def erosion(self, state: int):
        self.erosion_state = state
        print(f"[PICO] erosion = {state}")

    def pump_in(self, state: int):
        self.pump_in_state = state
        print(f"[PICO] pump_in = {state}")

    def pump_out(self, state: int):
        self.pump_out_state = state
        print(f"[PICO] pump_out = {state}")
