"""构建预演使用的索引并保持声明顺序。"""
from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class Graph:
    clips: dict
    edges: dict
    marks: dict
    start: str
    ttl: int
    rig: list


def compile_graph(doc):
    edges, marks = defaultdict(list), defaultdict(list)
    for edge in sorted(doc['edges'], key=lambda edge: -edge['priority']):
        edges[edge['source']].append(edge)
    for clip in doc['clips']:
        for mark in clip['marks']:
            marks[clip['id'], mark['at']].append(mark['tag'])
    return Graph({clip['id']: clip for clip in doc['clips']}, dict(edges), dict(marks),
                 doc['start'], doc['ttl'], doc['rig'])
