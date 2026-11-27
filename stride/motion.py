"""世界根位置与源帧事件共用同一个实际推进列表。"""


def traverse(graph, clip, passed, mirror):
    delta = sum(clip['root'][frame] for frame in passed)
    marks = [dict(at=frame, tag=tag) for frame in passed
             for tag in graph.marks.get((clip['id'], frame), ())]
    return -delta if mirror else delta, marks
