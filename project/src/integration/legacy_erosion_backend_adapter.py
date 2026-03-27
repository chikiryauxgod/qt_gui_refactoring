from __future__ import annotations

from src.ports.erosion_backend_port import ErosionBackendPort


class LegacyErosionBackendAdapter(ErosionBackendPort):
    def __init__(self, backend):
        self._backend = backend

    def start(self, filename: str | None = None, **params) -> None:
        if hasattr(self._backend, "start"):
            self._backend.start()
            return
        if callable(self._backend):
            self._backend(filename, **params)
            return
        raise TypeError("Unsupported erosion backend: expected start() or callable backend")

    def stop(self) -> None:
        if hasattr(self._backend, "stop"):
            self._backend.stop()
            return
        if hasattr(self._backend, "safe_finish"):
            self._backend.safe_finish()
            return
        raise TypeError("Unsupported erosion backend: expected stop() or safe_finish()")
