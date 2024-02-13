from collections.abc import Mapping
from typing import IO, Any

from rest_framework.parsers import JSONParser as _JSONParser
from rest_framework.renderers import JSONRenderer as _JSONRenderer

from ..abc import Parser, Renderer


class JSONRenderer(_JSONRenderer, Renderer):
    pass


class JSONParser(_JSONParser, Parser):
    def parse(
        self,
        stream: IO[Any],
        media_type: str | None = None,
        parser_context: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        return super().parse(
            stream,
            media_type=media_type,
            parser_context=parser_context,
        )


__all__ = ["JSONRenderer", "JSONParser"]
