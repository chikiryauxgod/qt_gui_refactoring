import pytest
from unittest.mock import MagicMock, patch
from src.services.hardware_controller import HardwareController

class MockRobot:
    def __init__(self):
        self.current_x = 0
        self.current_y = 0
        self.current_z = 0
        self.set_coord_pos = MagicMock()
        self.set_joint_pos = MagicMock()
        self.set_speed = MagicMock()
        self.emergency_stop = MagicMock()

class MockPico:
    def __init__(self):
        self.erosion = MagicMock()
        self.pump_in = MagicMock()
        self.pump_out = MagicMock()

class MockElectroerosion:
    def __init__(self):
        self.set_coord_pos = MagicMock()

@pytest.fixture
def hardware_controller():
    with patch('src.electoerosion.Electroerosion', return_value=MockElectroerosion()) as mock_erode:
        hc = HardwareController()
        hc.robot = MockRobot()
        hc.pico = MockPico()
        hc.erode = mock_erode.return_value
        yield hc

def test_hardware_set_coord_pos(hardware_controller):
    hardware_controller.erode = MagicMock()
    hardware_controller.robot = MagicMock()
    
    hardware_controller.set_coord_pos(1.0, 2.0, 3.0)

    hardware_controller.erode.set_coord_pos.assert_called_once_with(1.0, 2.0, 3.0)

    assert hardware_controller.robot.current_x == 1.0
    assert hardware_controller.robot.current_y == 2.0
    assert hardware_controller.robot.current_z == 3.0


def test_hardware_set_joint_pos(hardware_controller):
    joints = [10, 20, 30, 40, 50, 60]
    hardware_controller.set_joint_pos(joints)
    hardware_controller.robot.set_joint_pos.assert_called_with(joints)

def test_hardware_set_erosion(hardware_controller):
    hardware_controller.set_erosion(True)
    hardware_controller.pico.erosion.assert_called_with(1)
    hardware_controller.set_erosion(False)
    hardware_controller.pico.erosion.assert_called_with(0)

def test_hardware_set_water(hardware_controller):
    hardware_controller.set_water(True)
    hardware_controller.pico.pump_in.assert_called_with(1)
    hardware_controller.pico.pump_out.assert_called_with(1)

def test_hardware_pump_control_one(hardware_controller):
    hardware_controller.pump_control_one()
    assert hardware_controller.state_pump_one is True
    hardware_controller.pico.pump_in.assert_called_with(1)

def test_hardware_set_speed(hardware_controller):
    hardware_controller.set_speed(50)
    hardware_controller.robot.set_speed.assert_called_with(50)

def test_hardware_emergency_stop(hardware_controller):
    hardware_controller.emergency_stop()
    hardware_controller.robot.emergency_stop.assert_called()
