from src.visualization.canvas_redraw import request_canvas_redraw


class JointsTrajectoryPlotter:
    def __init__(self, ax, canvas):
        self._ax = ax
        self._canvas = canvas

    def plot(self, trajectories: list[list[float]]) -> None:
        self._ax.clear()

        if not trajectories:
            request_canvas_redraw(self._canvas)
            return

        steps = range(len(trajectories))

        for joint_index, joint_values in enumerate(zip(*trajectories)):
            self._ax.plot(
                steps,
                joint_values,
                label=f"J{joint_index}"
            )

        self._ax.set_xlabel("Шаг траектории")
        self._ax.set_ylabel("Угол сустава (°)")
        self._ax.set_title("Траектория суставов")
        self._ax.legend()
        self._ax.grid(True)

        request_canvas_redraw(self._canvas)
