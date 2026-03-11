from __future__ import annotations

import queue
from abc import ABC, abstractmethod
from typing import Optional

from PySide6.QtCore import QThread, Signal


class MessageSource(ABC):
    @abstractmethod
    def try_get(self) -> Optional[str]:
        """Вернуть сообщение или None, если пока нет."""
        ...

class QueueMessageSource(MessageSource):
    def __init__(self, message_queue: queue.Queue):
        self._q = message_queue

    def try_get(self) -> Optional[str]:
        try:
            return self._q.get_nowait()
        except queue.Empty:
            return None

class LogTextBoxErrosion(QThread):
    new_message = Signal(str)

    def __init__(self, source: MessageSource, latency_ms: int = 100):
        super().__init__()
        self._source = source
        self._latency_ms = latency_ms
        self._running = True

    def run(self):
        while self._running:
            msg = self._source.try_get()
            if msg is None:
                self.msleep(self._latency_ms)
                continue
            self.new_message.emit(msg)

    def stop(self):
        self._running = False
        self.wait()