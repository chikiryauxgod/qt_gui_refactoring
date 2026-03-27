__all__ = ["create_hardware_controller", "run_with_legacy_backend"]


def __getattr__(name):
    if name in __all__:
        from src.integration.electroerosion_bridge import (
            create_hardware_controller,
            run_with_legacy_backend,
        )

        exports = {
            "create_hardware_controller": create_hardware_controller,
            "run_with_legacy_backend": run_with_legacy_backend,
        }
        return exports[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
