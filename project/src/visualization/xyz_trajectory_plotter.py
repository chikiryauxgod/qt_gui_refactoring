import numpy as np
from src.visualization.canvas_redraw import request_canvas_redraw


class XYZTrajectoryPlotter:
    def __init__(self, ax, canvas):
        self._ax = ax
        self._canvas = canvas

    def plot(self, points: list[tuple[float, float, float]]) -> None:
        self._ax.clear()

        if not points:
            request_canvas_redraw(self._canvas)
            return

        pts = np.array(points)
        self._ax.plot(pts[:, 0], pts[:, 1], pts[:, 2])
        self._ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2])

        self._ax.set_title("Траектория XYZ")
        request_canvas_redraw(self._canvas)
