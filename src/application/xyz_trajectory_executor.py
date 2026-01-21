from typing import Iterable, Tuple


class XYZTrajectoryExecutor:
    def __init__(self, controller, trajectory_service, delay_sec: float = 1.0):
        self._controller = controller
        self._trajectory_service = trajectory_service
        self._delay_sec = delay_sec

    def execute(self) -> None:
        for x, y, z in self._trajectory_service.get_points():
            self._controller.set_coord_pos(x, y, z)
            self._sleep()

    def _sleep(self) -> None:
        import time
        time.sleep(self._delay_sec)


