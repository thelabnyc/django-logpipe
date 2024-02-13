from collections.abc import Mapping
from typing import IO, Any
from rest_framework import renderers, parsers
from ..abc import Renderer, Parser

_import_error: ImportError
try:
    import msgpack
except ImportError as e:
    msgpack = None  # type: ignore[assignment]
    _import_error = e


class MsgPackRenderer(renderers.BaseRenderer, Renderer):
    media_type = "application/msgpack"
    format = "msgpack"
    charset = None
    render_style = "binary"

    def render(
        self,
        data: dict[str, Any],
        media_type: str | None = None,
        renderer_context: Mapping[str, Any] | None = None,
    ) -> bytes:
        if not msgpack:
            raise _import_error
        return msgpack.packb(data, use_bin_type=True)


class MsgPackParser(parsers.BaseParser, Parser):
    media_type = "application/msgpack"

    def parse(
        self,
        stream: IO[Any],
        media_type: str | None = None,
        parser_context: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not msgpack:
            raise _import_error
        return msgpack.unpack(stream, use_list=False)


__all__ = ["MsgPackRenderer", "MsgPackParser"]
