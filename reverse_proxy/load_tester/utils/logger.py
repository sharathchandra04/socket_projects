import time
import threading


class Logger:
    def __init__(self, name="SYSTEM", enabled=True):
        self.name = name
        self.enabled = enabled
        self.lock = threading.Lock()

    def _log(self, level, msg):
        if not self.enabled:
            return

        with self.lock:
            ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print(f"[{ts}] [{self.name}] [{level}] {msg}")

    def info(self, msg):
        self._log("INFO", msg)

    def debug(self, msg):
        self._log("DEBUG", msg)

    def error(self, msg):
        self._log("ERROR", msg)