import pytest
from src.services.xyz_trajectory_service import XYZTrajectoryService


def test_set_initial_point():
    service = XYZTrajectoryService()

    service.set_initial_point(1.0, 2.0, 3.0)

    assert service.get_points() == [(1.0, 2.0, 3.0)]


def test_add_point():
    service = XYZTrajectoryService()
    service.set_initial_point(0.0, 0.0, 0.0)

    service.add_point(1.0, 2.0, 3.0)
    service.add_point(4.0, 5.0, 6.0)

    assert service.get_points() == [
        (0.0, 0.0, 0.0),
        (1.0, 2.0, 3.0),
        (4.0, 5.0, 6.0),
    ]


def test_remove_point():
    service = XYZTrajectoryService()
    service.set_initial_point(0.0, 0.0, 0.0)
    service.add_point(1.0, 1.0, 1.0)

    service.remove_point(0)

    assert service.get_points() == [(1.0, 1.0, 1.0)]


def test_remove_point_out_of_range():
    service = XYZTrajectoryService()

    with pytest.raises(IndexError):
        service.remove_point(0)


def test_clear():
    service = XYZTrajectoryService()
    service.set_initial_point(0.0, 0.0, 0.0)
    service.add_point(1.0, 1.0, 1.0)

    service.clear()

    assert service.is_empty()
