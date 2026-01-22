import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtCore import QThread, Signal
from src.qt_interface import MainWindow

X0, Y0, Z0 = 0.0, 0.0, 0.0

@pytest.fixture
def mocked_dependencies():
    with patch("src.qt_interface.HardwareController") as MockHardware, \
         patch("src.qt_interface.StateManager") as MockState, \
         patch("src.qt_interface.VideoManager") as MockVideo, \
         patch("src.qt_interface.ProcessManager") as MockProcess, \
         patch("src.qt_interface.UIManager") as MockUI:

        mock_hardware = MockHardware.return_value
        mock_hardware.set_coord_pos = MagicMock()
        mock_hardware.set_joint_pos = MagicMock()
        mock_hardware.set_erosion = MagicMock()
        mock_hardware.set_water = MagicMock()
        mock_hardware.pump_control_one = MagicMock()
        mock_hardware.pump_control_two = MagicMock()
        mock_hardware.emergency_stop = MagicMock()
        mock_hardware.set_speed = MagicMock()
        
        mock_state = MockState.return_value
        mock_state.updating = False
        mock_state.current_x = X0
        mock_state.current_y = Y0
        mock_state.current_z = Z0
        mock_state.current_joints = [0] * 6
        mock_state.sync_from_robot = MagicMock()
        
        mock_video = MockVideo.return_value
        mock_video.start = MagicMock()
        mock_video.stop = MagicMock()
        mock_video.video_label = None
        
        mock_process = MockProcess.return_value
        mock_process.start_erosion_process = MagicMock()
        mock_process.stop_erosion_process = MagicMock()
        
        mock_ui = MockUI.return_value
        mock_ui.sync_coordinates_to_tabs = MagicMock()
        mock_ui.sync_joints_to_tabs = MagicMock()
        
        yield {
            "HardwareController": mock_hardware,
            "StateManager": mock_state,
            "VideoManager": mock_video,
            "ProcessManager": mock_process,
            "UIManager": mock_ui
        }

def test_mainwindow_creation(qtbot, mocked_dependencies):
    """Тест создания MainWindow и вызова основных методов"""
    window = MainWindow()
    qtbot.addWidget(window) 
    assert hasattr(window, "hardware")
    assert hasattr(window, "state")
    assert hasattr(window, "video_manager")
    assert hasattr(window, "process_manager")
    assert hasattr(window, "ui_manager")
    assert hasattr(window, "erosion_tab")
    assert hasattr(window, "service_tab")

    window.set_coord_pos(10, 20, 30)
    window.hardware.set_coord_pos.assert_called_once_with(10, 20, 30)
    window.state.sync_from_robot.assert_called_once()
    
    window.set_joint_pos([1, 2, 3, 4, 5, 6])
    window.hardware.set_joint_pos.assert_called_once_with([1, 2, 3, 4, 5, 6])

    window.set_erosion(True)
    window.hardware.set_erosion.assert_called_once_with(True)
    
    window.set_water(True)
    window.hardware.set_water.assert_called_once_with(True)

    window.pump_control_one()
    window.hardware.pump_control_one.assert_called_once()
    
    window.pump_control_two()
    window.hardware.pump_control_two.assert_called_once()

    window.emergency_stop()
    window.hardware.emergency_stop.assert_called_once()

    window.safe_finish()
    window.process_manager.stop_erosion_process.assert_called()
    window.hardware.set_erosion.assert_called()
    window.hardware.set_water.assert_called()

    window.start_erosion_process([], 1, 1, 1, 1, 1, "file.gcode", "test")
    window.process_manager.start_erosion_process.assert_called_once()
    
    window.stop_erosion_process()
    window.process_manager.stop_erosion_process.assert_called()
