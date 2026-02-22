import html.parser
import ipaddress
import socket
import urllib.request
import urllib.error
import urllib.parse


class _HTMLTextExtractor(html.parser.HTMLParser):
    """Minimal HTML parser that extracts visible text from a page."""

    _SKIP_TAGS = {"script", "style", "head", "meta", "link", "noscript"}

    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []
        self._skip_depth: int = 0

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag.lower() in self._SKIP_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self._SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            stripped = data.strip()
            if stripped:
                self._parts.append(stripped)

    def get_text(self) -> str:
        return "\n".join(self._parts)


def _resolve_and_check(hostname: str) -> str:
    """Resolve hostname to an IP, validate it's not private, and return the IP string."""

    try:
        resolved_ip = socket.getaddrinfo(hostname, None)[0][4][0]
        addr = ipaddress.ip_address(resolved_ip)
    except (socket.gaierror, ValueError):
        raise ValueError(f"Could not resolve hostname: {hostname!r}")

    if addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved:
        raise ValueError(
            f"Requests to private or internal network addresses are not allowed "
            f"(resolved {hostname!r} → {resolved_ip})"
        )

    return resolved_ip


def _validate_url(url: str) -> tuple[str, str]:
    """Validate URL scheme/hostname and return (safe_url_with_ip, original_hostname).

    The returned ``safe_url`` replaces the hostname with the resolved IP so that
    the actual HTTP request avoids a TOCTOU DNS-rebinding race.

    Raises:
        ValueError: If the URL is invalid or resolves to a private/internal address.
    """

    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"URL must start with http:// or https://. Got: {url!r}")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError(f"URL has no hostname: {url!r}")

    resolved_ip = _resolve_and_check(hostname)

    # Build a URL that uses the resolved IP to prevent DNS-rebinding TOCTOU race.
    # Preserve port if explicitly set, or use the default for the scheme.
    port = parsed.port
    if port:
        netloc_with_ip = f"{resolved_ip}:{port}"
    elif ":" in resolved_ip:  # IPv6
        netloc_with_ip = f"[{resolved_ip}]"
    else:
        netloc_with_ip = resolved_ip

    safe_url = urllib.parse.urlunparse(
        parsed._replace(netloc=netloc_with_ip)
    )
    return safe_url, hostname


def load_url(url: str, timeout: int = 15) -> str:
    """Fetch a web page and return its visible text content.

    Args:
        url: The URL to fetch.  Must start with ``http://`` or ``https://``
             and must not resolve to a private/internal network address.
        timeout: Request timeout in seconds.

    Returns:
        The visible text extracted from the page.

    Raises:
        ValueError: If the URL scheme is not http/https or resolves to a private address.
        RuntimeError: If the page could not be fetched.
    """

    # Resolve & validate once; use the IP-based URL to avoid TOCTOU DNS-rebinding.
    safe_url, original_hostname = _validate_url(url)

    headers = {
        # Preserve original Host header so servers respond correctly.
        "Host": original_hostname,
        "User-Agent": (
            "Mozilla/5.0 (compatible; PersonalAIRAG/1.0; +https://github.com)"
        ),
    }

    req = urllib.request.Request(safe_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            content_type = response.headers.get("Content-Type", "")
            raw_bytes = response.read()
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Failed to fetch URL {url!r}: {exc}") from exc

    # Detect encoding from Content-Type header; fall back to utf-8
    charset = "utf-8"
    if "charset=" in content_type:
        charset = content_type.split("charset=")[1].split(";")[0].strip()

    raw_text = raw_bytes.decode(charset, errors="replace")

    content_type_lower = content_type.lower()
    if content_type_lower.startswith(("text/html", "application/xhtml+xml")):
        parser = _HTMLTextExtractor()
        parser.feed(raw_text)
        return parser.get_text()

    return raw_text
