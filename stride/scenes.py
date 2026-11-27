from .fields import flag, identifier, integer, items, label, mapping, reference


def read_scene(raw, commands):
    row = mapping(raw, '预演场景')
    ticks = integer(row.get('ticks'), '预演总拍数', 1, 240)
    inputs = []
    for item in items(row.get('inputs'), '输入轨', 0, 320):
        item = mapping(item, '输入')
        inputs.append(dict(at=integer(item.get('at'), '输入拍', 0, ticks - 1),
                           command=reference(item.get('command'), commands, '输入命令')))
    return dict(id=identifier(row.get('id'), '场景标识'), label=label(row.get('label'), '场景名称'),
                ticks=ticks, inputs=inputs, mirror=flag(row.get('mirror'), '镜像'),
                speed=integer(row.get('speed'), '源帧推进数', 1, 2))
