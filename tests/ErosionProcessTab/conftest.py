import pytest
from unittest.mock import Mock
import queue


@pytest.fixture
def fake_view():
    view = Mock()
    view.show_error = Mock()
    view.set_gcode_info = Mock()
    view.plot_gcode = Mock()
    view.append_log = Mock()
    view.set_started_ui_state = Mock()
    view.set_stopped_ui_state = Mock()
    view.set_paused_ui_state = Mock()
    view.set_running_ui_state = Mock()
    return view


@pytest.fixture
def fake_controller():
    controller = Mock()
    controller.start_erosion_process = Mock()
    controller.stop_erosion_process = Mock()
    controller.set_coord_pos = Mock()
    controller.X0 = 0
    controller.Y0 = 0
    controller.Z0 = 0
    return controller


@pytest.fixture
def q_ref():
    return queue.Queue()