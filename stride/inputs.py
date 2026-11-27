from collections import defaultdict
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Press:
    id: int
    at: int
    command: str


def schedule(scene):
    ticks = defaultdict(list)
    for index, item in enumerate(scene['inputs'], 1):
        ticks[item['at']].append(Press(index, item['at'], item['command']))
    return ticks


class Buffer:
    def __init__(self, ttl):
        self.ttl = ttl
        self.pending = []

    def begin(self, tick, arrivals):
        lost = [item.id for item in self.pending if tick - item.at > self.ttl]
        self.pending = [item for item in self.pending if tick - item.at <= self.ttl]
        self.pending.extend(arrivals)
        return lost

    def find(self, command):
        return next((item for item in self.pending if item.command == command), None)

    def consume(self, press):
        self.pending.remove(press)

    def snapshot(self):
        return [asdict(item) for item in self.pending]
