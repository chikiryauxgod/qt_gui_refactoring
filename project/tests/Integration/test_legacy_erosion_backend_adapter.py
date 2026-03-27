from src.integration.legacy_erosion_backend_adapter import LegacyErosionBackendAdapter


def test_adapter_delegates_start_to_backend_start():
    calls = []

    class Backend:
        def start(self):
            calls.append(("start",))

        def stop(self):
            calls.append(("stop",))

    adapter = LegacyErosionBackendAdapter(Backend())

    adapter.start("file.nc", speed=10)
    adapter.stop()

    assert calls == [("start",), ("stop",)]


def test_adapter_delegates_start_to_callable_backend():
    calls = []

    class Backend:
        def __call__(self, filename=None, **params):
            calls.append((filename, params))

        def safe_finish(self):
            calls.append(("safe_finish", {}))

    adapter = LegacyErosionBackendAdapter(Backend())

    adapter.start("file.nc", speed=10, mode="test")
    adapter.stop()

    assert calls[0][0] == "file.nc"
    assert calls[0][1]["speed"] == 10
    assert calls[0][1]["mode"] == "test"
    assert calls[1][0] == "safe_finish"
