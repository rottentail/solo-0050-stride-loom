from . import FORMAT
from .codec import digest
from .document import read_document
from .fields import mapping
from .pack import find_scene
from .problems import Problem
from .revision import REVID
from .runner import run


def verify(raw):
    envelope = mapping(raw, '交接包')
    content = mapping(envelope.get('content'), '交接包内容')
    if content.get('format') != FORMAT:
        raise Problem('不支持此交接格式')
    if digest(content) != envelope.get('sha256'):
        raise Problem('交接包摘要不一致')
    doc = read_document(content.get('document'))
    parent = content.get('parent')
    if parent is not None and (not isinstance(parent, str) or not REVID.fullmatch(parent)):
        raise Problem('交接包父修订无效')
    identity = digest(dict(parent=parent, document=doc))
    if identity != content.get('revision') or digest(content.get('document')) != digest(doc):
        raise Problem('交接包内的动作图与修订不一致')
    scene = find_scene(doc, content.get('scene'))
    result = run(doc, scene)
    if digest(result) != digest(content.get('trace')):
        raise Problem('交接包轨迹无法复演')
    return dict(revision=identity, document=doc, scene=scene, trace=result)
