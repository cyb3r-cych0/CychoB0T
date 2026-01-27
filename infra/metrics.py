from collections import defaultdict


class Metrics:
    def __init__(self):
        self.counters = defaultdict(int)
        self.timers = defaultdict(list)
        self.gauges = {}

    # Counters
    def inc(self, name, value=1):
        self.counters[name] += value

    # Timers
    def observe(self, name, ms):
        self.timers[name].append(ms)

    # Gauges
    def set(self, name, value):
        self.gauges[name] = value

    def snapshot(self):
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "timers": {
                k: {
                    "count": len(v),
                    "p50": sorted(v)[len(v) // 2] if v else 0,
                    "p95": sorted(v)[int(len(v) * 0.95)] if v else 0,
                }
                for k, v in self.timers.items()
            },
        }


metrics = Metrics()
metrics.inc("offline_model_busy")
metrics.set("offline_inflight", 1)

