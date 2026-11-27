from .fields import identifier, integer, items, label, mapping
from .problems import Problem


def read_rig(raw):
    joints, seen = [], set()
    for index, item in enumerate(items(raw, '关节', 1, 24)):
        row = mapping(item, '关节')
        key = identifier(row.get('id'), '关节标识')
        parent = row.get('parent')
        if key in seen or (index == 0 and parent is not None) or (
                index > 0 and (not isinstance(parent, str) or parent not in seen)):
            raise Problem('关节必须组成先父后子的单根树')
        seen.add(key)
        joints.append(dict(id=key, parent=parent, label=label(row.get('label'), '关节名称'),
                           dx=integer(row.get('dx'), '关节横向偏移', -80, 80),
                           dy=integer(row.get('dy'), '关节纵向偏移', -80, 80)))
    return joints
