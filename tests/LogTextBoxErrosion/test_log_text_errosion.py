import queue
import time

import pytest
from PySide6.QtCore import QCoreApplication, QEventLoop, QTimer

from src.LogText.LogTextBoxErrosion import QueueMessageSource, LogTextBoxErrosion


@pytest.fixture(scope="session", autouse=True)
def qapp():
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    return app


def wait_until(predicate, timeout_ms: int = 1000, step_ms: int = 10) -> bool:
    loop = QEventLoop()
    ok = {"value": False}

    def tick():
        if predicate():
            ok["value"] = True
            loop.quit()

    timer = QTimer()
    timer.setInterval(step_ms)
    timer.timeout.connect(tick)
    timer.start()

    QTimer.singleShot(timeout_ms, loop.quit)
    loop.exec()

    timer.stop()
    return ok["value"]


def test_emits_message_from_queue(qapp):
    q = queue.Queue()
    source = QueueMessageSource(q)
    thread = LogTextBoxErrosion(source, latency_ms=5)

    received = []
    thread.new_message.connect(received.append)

    thread.start()
    try:
        q.put("hello")

        assert wait_until(lambda: len(received) >= 1, timeout_ms=1000), "Сигнал не пришёл вовремя"
        assert received[0] == "hello"
    finally:
        thread.stop()


def test_no_message_when_queue_empty(qapp):
    q = queue.Queue()
    source = QueueMessageSource(q)
    thread = LogTextBoxErrosion(source, latency_ms=5)

    received = []
    thread.new_message.connect(received.append)

    thread.start()
    try:
        time.sleep(0.05)
        assert received == []
    finally:
        thread.stop()


def test_multiple_messages_order(qapp):
    q = queue.Queue()
    source = QueueMessageSource(q)
    thread = LogTextBoxErrosion(source, latency_ms=1)

    received = []
    thread.new_message.connect(received.append)

    thread.start()
    try:
        q.put("m1")
        q.put("m2")
        q.put("m3")

        assert wait_until(lambda: len(received) >= 3, timeout_ms=1500), "Не все сообщения дошли"
        assert received[:3] == ["m1", "m2", "m3"]
    finally:
        thread.stop()
