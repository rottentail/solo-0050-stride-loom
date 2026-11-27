from .runner import run

OBSERVABLE = ('clip', 'frame', 'crossed', 'world', 'edge', 'target', 'events', 'pose', 'consumed')


def compare(left_doc, left_scene, right_doc, right_scene):
    left, right = run(left_doc, left_scene), run(right_doc, right_scene)
    differences = []
    for a, b in zip(left['rows'], right['rows']):
        fields = [field for field in OBSERVABLE if a[field] != b[field]]
        if fields:
            differences.append(dict(tick=a['tick'], fields=fields))
    matched = min(len(left['rows']), len(right['rows']))
    for tick in range(matched, max(len(left['rows']), len(right['rows']))):
        differences.append(dict(tick=tick, fields=['length']))
    return dict(left=left, right=right, differences=differences,
                first=differences[0] if differences else None)
