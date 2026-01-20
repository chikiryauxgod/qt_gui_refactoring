

import numpy as np
import pytest
import sys, types


sys.modules["electoerosion"] = types.ModuleType("electoerosion")
sys.modules["pico"] = types.ModuleType("pico")
sys.modules["robot"] = types.ModuleType("robot")

import src.qt_interface as qi
from src.qt_interface import VideoStreamThread


class FakeCapture:
    """
    Фейковая камера:
    - 1 раз отдаёт кадр
    - затем "закрывается" и возвращает ret=False
    """
    def __init__(self, idx):
        self._released = False
        self._read_count = 0

    def isOpened(self):
        return not self._released

    def set(self, *_):
        return True

    def read(self):
        self._read_count += 1
        if self._read_count == 1:
            frame = np.zeros((10, 10, 3), dtype=np.uint8)
            return True, frame

        # после первого кадра считаем, что камера закончилась/закрылась
        self._released = True
        return False, None

    def release(self):
        self._released = True


@pytest.fixture
def patch_cv2(monkeypatch):
    """Патчим cv2 внутри src.qt_interface, чтобы не трогать реальную камеру."""
    def fake_videocapture(idx):
        return FakeCapture(idx)

    def fake_cvtcolor(frame, code):
        return frame  # нам не важно, что именно делает конвертация

    monkeypatch.setattr(qi.cv2, "VideoCapture", fake_videocapture)
    monkeypatch.setattr(qi.cv2, "cvtColor", fake_cvtcolor)


def test_run_finishes_when_capture_ends(patch_cv2):
    """
    Тест НЕ проверяет сигнал new_frame.
    Он проверяет главное: run() не уходит в вечный цикл, если камера "закончилась".
    """
    t = VideoStreamThread(camera_idx=0, width=640, height=480, latency=1)

    # на всякий случай: ограничим время выполнения теста логикой в FakeCapture
    t.running = True
    t.run()

    # После выполнения run() камера должна быть "закрыта"
    assert t.cap.isOpened() is False