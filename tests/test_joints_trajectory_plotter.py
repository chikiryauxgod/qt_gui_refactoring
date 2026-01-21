from unittest.mock import Mock
from src.visualization.joints_trajectory_plotter import JointsTrajectoryPlotter


def test_joints_trajectory_plot_calls_draw():
    ax = Mock()
    canvas = Mock()

    plotter = JointsTrajectoryPlotter(ax, canvas)

    trajectories = [
        [0, 0, 0, 0, 0, 0],
        [10, 20, 30, 40, 50, 60],
    ]

    plotter.plot(trajectories)

    canvas.draw.assert_called_once()
