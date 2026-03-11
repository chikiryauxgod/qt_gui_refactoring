from src.domain.xyz_availability_service import XYZAvailabilityService


def test_xyz_valid_point():
    service = XYZAvailabilityService()
    assert service.is_available(0, 0, 100) is True


def test_xyz_out_of_range_x():
    service = XYZAvailabilityService()
    assert service.is_available(1000, 0, 100) is False


def test_xyz_negative_z():
    service = XYZAvailabilityService()
    assert service.is_available(0, 0, -10) is False
