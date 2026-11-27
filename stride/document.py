from .clips import read_clip
from .edges import read_edges
from .fields import identifier, integer, items, label, mapping, reference, unique
from .problems import Problem
from .rig import read_rig
from .scenes import read_scene


def read_document(raw):
    row = mapping(raw, '动作图')
    if type(row.get('version')) is not int or row['version'] != 1:
        raise Problem('不支持此动作图版本')
    rig = read_rig(row.get('rig'))
    clips = [read_clip(clip, len(rig)) for clip in items(row.get('clips'), '动作片段', 1, 32)]
    ids = unique(clips, '动作片段')
    commands = [identifier(cmd, '命令标识') for cmd in items(row.get('commands'), '命令', 1, 32)]
    if len(set(commands)) != len(commands):
        raise Problem('命令标识重复')
    edges = read_edges(row.get('edges'), clips, set(commands))
    scenes = [read_scene(scene, set(commands)) for scene in items(row.get('scenes'), '预演场景', 1, 20)]
    unique(scenes, '预演场景')
    return dict(version=1, title=label(row.get('title'), '动作图名称'), rig=rig, clips=clips,
                start=reference(row.get('start'), ids, '起始动作'), commands=commands,
                ttl=integer(row.get('ttl'), '输入有效期', 0, 30), edges=edges, scenes=scenes)
