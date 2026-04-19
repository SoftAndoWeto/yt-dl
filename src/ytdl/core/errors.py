class CoreError(Exception):
    pass


class NoUrlFound(CoreError):
    pass


class UnsupportedUrl(CoreError):
    pass


class InvalidUrl(CoreError):
    pass


class DownloadFailed(CoreError):
    pass
