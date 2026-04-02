from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from pathlib import Path

from src.application.application_runner import run
from src.log import logger, q
from src.services.hardware_controller import HardwareController


@contextmanager
def _working_directory(path: Path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def embedded_legacy_root() -> Path:
    return Path(__file__).resolve().parents[2] / "electroerosion"


def create_hardware_controller(legacy_root: str | os.PathLike[str]) -> HardwareController:
    legacy_path = Path(legacy_root).resolve()

    if str(legacy_path) not in sys.path:
        sys.path.insert(0, str(legacy_path))

    try:
        with _working_directory(legacy_path):
            import electoerosion

            erode = electoerosion.Electroerosion(queue=q)
        logger(f"Legacy backend loaded from {legacy_path}", queue=q)
        return HardwareController(erode=erode)
    except Exception as exc:
        logger(
            f"Legacy backend unavailable ({type(exc).__name__}: {exc}). Fallback to local stubs.",
            queue=q,
        )
        return HardwareController()


def run_with_legacy_backend(legacy_root: str | os.PathLike[str] | None = None) -> int:
    if legacy_root is None:
        legacy_root = embedded_legacy_root()
    hardware_controller = create_hardware_controller(legacy_root)
    return run(hardware_controller=hardware_controller, q_ref=q)
