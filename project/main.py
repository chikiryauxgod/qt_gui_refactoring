import sys
from src.integration.electroerosion_bridge import run_with_legacy_backend


def main() -> None:
    sys.exit(run_with_legacy_backend())


if __name__ == "__main__":
    main()
