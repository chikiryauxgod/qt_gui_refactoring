from unittest.mock import Mock
from src.visualization.xyz_kinematics_plotter import XYZKinematicsPlotter

def test_plot_calls_canvas_draw():
    ax = Mock()
    canvas = Mock()
    robot_chain = Mock()

    robot_chain.inverse_kinematics.return_value = [0, 0, 0]
    robot_chain.plot.return_value = None

    plotter = XYZKinematicsPlotter(
        ax=ax,
        canvas=canvas,
        robot_chain=robot_chain,
        ikpy_available=True,
    )

    plotter.plot(100, 200, 300)

    canvas.draw.assert_called_once()

def test_plot_with_kinematics_calls_inverse_kinematics():
    ax = Mock()
    canvas = Mock()
    robot_chain = Mock()

    robot_chain.inverse_kinematics.return_value = [1, 2, 3]

    plotter = XYZKinematicsPlotter(
        ax=ax,
        canvas=canvas,
        robot_chain=robot_chain,
        ikpy_available=True,
    )

    plotter.plot(100, 200, 300)

    robot_chain.inverse_kinematics.assert_called_once()
    robot_chain.plot.assert_called_once()
    
def test_plot_without_kinematics_uses_scatter_only():
    ax = Mock()
    canvas = Mock()

    plotter = XYZKinematicsPlotter(
        ax=ax,
        canvas=canvas,
        robot_chain=None,
        ikpy_available=False,
    )

    plotter.plot(100, 200, 300)

    ax.scatter.assert_called_once()
    canvas.draw.assert_called_once()

def test_plot_kinematics_exception_falls_back_to_point():
    ax = Mock()
    canvas = Mock()
    robot_chain = Mock()

    robot_chain.inverse_kinematics.side_effect = Exception("IK error")

    plotter = XYZKinematicsPlotter(
        ax=ax,
        canvas=canvas,
        robot_chain=robot_chain,
        ikpy_available=True,
    )

    plotter.plot(100, 200, 300)

    ax.scatter.assert_called_once()
    canvas.draw.assert_called_once()

