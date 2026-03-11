from unittest.mock import Mock
from src.visualization.xyz_trajectory_plotter import XYZTrajectoryPlotter


def test_plot_calls_canvas_draw():
    ax = Mock()
    canvas = Mock()

    plotter = XYZTrajectoryPlotter(ax, canvas)
    plotter.plot([(0, 0, 0), (1, 1, 1)])

    canvas.draw.assert_called_once()

def test_xyz_trajectory_plot_empty_points():
    ax = Mock()
    canvas = Mock()

    plotter = XYZTrajectoryPlotter(ax, canvas)
    plotter.plot([])

    canvas.draw.assert_called_once()
