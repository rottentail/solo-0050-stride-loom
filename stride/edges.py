from .fields import identifier, integer, items, mapping, reference, unique
from .problems import Problem


def read_edges(raw, clips, commands):
    clip_ids = {clip['id'] for clip in clips}
    tags = {clip['id']: {mark['tag'] for mark in clip['marks']} for clip in clips}
    result = []
    for item in items(raw, '转场', 0, 90):
        row = mapping(item, '转场')
        source = reference(row.get('source'), clip_ids, '来源动作')
        mark = row.get('mark')
        if mark is not None:
            mark = reference(mark, tags[source], '来源事件条件')
        result.append(dict(id=identifier(row.get('id'), '转场标识'), source=source,
                           target=reference(row.get('target'), clip_ids, '目标动作'),
                           command=reference(row.get('command'), commands, '转场命令'), mark=mark,
                           age=integer(row.get('age'), '最短停留拍数', 1, 240),
                           priority=integer(row.get('priority'), '优先级', -100, 100)))
    unique(result, '转场')
    return result
