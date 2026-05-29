from .config import build_config
from .scheduler import run


def main() -> None:
    config = build_config()
    run(config)


if __name__ == "__main__":
    main()
