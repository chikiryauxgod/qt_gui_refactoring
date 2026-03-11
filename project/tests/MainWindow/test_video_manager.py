import pytest
from unittest.mock import MagicMock, patch
from src.ui.video_manager import VideoManager

class MockSignal:
    def __init__(self):
        self.connect = MagicMock()

class MockVideoStreamThread:
    def __init__(self):
        self.start = MagicMock()
        self.stop = MagicMock()
        self.new_frame = MockSignal()

@pytest.fixture
def video_manager():
    with patch('src.ui.video_manager.VideoStreamThread', return_value=MockVideoStreamThread()):
        vm = VideoManager()
        yield vm

def test_video_manager_start(video_manager):
    video_manager.start()
    assert video_manager.video_thread is not None
    video_manager.video_thread.new_frame.connect.assert_called_with(video_manager.update_frame)
    video_manager.video_thread.start.assert_called()

def test_video_manager_stop(video_manager):
    video_manager.stop()
    video_manager.video_thread.stop.assert_called()
