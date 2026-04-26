import time
from collections import defaultdict


class Metrics:

    def __init__(self):
        # Counters
        self.counters = defaultdict(int)

        # Latency tracking
        self.latencies = defaultdict(list)

    # -----------------------------
    # Counters
    # -----------------------------
    def inc(self, name, value=1):
        self.counters[name] += value

    def get(self, name):
        return self.counters.get(name, 0)

    # -----------------------------
    # Latency
    # -----------------------------
    def record_latency(self, name, duration):
        self.latencies[name].append(duration)

    def get_avg_latency(self, name):
        values = self.latencies.get(name, [])
        if not values:
            return 0
        return sum(values) / len(values)

    # -----------------------------
    # Timer helper
    # -----------------------------
    def start_timer(self):
        return time.time()

    def end_timer(self, name, start_time):
        duration = time.time() - start_time
        self.record_latency(name, duration)

    # -----------------------------
    # Snapshot (for debugging/logging)
    # -----------------------------
    def snapshot(self):
        return {
            "counters": dict(self.counters),
            "avg_latencies": {
                k: self.get_avg_latency(k)
                for k in self.latencies
            },
        }