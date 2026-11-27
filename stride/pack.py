from . import FORMAT
from .codec import digest
from .problems import Problem
from .runner import run


def find_scene(doc, key):
    scene = next((scene for scene in doc['scenes'] if scene['id'] == key), None)
    if scene is None:
        raise Problem('未找到指定预演场景', 404)
    return scene


def freeze(record, key):
    doc = record['document']
    scene = find_scene(doc, key)
    content = dict(format=FORMAT, revision=record['revision'], parent=record['parent'],
                   document=doc, scene=key, trace=run(doc, scene))
    return dict(content=content, sha256=digest(content))
