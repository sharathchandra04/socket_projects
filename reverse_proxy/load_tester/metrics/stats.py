import time
import threading


class Stats:
    def __init__(self):
        self.lock = threading.Lock()

        self.total_requests = 0
        self.success = 0
        self.failure = 0

        self.latencies = []  # store per-request latency

        self.start_time = time.time()

    # -----------------------------
    def record_request_start(self):
        return time.time()

    # -----------------------------
    def record_success(self, start_time):
        latency = time.time() - start_time

        with self.lock:
            self.total_requests += 1
            self.success += 1
            self.latencies.append(latency)

    # -----------------------------
    def record_failure(self):
        with self.lock:
            self.total_requests += 1
            self.failure += 1

    # -----------------------------
    def get_summary(self):
        with self.lock:
            total_time = time.time() - self.start_time

            avg_latency = (
                sum(self.latencies) / len(self.latencies)
                if self.latencies else 0
            )

            return {
                "total_requests": self.total_requests,
                "success": self.success,
                "failure": self.failure,
                "avg_latency_ms": avg_latency * 1000,
                "requests_per_sec": (
                    self.total_requests / total_time
                    if total_time > 0 else 0
                )
            }

    # -----------------------------
    def print_summary(self):
        summary = self.get_summary()

        print("\n========== LOAD TEST STATS ==========")
        for k, v in summary.items():
            print(f"{k}: {v}")
        print("====================================\n")