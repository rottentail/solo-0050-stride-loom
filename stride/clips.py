from .fields import flag, identifier, integer, items, label, mapping
from .problems import Problem


def read_clip(raw, joints):
    row = mapping(raw, '动作片段')
    frames = integer(row.get('frames'), '源帧数', 1, 120)
    root = items(row.get('root'), '根位移', frames, frames)
    marks = []
    for item in items(row.get('marks'), '帧事件', 0, 64):
        mark = mapping(item, '帧事件')
        marks.append(dict(at=integer(mark.get('at'), '事件源帧', 0, frames - 1),
                          tag=identifier(mark.get('tag'), '事件标识')))
    keys = []
    for item in items(row.get('keys'), '姿态关键帧', 1, frames):
        key = mapping(item, '姿态关键帧')
        at = integer(key.get('at'), '姿态源帧', 0, frames - 1)
        values = items(key.get('angles'), '关节角度', joints, joints)
        if (not keys and at != 0) or (keys and at <= keys[-1]['at']):
            raise Problem('姿态源帧必须从零开始且严格递增')
        keys.append(dict(at=at, angles=[integer(a, '关节角度', -180, 180) for a in values]))
    return dict(id=identifier(row.get('id'), '动作标识'), label=label(row.get('label'), '动作名称'),
                frames=frames, loop=flag(row.get('loop'), '循环'),
                root=[integer(dx, '根位移', -100, 100) for dx in root], marks=marks, keys=keys)
