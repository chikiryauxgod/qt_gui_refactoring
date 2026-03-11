class XYZKinematicsPlotter:
    def __init__(
        self,
        ax,
        canvas,
        robot_chain=None,
        ikpy_available: bool = False,
    ):
        self._ax = ax
        self._canvas = canvas
        self._robot_chain = robot_chain
        self._ikpy_available = ikpy_available

    def plot(self, x: float, y: float, z: float) -> None:
        self._ax.clear()

        if self._robot_chain and self._ikpy_available:
            self._plot_with_kinematics(x, y, z)
        else:
            self._plot_point(x, y, z)

        self._configure_axes(x, y, z)
        self._canvas.draw()

    def _plot_with_kinematics(self, x, y, z):
        try:
            target = [x / 1000, y / 1000, z / 1000]
            joint_angles = self._robot_chain.inverse_kinematics(
                target_position=target,
                target_orientation=[0, 0, 0],
                orientation_mode="all",
            )
            self._robot_chain.plot(joint_angles, self._ax, target=target)
            self._ax.scatter(*target, c="red", s=100)
        except Exception:
            self._plot_point(x, y, z)

    def _plot_point(self, x, y, z):
        self._ax.scatter(
            [x / 1000],
            [y / 1000],
            [z / 1000],
            c="red",
            s=100,
        )

    def _configure_axes(self, x, y, z):
        padding = 0.5
        self._ax.set_title("Кинематическая цепочка робота")
        self._ax.set_xlabel("X (м)")
        self._ax.set_ylabel("Y (м)")
        self._ax.set_zlabel("Z (м)")

        self._ax.set_xlim([x / 1000 - padding, x / 1000 + padding])
        self._ax.set_ylim([y / 1000 - padding, y / 1000 + padding])
        self._ax.set_zlim([max(0, z / 1000 - padding), z / 1000 + padding])
