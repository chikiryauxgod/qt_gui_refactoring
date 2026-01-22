import pytest
from unittest.mock import MagicMock
from PySide6.QtCore import Qt

@pytest.fixture
def mainwindow_mocked(qtbot):
    from src.ui.main_window import MainWindow

    hardware_mock = MagicMock()
    state_mock = MagicMock()
    state_mock.current_x = 1.0
    state_mock.current_y = 2.0
    state_mock.current_z = 3.0
    state_mock.current_joints = [10, 20, 30, 40, 50, 60]
    state_mock.updating = False

    process_manager_mock = MagicMock()
    ui_manager_mock = MagicMock()

    window = MainWindow()
    qtbot.addWidget(window)

    window.hardware = hardware_mock
    window.state = state_mock
    window.process_manager = process_manager_mock
    window.ui_manager = ui_manager_mock

    if hasattr(window, 'erosion_tab'):
        window.erosion_tab.video_label = MagicMock()
    if hasattr(window, 'service_tab'):
        window.service_tab.update_status = MagicMock()
        window.service_tab.stop_continuous_move = MagicMock()

    return window, hardware_mock, state_mock


def test_mainwindow_methods(mainwindow_mocked, qtbot):
    window, hardware, state = mainwindow_mocked

    window.set_coord_pos(10.0, 20.0, 30.0)
    hardware.set_coord_pos.assert_called_once_with(10.0, 20.0, 30.0)
    state.sync_from_robot.assert_called_once()
    window.ui_manager.sync_coordinates_to_tabs.assert_called_once()

    joints = [1, 2, 3, 4, 5, 6]
    window.set_joint_pos(joints)
    hardware.set_joint_pos.assert_called_once_with(joints)
    assert state.current_joints == joints[:6]
    window.ui_manager.sync_joints_to_tabs.assert_called_once()

    window.set_erosion(True)
    hardware.set_erosion.assert_called_once_with(True)
    window.service_tab.update_status.assert_called()

    window.set_water(True)
    hardware.set_water.assert_called_once_with(True)
    window.service_tab.update_status.assert_called()

    window.pump_control_one()
    hardware.pump_control_one.assert_called_once()
    window.service_tab.update_status.assert_called()

    window.pump_control_two()
    hardware.pump_control_two.assert_called_once()
    window.service_tab.update_status.assert_called()

    window.emergency_stop()
    hardware.emergency_stop.assert_called_once()
    window.service_tab.stop_continuous_move.assert_called_once()