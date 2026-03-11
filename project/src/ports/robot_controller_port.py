from typing import Protocol


class RobotControllerPort(Protocol):
    X0: float
    Y0: float
    Z0: float

    def move_xyz(self, dx: float, dy: float, dz: float) -> None: ...
    def set_coord_pos(self, x: float, y: float, z: float) -> None: ...
