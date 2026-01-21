class JointsTrajectoryPlotter:
    def __init__(self, ax, canvas):
        self._ax = ax
        self._canvas = canvas

    def plot(self, trajectories: list[list[float]]) -> None:
        self._ax.clear()

        if not trajectories:
            self._canvas.draw()
            return

        for joint_index, joint_values in enumerate(zip(*trajectories)):
            self._ax.plot(joint_values, label=f"J{joint_index}")

        self._ax.legend()
        self._ax.set_title("Траектория суставов")
        self._canvas.draw()
