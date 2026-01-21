from unittest.mock import Mock

from src.application.joint_trajectory_executor import JointTrajectoryExecutor


def test_joint_trajectory_executor_calls_controller():
    controller = Mock()
    trajectory_service = Mock()
    trajectory_service.get_points.return_value = [
        [0, 0, 0, 0, 0, 0],
        [10, 20, 30, 40, 50, 60],
    ]

    executor = JointTrajectoryExecutor(
        controller=controller,
        trajectory_service=trajectory_service,
        delay_sec=0,
    )

    executor.execute()

    controller.set_joints.assert_any_call([0, 0, 0, 0, 0, 0])
    controller.set_joints.assert_any_call([10, 20, 30, 40, 50, 60])
    assert controller.set_joints.call_count == 2
