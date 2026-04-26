from config.config import Config
from core.master import Master


def main():
    config = Config()

    master = Master(config)
    master.start()


if __name__ == "__main__":
    main()