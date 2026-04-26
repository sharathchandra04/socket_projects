from config.config import load_config
from backend.server import BackendServer


def main():
    config = load_config()
    server = BackendServer(config)
    server.start()


if __name__ == "__main__":
    main()