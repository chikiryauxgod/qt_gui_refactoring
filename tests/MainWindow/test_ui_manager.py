import pytest
from unittest.mock import MagicMock
from src.qt_interface import UIManager

@pytest.fixture
def ui_manager():
    mock_xyz_controls = {}
    for axis in ['X', 'Y', 'Z']:
        mock_display = MagicMock()
        mock_input = MagicMock()
        mock_xyz_controls[axis] = {'display': mock_display, 'input': mock_input}

    mock_joints_controls = {}
    for i in range(6):
        mock_display = MagicMock()
        mock_input = MagicMock()
        mock_joints_controls[f'J{i}'] = {'display': mock_display, 'input': mock_input}

    mock_service = MagicMock()
    mock_service.xyz_controls = mock_xyz_controls
    mock_service.joints_controls = mock_joints_controls
    mock_service.update_xyz_plot = MagicMock()
    mock_service.update_joints_plot = MagicMock()

    mock_erosion = MagicMock()
    mock_erosion.x_control = MagicMock()
    mock_erosion.y_control = MagicMock()
    mock_erosion.z_control = MagicMock()
    for ctrl in [mock_erosion.x_control, mock_erosion.y_control, mock_erosion.z_control]:
        ctrl.value_label = MagicMock()

    mock_state = MagicMock()
    mock_state.current_x = 1.0
    mock_state.current_y = 2.0
    mock_state.current_z = 3.0
    mock_state.current_joints = [10, 20, 30, 40, 50, 60]
    
    um = UIManager(mock_erosion, mock_service, mock_state)
    yield um

def test_ui_manager_sync_coordinates(ui_manager):
    ui_manager.sync_coordinates_to_tabs()
    ui_manager.service_tab.xyz_controls['X']['display'].setText.assert_called_with("1.00")
    ui_manager.service_tab.xyz_controls['X']['input'].setValue.assert_called_with(1.0)
    ui_manager.service_tab.update_xyz_plot.assert_called()
    ui_manager.erosion_tab.x_control.value_label.setText.assert_called_with("1.0 мм")

def test_ui_manager_sync_joints(ui_manager):
    ui_manager.sync_joints_to_tabs()
    ui_manager.service_tab.joints_controls['J0']['display'].setText.assert_called_with("10.00")
    ui_manager.service_tab.joints_controls['J0']['input'].setValue.assert_called_with(10)
    ui_manager.service_tab.update_joints_plot.assert_called()
