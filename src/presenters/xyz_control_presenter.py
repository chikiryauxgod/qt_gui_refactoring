from src.ports.robot_controller_port import RobotControllerPort


class XYZControlPresenter:
    """ Управляет XYZ-движением робота. """

    def __init__(self, controller: RobotControllerPort):
        self._controller = controller

    def move(self, dx: float, dy: float, dz: float) -> None:
        self._controller.move_xyz(dx, dy, dz)

    def set_position(self, x: float, y: float, z: float) -> None:
        self._controller.set_coord_pos(x, y, z)

    def return_to_zero(self) -> None:
        self._controller.set_coord_pos(
            self._controller.X0,
            self._controller.Y0,
            self._controller.Z0
        )

