import re
from urllib.parse import ParseResult, urlparse

from ytdl.core.enums import Provider, VideoKind
from ytdl.core.errors import InvalidUrl, NoUrlFound, UnsupportedUrl
from ytdl.core.models import VideoUrl

ALLOWED_YOUTUBE_HOSTS = frozenset(
    {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
    }
)
URL_PATTERN = re.compile(r"https?://\S+")


def remove_brackets_beyond(text: str) -> str:
    text = text.lstrip("([{<\"'")
    text = text.rstrip(")]}>\"'`.,;:!?")
    return text


def find_first_url(text: str) -> str | None:
    for match in URL_PATTERN.finditer(text):
        url = remove_brackets_beyond(match.group(0))
        if url:
            return url

    return None


def valid_provider(url: str) -> bool:
    return url.lower() in ALLOWED_YOUTUBE_HOSTS


def get_provider(url: str) -> Provider | None:
    if valid_provider(url):
        return Provider.YOUTUBE

    return None


def valid_kind(url: str) -> bool:
    return _get_shorts_video_id(url) is not None


def get_kind(url: str) -> VideoKind | None:
    if valid_kind(url):
        return VideoKind.SHORTS

    return None


def get_video_id(path: str) -> str:
    video_id = _get_shorts_video_id(path)
    if video_id is None:
        raise UnsupportedUrl(f"Unsupported video URL path: {path}")

    return video_id


def build_original_url(url: str) -> str:
    return _normalize_url(urlparse(url)).geturl()


def valid_url(url: str) -> bool:
    try:
        parse_video_url(url)
    except (InvalidUrl, UnsupportedUrl):
        return False

    return True


def parse_video_url(url: str) -> VideoUrl:
    parsed_url = urlparse(url)
    if not _has_valid_url_shape(parsed_url):
        raise InvalidUrl(f"Invalid URL: {url}")

    provider = get_provider(parsed_url.netloc)
    if provider is None:
        raise UnsupportedUrl(f"Unsupported provider: {parsed_url.netloc}")

    kind = get_kind(parsed_url.path)
    if kind is None:
        raise UnsupportedUrl(f"Unsupported video URL path: {parsed_url.path}")

    return VideoUrl(
        video_id=get_video_id(parsed_url.path),
        original_url=url,
        normalized_url=_normalize_url(parsed_url).geturl(),
        provider=provider,
        kind=kind,
    )


def extract_video_url(text: str) -> VideoUrl:
    url = find_first_url(text)
    if url is None:
        raise NoUrlFound("No URL found in text")

    return parse_video_url(url)


def build_video_url(url: str) -> VideoUrl:
    return parse_video_url(url)


def _has_valid_url_shape(parsed_url: ParseResult) -> bool:
    return parsed_url.scheme == "https" and bool(parsed_url.netloc)


def _normalize_url(parsed_url: ParseResult) -> ParseResult:
    return parsed_url._replace(
        scheme=parsed_url.scheme.lower(),
        netloc=parsed_url.netloc.lower(),
        fragment="",
    )


def _get_shorts_video_id(path: str) -> str | None:
    parts = path.strip("/").split("/")
    if len(parts) != 2:
        return None

    kind, video_id = parts
    if kind != VideoKind.SHORTS or not video_id:
        return None

    return video_id
