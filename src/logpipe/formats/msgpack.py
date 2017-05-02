from rest_framework import renderers, parsers

_import_error = None
try:
    import msgpack
except ImportError as e:
    msgpack = None
    _import_error = e


class MsgPackRenderer(renderers.BaseRenderer):
    media_type = 'application/msgpack'
    format = 'msgpack'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        if not msgpack:
            raise _import_error
        return msgpack.packb(data, use_bin_type=True)


class MsgPackParser(parsers.BaseParser):
    media_type = 'application/msgpack'

    def parse(self, stream, media_type=None, parser_context=None):
        if not msgpack:
            raise _import_error
        return msgpack.unpack(stream, use_list=False, encoding='utf-8')


__all__ = ['MsgPackRenderer', 'MsgPackParser']
