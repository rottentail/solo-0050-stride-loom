from .compare import compare
from .document import read_document
from .fields import mapping
from .pack import find_scene, freeze
from .problems import Problem
from .runner import run
from .scenes import read_scene
from .verify import verify

BASE = '/stride/api/'


def read_run(payload):
    data = mapping(payload, '预演请求')
    doc = read_document(data.get('document'))
    scene = data.get('scene')
    if isinstance(scene, str):
        return doc, find_scene(doc, scene)
    return doc, read_scene(scene, set(doc['commands']))


class API:
    def __init__(self, store):
        self.store = store

    def get(self, path, query):
        if path == 'graph':
            return self.store.get(query.get('revision', [None])[0])
        if path == 'revisions':
            return self.store.list()
        if path == 'pack':
            return freeze(self.store.get(query.get('revision', [None])[0]), query.get('scene', [None])[0])
        raise Problem('未找到接口', 404)

    def post(self, path, payload):
        body = mapping(payload, '请求')
        if path == 'validate':
            return dict(document=read_document(body.get('document')))
        if path == 'run':
            return run(*read_run(body))
        if path == 'compare':
            return compare(*read_run(body.get('left')), *read_run(body.get('right')))
        if path == 'save':
            return self.store.save(body.get('document'), body.get('base'))
        if path in {'verify', 'rehearse'}:
            result = verify(body.get('pack'))
            if path == 'rehearse':
                return result
            return dict(revision=result['revision'], scene=result['scene']['id'],
                        ticks=len(result['trace']['rows']))
        raise Problem('未找到接口', 404)
