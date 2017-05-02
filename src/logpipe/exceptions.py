class LogPipeError(Exception):
    pass


class UnknownFormatError(LogPipeError):
    pass


class UnknownMessageTypeError(LogPipeError):
    pass


class UnknownMessageVersionError(LogPipeError):
    pass


class InvalidMessageError(LogPipeError):
    pass


class MissingTopicError(LogPipeError):
    pass
