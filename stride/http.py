from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import mimetypes
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from .api import API, BASE
from .codec import decode, encode
from .demo import demo_document
from .problems import Problem
from .revision import Revisions

WEB = Path(__file__).with_name('web')
LIMIT = 16 * 1024 * 1024


class Handler(BaseHTTPRequestHandler):
    def __init__(self, *args, api, quiet, **kwargs):
        self.api, self.quiet = api, quiet
        super().__init__(*args, **kwargs)

    def log_message(self, pattern, *args):
        if not self.quiet:
            super().log_message(pattern, *args)

    def send(self, body, kind, status=200):
        self.send_response(status)
        self.send_header('Content-Type', kind)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def respond(self, result, status=200):
        self.send(encode(result), 'application/json; charset=utf-8', status)

    def do_GET(self):
        try:
            url = urlsplit(self.path)
            if url.path.startswith(BASE):
                self.respond(self.api.get(url.path.removeprefix(BASE), parse_qs(url.query)))
                return
            name = 'index.html' if url.path == '/' else url.path.removeprefix('/stride/static/')
            if url.path != '/' and not url.path.startswith('/stride/static/'):
                raise Problem('未找到页面', 404)
            file = WEB / name
            if file.suffix not in {'.js', '.html', '.css'} or file.parent != WEB or not file.is_file():
                raise Problem('未找到界面资源', 404)
            kind = mimetypes.guess_type(file.name)[0]
            self.send(file.read_bytes(), f'{kind}; charset=utf-8')
        except Problem as error:
            self.respond(dict(error=str(error)), error.status)

    def do_POST(self):
        try:
            path = urlsplit(self.path).path
            if not path.startswith(BASE):
                raise Problem('未找到接口', 404)
            if self.headers.get_content_type() != 'application/json':
                raise Problem('请求需要 application/json', 415)
            try:
                count = int(self.headers.get('Content-Length', ''))
            except ValueError as error:
                raise Problem('无效的请求长度', 400) from error
            if not 0 < count <= LIMIT:
                raise Problem('请求资料超出上限或为空', 413)
            body = decode(self.rfile.read(count))
            self.respond(self.api.post(path.removeprefix(BASE), body))
        except Problem as error:
            self.respond(dict(error=str(error)), error.status)


def server(host, port, directory, quiet=False):
    api = API(Revisions(directory, demo_document()))
    return ThreadingHTTPServer((host, port), partial(Handler, api=api, quiet=quiet))
