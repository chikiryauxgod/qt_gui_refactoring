from typing import List, Tuple


JointPoint = Tuple[float, ...]


class JointTrajectoryService:
    """ Отвечает за хранение и управление joint-траекторией. """

    def __init__(self) -> None:
        self._points: List[JointPoint] = []

    def set_initial_point(self, joints: JointPoint) -> None:
        self._points = [tuple(joints)]

    def add_point(self, joints: JointPoint) -> None:
        self._points.append(tuple(joints))

    def remove_point(self, index: int) -> None:
        if index < 0 or index >= len(self._points):
            raise IndexError("Joint trajectory index out of range")
        self._points.pop(index)

    def clear(self) -> None:
        self._points.clear()

    def get_points(self) -> List[JointPoint]:
        return list(self._points)

    def is_empty(self) -> bool:
        return not self._points
