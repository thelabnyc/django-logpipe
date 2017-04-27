from rest_framework import renderers, parsers
import pickle


class PickleRenderer(renderers.BaseRenderer):
    media_type = 'application/python-pickle'
    format = 'pickle'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return pickle.dumps(data)


class PickleParser(parsers.BaseParser):
    media_type = 'application/python-pickle'

    def parse(self, stream, media_type=None, parser_context=None):
        return pickle.load(stream)


__all__ = ['PickleRenderer', 'PickleParser']
