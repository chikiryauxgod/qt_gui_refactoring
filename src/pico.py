class Pico:
    def __init__(self, *args, **kwargs):
        pass

    def pump_in(self, state: int):
        print(f"[PICO] pump_in = {state}")

    def pump_out(self, state: int):
        print(f"[PICO] pump_out = {state}")
