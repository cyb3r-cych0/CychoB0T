from collections import defaultdict

class Metrics:
    def __init__(self):
        self.counters = defaultdict(int)
        self.timers = defaultdict(list)

    def inc(self, name, value=1):
        self.counters[name] += value

    def observe(self, name, ms):
        self.timers[name].append(ms)

    def snapshot(self):
        return {
            "counters": dict(self.counters),
            "timers": {k: {
                "count": len(v),
                "p50": sorted(v)[len(v)//2] if v else 0,
                "p95": sorted(v)[int(len(v)*0.95)] if v else 0,
            } for k, v in self.timers.items()}
        }

metrics = Metrics()
