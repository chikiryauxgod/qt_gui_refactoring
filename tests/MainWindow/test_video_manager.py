import pytest
from unittest.mock import MagicMock, patch
from src.qt_interface import VideoManager

# Мок для сигнала
class MockSignal:
    def __init__(self):
        self.connect = MagicMock()

# Мок потока
class MockVideoStreamThread:
    def __init__(self):
        self.start = MagicMock()
        self.stop = MagicMock()
        self.new_frame = MockSignal()

# Фикстура VideoManager с патчем
@pytest.fixture
def video_manager():
    with patch('src.qt_interface.VideoStreamThread', return_value=MockVideoStreamThread()):
        vm = VideoManager()
        yield vm

# Тест запуска видео
def test_video_manager_start(video_manager):
    video_manager.start()

    # Проверяем, что поток создан
    assert video_manager.video_thread is not None
    # Проверяем, что connect сигнала вызван
    assert video_manager.video_thread.new_frame.connect.called
    # Проверяем, что поток стартанул
    assert video_manager.video_thread.start.called

# Тест остановки видео
def test_video_manager_stop(video_manager):
    video_manager.stop()
    assert video_manager.video_thread.stop.called
