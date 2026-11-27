"""外部文档的基本类型与有界字段。"""
import re

from .problems import Problem

KEY = re.compile(r'[a-z][a-z0-9_-]{0,31}\Z')


def mapping(value, field):
    if not isinstance(value, dict):
        raise Problem(f'{field} 必须是对象')
    return value


def items(value, field, least=0, most=160):
    if not isinstance(value, list) or not least <= len(value) <= most:
        raise Problem(f'{field} 必须包含 {least} 至 {most} 项')
    return value


def integer(value, field, low, high):
    if type(value) is not int or not low <= value <= high:
        raise Problem(f'{field} 必须是 {low} 至 {high} 的整数')
    return value


def identifier(value, field):
    if not isinstance(value, str) or not KEY.fullmatch(value):
        raise Problem(f'{field} 需要小写英文标识')
    return value


def label(value, field):
    if not isinstance(value, str) or not 1 <= len(value.strip()) <= 80:
        raise Problem(f'{field} 需要 1 至 80 个字符')
    return value.strip()


def flag(value, field):
    if type(value) is not bool:
        raise Problem(f'{field} 必须是布尔值')
    return value


def unique(rows, field):
    keys = {row['id'] for row in rows}
    if len(keys) != len(rows):
        raise Problem(f'{field} 标识重复')
    return keys


def reference(value, keys, field):
    key = identifier(value, field)
    if key not in keys:
        raise Problem(f'{field} 未定义：{key}')
    return key
