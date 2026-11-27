"""对真实 HTTP 入口运行有界、隔离的生产走查。"""
from copy import deepcopy
from tempfile import TemporaryDirectory
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from .codec import decode, digest, encode
from .http import server


def require(value, description):
    if not value:
        raise RuntimeError(description)


class Walk:
    def __init__(self, port):
        self.url = f'http://127.0.0.1:{port}/stride/api/'
        self.origin = self.call('graph')

    def call(self, route, payload=None, expected=200):
        body = encode(payload) if payload is not None else None
        request = Request(self.url + route, body, headers={'Content-Type': 'application/json'})
        try:
            reply = urlopen(request, timeout=8)
        except HTTPError as error:
            reply = error
        with reply:
            result = decode(reply.read())
            require(reply.code == expected, f'{route}：{reply.code} 不符 {expected}，{result}')
            return result

    def doc(self):
        return deepcopy(self.origin['document'])

    def scene(self, **values):
        return dict(self.doc()['scenes'][0], **values)

    def pack(self):
        return self.call(f"pack?revision={self.origin['revision']}&scene=dock-pass")


def load(w):
    listed = w.call('revisions')
    require(listed[0]['revision'] == w.origin['revision'], '演示修订未列出')
    w.call('graph?revision=missing', expected=404)
    return f"{w.origin['document']['title']} · {len(w.doc()['clips'])} 段动作"


def validate(w):
    doc = w.doc()
    require(w.call('validate', dict(document=doc))['document'] == doc, '合法图被改变')
    doc['edges'][0]['mark'] = 'missing'
    w.call('validate', dict(document=doc), 422)
    return '合法图规范化一致，未知事件条件被拒绝'


def preview(w):
    trace = w.call('run', dict(document=w.doc(), scene='dock-pass'))
    rows = trace['rows']
    picked = [(r['tick'], r['edge'], r['consumed']) for r in rows if r['edge']]
    require(picked[:3] == [(0, 'start_walk', 1), (3, 'plant_crouch', 2),
                           (6, 'stand_up', 3)], f'转场或消费顺序异常 {picked}')
    w.call('run', dict(document=w.doc(), scene=w.scene(ticks=0)), 422)
    return str(picked)


def variants(w):
    trace = w.call('run', dict(document=w.doc(), scene=w.scene(speed=2, mirror=True)))
    rows = trace['rows']
    require(rows[1]['crossed'] == [0, 1] and rows[1]['delta'] == -10, '镜像快进异常')
    w.call('run', dict(document=w.doc(), scene=w.scene(speed=3)), 422)
    return '首个行走拍穿越源帧 0、1，根位移 −10'


def compare(w):
    left = dict(document=w.doc(), scene='dock-pass')
    right = dict(document=w.doc(), scene=w.scene(inputs=[]))
    answer = w.call('compare', dict(left=left, right=right))
    require(answer['first'] == {'tick': 0, 'fields': ['edge', 'target', 'consumed']}, '首差异异常')
    w.call('compare', dict(left=left, right=dict(document=w.doc(), scene='missing')), 404)
    return '第零拍转场、目标、消费分歧；未知场景无法比较'


def save(w):
    doc = w.doc()
    base = w.call('graph')['revision']
    doc['title'] += ' · 调校'
    saved = w.call('save', dict(document=doc, base=base))
    require(saved['parent'] == base and saved['revision'] != base, '修订谱系异常')
    require(w.call('save', dict(document=doc, base=saved['revision'])) == saved, '相同内容重复写入')
    w.call('save', dict(document=w.doc(), base=base), 409)
    return '新子修订可读，相同内容沿用工作头，过期写入被拒绝'


def history(w):
    save(w)
    origin = w.call(f"graph?revision={w.origin['revision']}")
    require(origin == w.origin and len(w.call('revisions')) >= 2, '历史修订消失')
    w.call('graph?revision=' + 'a'*64, expected=404)
    return '旧图与最新图共存，未知修订返回 404'


def freeze(w):
    pack = w.pack()
    require(digest(pack['content']) == pack['sha256'], '冻结摘要无效')
    w.call('pack?scene=missing', expected=404)
    return f"交接摘要 {pack['sha256'][:14]}…，未知场景返回 404"


def verify(w):
    pack = w.pack()
    report = w.call('verify', dict(pack=pack))
    require(report['ticks'] == w.doc()['scenes'][0]['ticks'], '复验拍数异常')
    pack['content']['trace']['rows'][0]['world'] = 999
    w.call('verify', dict(pack=pack), 422)
    pack['sha256'] = digest(pack['content'])
    report = w.call('verify', dict(pack=pack), 422)
    require('无法复演' in report['error'], '复验未区分语义失败')
    return '摘要正确时仍可识别伪造逐拍结果'


def rehearse(w):
    pack = w.pack()
    result = w.call('rehearse', dict(pack=pack))
    require(result['trace'] == pack['content']['trace'], '重播与冻结轨迹不同')
    pack['content']['format'] = 'unknown'
    w.call('rehearse', dict(pack=pack), 422)
    return '重播与冻结轨迹一致，未知格式阻止重播'


CHECKS = dict(load=load, validate=validate, preview=preview, variants=variants, compare=compare,
              save=save, history=history, freeze=freeze, verify=verify, rehearse=rehearse)


def walkthrough(which):
    names = CHECKS if which == 'all' else [which]
    for name in names:
        with TemporaryDirectory(prefix='stride-walk-') as directory, server('127.0.0.1', 0, directory, True) as app:
            worker = Thread(target=app.serve_forever, daemon=True)
            worker.start()
            try:
                print(f'{name} ✓ {CHECKS[name](Walk(app.server_port))}', flush=True)
            finally:
                app.shutdown()
                worker.join()
