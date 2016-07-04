from rest_framework import renderers, parsers
import msgpack


class MsgPackRenderer(renderers.BaseRenderer):
    media_type = 'application/msgpack'
    format = 'msgpack'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return msgpack.packb(data, use_bin_type=True)


class MsgPackParser(parsers.BaseParser):
    media_type = 'application/msgpack'

    def parse(self, stream, media_type=None, parser_context=None):
        return msgpack.unpack(stream, use_list=False, encoding='utf-8')


__all__ = ['MsgPackRenderer', 'MsgPackParser']
