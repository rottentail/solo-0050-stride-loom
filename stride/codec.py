import hashlib
import json

from .problems import Problem


def _invalid_constant(_):
    raise ValueError('non-finite number')


def encode(value):
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'),
                          allow_nan=False).encode('utf-8')
    except (ValueError, UnicodeError, RecursionError) as error:
        raise Problem('无法编码此资料') from error


def decode(value):
    try:
        return json.loads(value.decode('utf-8'), parse_constant=_invalid_constant)
    except (ValueError, UnicodeError, RecursionError) as error:
        raise Problem('资料必须是有效的 UTF-8 JSON', 400) from error


def digest(value):
    return hashlib.sha256(encode(value)).hexdigest()
