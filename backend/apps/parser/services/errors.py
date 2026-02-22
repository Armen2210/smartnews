class ParserError(Exception):
    """Base parser exception."""


class RSSReadError(ParserError):
    """Raised when RSS feed can not be read."""


class ContentExtractionError(ParserError):
    """Raised when content extraction fails."""