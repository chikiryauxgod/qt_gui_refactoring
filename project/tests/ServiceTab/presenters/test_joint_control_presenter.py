from unittest.mock import Mock
from src.presenters.joint_control_presenter import JointControlPresenter


def test_set_position_calls_controller():
    controller = Mock()
    presenter = JointControlPresenter(controller)

    joints = [1, 2, 3, 4, 5, 6]
    presenter.set_position(joints)

    controller.set_joint_pos.assert_called_once_with(joints)
