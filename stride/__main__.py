import argparse
import os

from .http import server
from .walkthrough import CHECKS, walkthrough


def main():
    parser = argparse.ArgumentParser(description='折步台')
    commands = parser.add_subparsers(dest='operation', required=True)
    serve = commands.add_parser('serve', help='启动浏览器工作台')
    serve.add_argument('--port', type=int, default=8675)
    serve.add_argument('--host', default='127.0.0.1')
    serve.add_argument('--data', default=os.environ.get('STRIDE_LOOM_DATA', '.stride-data'))
    check = commands.add_parser('walkthrough', help='走查生产 HTTP 流程')
    check.add_argument('workflow', choices=['all', *CHECKS])
    args = parser.parse_args()
    if args.operation == 'walkthrough':
        walkthrough(args.workflow)
    else:
        with server(args.host, args.port, args.data) as instance:
            print(f'折步台已启动 http://{args.host}:{instance.server_port}', flush=True)
            try:
                instance.serve_forever()
            except KeyboardInterrupt:
                pass


if __name__ == '__main__':
    main()
