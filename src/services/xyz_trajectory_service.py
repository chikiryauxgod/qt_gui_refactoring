from typing import List, Tuple


PointXYZ = Tuple[float, float, float]


class XYZTrajectoryService:
    """ Отвечает за хранение и управление XYZ-траекторией. """

    def __init__(self) -> None:
        self._points: List[PointXYZ] = []

    def set_initial_point(self, x: float, y: float, z: float) -> None:
        self._points = [(x, y, z)]

    def add_point(self, x: float, y: float, z: float) -> None:
        self._points.append((x, y, z))

    def remove_point(self, index: int) -> None:
        if index < 0 or index >= len(self._points):
            raise IndexError("Trajectory point index out of range")
        self._points.pop(index)

    def clear(self) -> None:
        self._points.clear()

    def get_points(self) -> List[PointXYZ]:
        return list(self._points)

    def is_empty(self) -> bool:
        return not self._points
