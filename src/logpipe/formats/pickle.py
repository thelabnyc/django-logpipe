from collections.abc import Mapping
from typing import IO, Any
import pickle

from rest_framework import parsers, renderers

from ..abc import Parser, Renderer


class PickleRenderer(renderers.BaseRenderer, Renderer):
    media_type = "application/python-pickle"
    format = "pickle"
    charset = None
    render_style = "binary"

    def render(
        self,
        data: dict[str, Any],
        media_type: str | None = None,
        renderer_context: Mapping[str, Any] | None = None,
    ) -> bytes:
        return pickle.dumps(data)


class PickleParser(parsers.BaseParser, Parser):
    media_type = "application/python-pickle"

    def parse(
        self,
        stream: IO[Any],
        media_type: str | None = None,
        parser_context: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        return pickle.load(stream)


__all__ = ["PickleRenderer", "PickleParser"]
