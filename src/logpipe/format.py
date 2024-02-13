from io import BytesIO
from typing import Any, TypedDict

from .abc import Parser, Renderer
from .exceptions import UnknownFormatError


class FormatRegistryEntry(TypedDict):
    renderer: Renderer
    parser: Parser


FormatRegistry = dict[bytes, FormatRegistryEntry]

_delim = b":"
_formats: FormatRegistry = {}


def _bytes(seq: str | bytes) -> bytes:
    return seq.encode() if hasattr(seq, "encode") else seq


def register(codestr: str, renderer: Renderer, parser: Parser) -> None:
    code = _bytes(codestr)
    _formats[code] = {
        "renderer": renderer,
        "parser": parser,
    }


def unregister(codestr: str) -> None:
    code = _bytes(codestr)
    try:
        del _formats[code]
    except KeyError:
        pass


def render(codestr: str, data: dict[str, Any]) -> bytes:
    code = _bytes(codestr)
    if code not in _formats:
        raise UnknownFormatError(f"Could not find renderer for format {codestr}")
    body = _formats[code]["renderer"].render(data)
    return code + _delim + body


def parse(_data: str | bytes) -> dict[str, Any]:
    data = _bytes(_data)
    code, body = data.split(_delim, 1)
    if code not in _formats:
        raise UnknownFormatError("Could not find parser for format %s" % code.decode())
    return _formats[code]["parser"].parse(BytesIO(body))


__all__ = ["register", "unregister", "render", "parse"]
