import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtCore import QThread, Signal
from src.qt_interface import ProcessManager

class MockErosionWorker(QThread):
    progress_updated = Signal(float)
    time_updated = Signal(str)
    finished = Signal()
    paused = Signal()
    resumed = Signal()
    def __init__(self, *args):
        super().__init__()
        self.start = MagicMock()
        self.stop = MagicMock()
        self.pause = MagicMock()
        self.resume = MagicMock()
        self.wait = MagicMock(return_value=True)
        self.isRunning = MagicMock(return_value=True)
        self.terminate = MagicMock()

@pytest.fixture
def process_manager():
    mock_hardware = MagicMock()
    mock_erosion_tab = MagicMock()
    mock_state = MagicMock()
    pm = ProcessManager(mock_hardware, mock_erosion_tab, mock_state)
    yield pm

@patch('src.qt_interface.ErosionController')
@patch('src.qt_interface.GCodeProcessor')
@patch('src.qt_interface.ErosionWorker', return_value=MockErosionWorker())
def test_process_manager_start_erosion(mock_worker_class, mock_gcode, mock_controller, process_manager):
    process_manager.start_erosion_process([], 1, 2, 3, 4, 5, 'file', 'mode')
    mock_worker_class.return_value.start.assert_called()
    process_manager.erosion_tab.set_erosion_worker.assert_called()
    process_manager.erosion_tab.update_process_status.assert_called_with("ПРОЦЕСС ВЫПОЛНЯЕТСЯ", "#27ae60")

def test_process_manager_stop_erosion(process_manager):
    process_manager.erosion_worker = MockErosionWorker()
    process_manager.stop_erosion_process()
    process_manager.erosion_worker.stop.assert_called()
    process_manager.erosion_worker.wait.assert_called_with(2000)
    process_manager.erosion_tab.set_stopped_ui_state.assert_called()
    process_manager.erosion_tab.update_process_status.assert_called_with("ПРОЦЕСС ОСТАНОВЛЕН", "#e74c3c")

def test_process_manager_signals(process_manager):
    process_manager.erosion_finished()
    process_manager.erosion_tab.update_process_status.assert_called_with("ПРОЦЕСС ЗАВЕРШЕН", "#3498db")
    process_manager.erosion_paused()
    process_manager.erosion_tab.update_process_status.assert_called_with("ПРОЦЕСС НА ПАУЗЕ", "#f39c12")
    process_manager.erosion_resumed()
    process_manager.erosion_tab.update_process_status.assert_called_with("ПРОЦЕСС ВЫПОЛНЯЕТСЯ", "#27ae60")