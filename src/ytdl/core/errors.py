class BaseError(Exception):
    pass


class NoUrlFound(BaseError):
    pass


class UnsupportedUrl(BaseError):
    pass


class InvalidUrl(BaseError):
    pass


class DownloadedFailed(BaseError):
    pass
