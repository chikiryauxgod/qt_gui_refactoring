import sys
from pathlib import Path

# добавляем корень проекта в sys.path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.qt_interface import run


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()