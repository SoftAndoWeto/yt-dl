import mimetypes
from pathlib import Path
from typing import Any

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from ytdl.core.errors import DownloadFailed
from ytdl.core.models import DownloadedFile, DownloadRequest, DownloadResult, VideoUrl
from ytdl.core.url_parser import extract_video_url


class DownloadService:
    def __init__(self, downloader: "VideoDownloader | None" = None) -> None:
        self.downloader = downloader or VideoDownloader()

    def request(self, dl_req: DownloadRequest) -> DownloadResult:
        video_url = extract_video_url(dl_req.text)
        return self.downloader.download(video_url)


class VideoDownloader:
    def __init__(self, download_dir: Path | str = "downloads") -> None:
        self.download_dir = Path(download_dir)

    def download(self, video_url: VideoUrl) -> DownloadResult:
        self.download_dir.mkdir(parents=True, exist_ok=True)

        ydl_options = {
            "format": "best[ext=mp4]/best",
            "noplaylist": True,
            "no_warnings": True,
            "outtmpl": str(self.download_dir / "%(id)s.%(ext)s"),
            "quiet": True,
        }

        try:
            with YoutubeDL(ydl_options) as ydl:
                info = ydl.extract_info(video_url.normalized_url, download=True)
                if info is None:
                    raise DownloadFailed("yt-dlp returned no metadata")

                file_path = self._get_downloaded_path(info, ydl)
        except DownloadFailed:
            raise
        except (DownloadError, OSError) as exc:
            raise DownloadFailed(f"Failed to download video: {video_url.normalized_url}") from exc

        return DownloadResult(
            url=video_url,
            file=DownloadedFile(
                path=file_path,
                filename=file_path.name,
                size_bytes=file_path.stat().st_size,
                mime_type=mimetypes.guess_type(file_path.name)[0],
            ),
            title=info.get("title"),
            duration_seconds=_to_int_or_none(info.get("duration")),
        )

    def _get_downloaded_path(self, info: dict[str, Any], ydl: YoutubeDL) -> Path:
        requested_downloads = info.get("requested_downloads") or []
        for downloaded_file in requested_downloads:
            path = _path_from_info(downloaded_file)
            if path is not None and path.exists():
                return path

        path = _path_from_info(info)
        if path is not None and path.exists():
            return path

        path = Path(ydl.prepare_filename(info))
        if path.exists():
            return path

        raise DownloadFailed("Downloaded file was not found")


def _path_from_info(info: dict[str, Any]) -> Path | None:
    filename = info.get("filepath") or info.get("_filename")
    if not filename:
        return None

    return Path(filename)


def _to_int_or_none(value: Any) -> int | None:
    if value is None:
        return None

    return int(value)
