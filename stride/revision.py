from contextlib import contextmanager
import fcntl
from pathlib import Path
import re

from .codec import decode, digest, encode
from .document import read_document
from .fs import atomic_write
from .problems import Problem

REVID = re.compile(r'[0-9a-f]{64}\Z')


class Revisions:
    def __init__(self, root, initial):
        self.root = Path(root)
        self.path = self.root / 'graphs'
        self.path.mkdir(parents=True, exist_ok=True)
        self.head = self.root / 'HEAD'
        with self.lock():
            if not self.head.exists():
                self._write(initial, None)

    @contextmanager
    def lock(self):
        with (self.root / 'writer.lock').open('ab') as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            yield

    def latest(self):
        return self.head.read_text(encoding='ascii').strip()

    def _write(self, doc, parent):
        record = dict(parent=parent, document=doc)
        revision = digest(record)
        target = self.path / f'{revision}.json'
        if not target.exists():
            atomic_write(target, encode(record))
        atomic_write(self.head, (revision + '\n').encode('ascii'))
        return dict(revision=revision, **record)

    def get(self, revision=None):
        revision = self.latest() if revision is None else revision
        if not isinstance(revision, str) or not REVID.fullmatch(revision):
            raise Problem('未找到指定修订', 404)
        try:
            record = decode((self.path / f'{revision}.json').read_bytes())
        except FileNotFoundError as error:
            raise Problem('未找到指定修订', 404) from error
        if digest(record) != revision:
            raise Problem('修订内容与标识不一致', 409)
        return dict(revision=revision, **record)

    def save(self, raw, base):
        doc = read_document(raw)
        with self.lock():
            latest = self.get()
            if base != latest['revision']:
                raise Problem('工作头已更新，请读取最新修订再保存', 409)
            if doc == latest['document']:
                return latest
            return self._write(doc, latest['revision'])

    def list(self):
        revision, items = self.latest(), []
        while revision is not None and len(items) < 60:
            record = self.get(revision)
            items.append(dict(revision=revision, title=record['document']['title'],
                              parent=record['parent']))
            revision = record['parent']
        return items
