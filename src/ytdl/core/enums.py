from enum import StrEnum


class Transport(StrEnum):
    TG = "tg"
    VK = "vk"


class Provider(StrEnum):
    YOUTUBE = "youtube"


class VideoKind(StrEnum):
    SHORTS = "shorts"
    # WATCH = "watch"
    # UNKNOWN = "unknown"
