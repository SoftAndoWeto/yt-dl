from dataclasses import dataclass
from pathlib import Path

from ytdl.core.enums import Transport, Provider, VideoKind


@dataclass(frozen=True)
class RequestContext:
    platform: Transport
    user_id: str
    chat_id: str


@dataclass(frozen=True)
class DownloadRequest:
    text: str
    context: RequestContext


class VideoUrl:
    video_id: str | None
    original_url: str
    normalized_url: str
    provider: Provider
    kind: VideoKind

    def __init__(self, video_id: str, original_url: str, normalized_url: str, provider: Provider, kind: VideoKind):
        self.video_id = video_id
        self.original_url = original_url
        self.normalized_url = normalized_url
        self.provider = provider
        self.kind = kind


@dataclass(frozen=True)
class DownloadedFile:
    path: Path
    filename: str
    size_bytes: int
    mime_type: str | None


@dataclass(frozen=True)
class DownloadResult:
    url: VideoUrl
    file: DownloadedFile
    title: str | None
    duration_sec: int | None
