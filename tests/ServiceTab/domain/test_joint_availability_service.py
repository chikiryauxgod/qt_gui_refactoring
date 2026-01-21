from src.domain.joint_availability_service import JointAvailabilityService


def test_joints_valid():
    service = JointAvailabilityService()
    assert service.is_available([0, 10, -20, 30, 40, 50]) is True


def test_joint_out_of_range():
    service = JointAvailabilityService()
    assert service.is_available([0, 0, 0, 0, 0, 200]) is False
