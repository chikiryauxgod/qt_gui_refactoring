from unittest.mock import Mock
from src.presenters.xyz_control_presenter import XYZControlPresenter


def test_move_xyz_calls_controller():
    controller = Mock()
    presenter = XYZControlPresenter(controller)

    presenter.move(1.0, 2.0, 3.0)

    controller.move_xyz.assert_called_once_with(1.0, 2.0, 3.0)


def test_set_position_calls_controller():
    controller = Mock()
    presenter = XYZControlPresenter(controller)

    presenter.set_position(10.0, 20.0, 30.0)

    controller.set_coord_pos.assert_called_once_with(10.0, 20.0, 30.0)


def test_return_to_zero_calls_controller():
    controller = Mock()
    presenter = XYZControlPresenter(controller)

    presenter.return_to_zero()

    controller.return_to_zero_xyz.assert_called_once()
