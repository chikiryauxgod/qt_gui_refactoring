from pathlib import Path
import sys


REF_GUI_ROOT = Path("/home/lew/prog/qt_gui_refactoring/project")
LEGACY_ROOT = Path(__file__).resolve().parent


if str(REF_GUI_ROOT) not in sys.path:
    sys.path.insert(0, str(REF_GUI_ROOT))


from src.integration.electroerosion_bridge import run_with_legacy_backend


def main() -> int:
    return run_with_legacy_backend(LEGACY_ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
