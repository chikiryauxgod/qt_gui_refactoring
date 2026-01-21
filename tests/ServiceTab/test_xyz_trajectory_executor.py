from unittest.mock import Mock

from src.application.xyz_trajectory_executor import XYZTrajectoryExecutor


def test_xyz_trajectory_execution_calls_controller_in_order():
    controller = Mock()
    trajectory_service = Mock()
    trajectory_service.get_points.return_value = [
        (1, 2, 3),
        (4, 5, 6),
    ]

    executor = XYZTrajectoryExecutor(
        controller=controller,
        trajectory_service=trajectory_service,
        delay_sec=0,
    )

    executor.execute()

    controller.set_coord_pos.assert_any_call(1, 2, 3)
    controller.set_coord_pos.assert_any_call(4, 5, 6)
    assert controller.set_coord_pos.call_count == 2
