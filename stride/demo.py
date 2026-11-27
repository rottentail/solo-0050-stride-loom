from pathlib import Path

from .codec import decode
from .document import read_document


def demo_document():
    return read_document(decode(Path(__file__).with_name('data').joinpath('lantern.json').read_bytes()))
