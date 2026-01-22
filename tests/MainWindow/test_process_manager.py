import pytest
from unittest.mock import MagicMock, patch
from src.application.process_manager import ProcessManager

from unittest.mock import MagicMock

class MockErosionWorker:
    def __init__(self, *args, **kwargs):
        self.start = MagicMock()
        self.stop = MagicMock()
        self.pause = MagicMock()
        self.resume = MagicMock()
        self.wait = MagicMock(return_value=True)
        self.isRunning = MagicMock(return_value=True)
        self.terminate = MagicMock()

        self.progress_updated = MagicMock()
        self.time_updated = MagicMock()
        self.finished = MagicMock()
        self.paused = MagicMock()
        self.resumed = MagicMock()

@pytest.fixture
def process_manager():
    mock_hardware = MagicMock()
    mock_erosion_tab = MagicMock()
    mock_state = MagicMock()
    pm = ProcessManager(mock_hardware, mock_erosion_tab, mock_state)
    yield pm

@patch('src.application.process_manager.ErosionWorker')
@patch('src.erosion_worker.erosion_worker.GCodeProcessor')
@patch('src.erosion_worker.erosion_worker.ErosionController')
def test_process_manager_start_erosion(mock_controller, mock_gcode, mock_worker_class, process_manager):

    mock_worker_instance = MockErosionWorker()
    mock_worker_class.return_value = mock_worker_instance

    process_manager.start_erosion_process([], 1, 2, 3, 4, 5, 'file', 'mode')

    mock_worker_instance.start.assert_called()

    process_manager.erosion_tab.set_erosion_worker.assert_called_with(mock_worker_instance)

    process_manager.erosion_tab.update_process_status.assert_called_with("ПРОЦЕСС ВЫПОЛНЯЕТСЯ", "#27ae60")

def test_process_manager_stop_erosion(process_manager):
    mock_worker_instance = MockErosionWorker()
    process_manager.erosion_worker = mock_worker_instance

    process_manager.stop_erosion_process()

    mock_worker_instance.stop.assert_called()
    mock_worker_instance.wait.assert_called_with(2000)
    process_manager.erosion_tab.set_stopped_ui_state.assert_called()
    process_manager.erosion_tab.update_process_status.assert_called_with("ПРОЦЕСС ОСТАНОВЛЕН", "#e74c3c")

def test_process_manager_signals(process_manager):
    process_manager.erosion_finished()
    process_manager.erosion_tab.update_process_status.assert_called_with("ПРОЦЕСС ЗАВЕРШЕН", "#3498db")

    process_manager.erosion_paused()
    process_manager.erosion_tab.update_process_status.assert_called_with("ПРОЦЕСС НА ПАУЗЕ", "#f39c12")

    process_manager.erosion_resumed()
    process_manager.erosion_tab.update_process_status.assert_called_with("ПРОЦЕСС ВЫПОЛНЯЕТСЯ", "#27ae60")
