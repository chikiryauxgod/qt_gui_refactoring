import pytest
from src.services.joint_trajectory_service import JointTrajectoryService


def test_set_initial_joint_point():
    service = JointTrajectoryService()

    service.set_initial_point((0.0, 1.0, 2.0))

    assert service.get_points() == [(0.0, 1.0, 2.0)]


def test_add_joint_point():
    service = JointTrajectoryService()
    service.set_initial_point((0.0, 0.0))

    service.add_point((1.0, 2.0))

    assert service.get_points() == [
        (0.0, 0.0),
        (1.0, 2.0),
    ]


def test_remove_joint_point():
    service = JointTrajectoryService()
    service.set_initial_point((0.0,))
    service.add_point((1.0,))

    service.remove_point(0)

    assert service.get_points() == [(1.0,)]


def test_clear_joint_trajectory():
    service = JointTrajectoryService()
    service.set_initial_point((0.0, 1.0))

    service.clear()

    assert service.is_empty()


def test_remove_joint_point_out_of_range():
    service = JointTrajectoryService()

    with pytest.raises(IndexError):
        service.remove_point(0)
