"""Website icons and names for saved logins, fetched directly from each site and kept in an
encrypted local cache.

Privacy and safety rules:
- Requests go only to the login's own host (or its parent domain) and the icon URLs it
  declares, never to an icon service that would learn the whole list of accounts.
- HTTPS only, no cookies or credentials, a generic user agent, bounded sizes, bounded
  redirects, and every hop must resolve to public internet addresses (no loopback, private,
  link-local, or reserved ranges).
- Downloaded bytes are decoded as an image and re-encoded as a small PNG; nothing else from
  the response is kept except a sanitized site name.
- The cache is encrypted with the vault's master key; file names are keyed hashes, so the
  disk does not reveal which sites have saved logins.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import html
import ipaddress
import json
import os
import re
import socket
import threading
import time
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import nacl.exceptions
import nacl.secret

ICON_PX = 128
MAX_HTML = 300_000
MAX_IMAGE = 512_000
MAX_CUSTOM = 2_000_000
MAX_REDIRECTS = 3
TIMEOUT = 6
RETRY_FAILED_AFTER = 7 * 24 * 3600
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64)"

_HOST = re.compile(r"^(?=.{1,253}$)(?!-)[a-z0-9-]{1,63}(?<!-)(\.(?!-)[a-z0-9-]{1,63}(?<!-))+$")
_LINK = re.compile(r"<link\b[^>]*>", re.IGNORECASE)
_META = re.compile(r"<meta\b[^>]*>", re.IGNORECASE)
_ATTR = re.compile(r"""([a-zA-Z:-]+)\s*=\s*("([^"]*)"|'([^']*)'|([^\s>]+))""")
_TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_CONTROL = re.compile(r"[\x00-\x1f\x7f​-‏‪-‮⁦-⁩]")


class FetchError(Exception):
    pass


# ---- naming ------------------------------------------------------------------------------
def normalize_host(value: str) -> str:
    host = (value or "").strip().lower().rstrip(".")
    if "://" in host:
        host = urlsplit(host).hostname or ""
    if host.startswith("www."):
        host = host[4:]
    return host if _HOST.match(host) and not _is_ip_literal(host) else ""


def _is_ip_literal(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def candidate_hosts(host: str) -> list[str]:
    """The host, its www. form, then its parent when it has three or more labels."""
    labels = host.split(".")
    hosts = [host, f"www.{host}"]
    if len(labels) >= 3:
        hosts.append(".".join(labels[1:]))
    return hosts


def clean_name(raw: str) -> str:
    text = _CONTROL.sub("", html.unescape(raw or ""))
    text = re.sub(r"\s+", " ", text).strip()
    return text[:40].strip()


def _attrs(tag: str) -> dict:
    out = {}
    for match in _ATTR.finditer(tag):
        out[match.group(1).lower()] = html.unescape(match.group(3) or match.group(4) or match.group(5) or "")
    return out


def parse_page(page: str, base_url: str) -> tuple[list[str], str]:
    """Icon URLs (best first) and a site name from a home page's HTML."""
    icons: list[tuple[int, str]] = []
    for tag in _LINK.findall(page):
        attrs = _attrs(tag)
        rel = attrs.get("rel", "").lower()
        href = attrs.get("href", "")
        if not href or "icon" not in rel or "mask-icon" in rel:
            continue
        if href.lower().endswith(".svg") or attrs.get("type", "").lower() == "image/svg+xml":
            continue
        size = 0
        for part in attrs.get("sizes", "").lower().split():
            if "x" in part and part.split("x")[0].isdigit():
                size = max(size, int(part.split("x")[0]))
        rank = size + (1000 if "apple-touch-icon" in rel else 0)
        icons.append((rank, urljoin(base_url, href)))
    icons.sort(key=lambda pair: -pair[0])

    names = {}
    for tag in _META.findall(page):
        attrs = _attrs(tag)
        key = (attrs.get("property") or attrs.get("name") or "").lower()
        if key in ("og:site_name", "application-name", "apple-mobile-web-app-title"):
            names.setdefault(key, attrs.get("content", ""))
    name = (names.get("og:site_name") or names.get("application-name")
            or names.get("apple-mobile-web-app-title") or "")
    if not name:
        title = _TITLE.search(page)
        if title:
            parts = re.split(r"\s+[|\-–—:·]\s+", html.unescape(title.group(1)).strip())
            name = min((p for p in parts if p.strip()), key=len, default="")
    return [url for _, url in icons], clean_name(name)


# ---- network -----------------------------------------------------------------------------
def _assert_public(host: str) -> None:
    try:
        infos = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except OSError as error:
        raise FetchError(f"cannot resolve {host}") from error
    if not infos:
        raise FetchError(f"cannot resolve {host}")
    for info in infos:
        address = ipaddress.ip_address(info[4][0])
        if not address.is_global or address.is_multicast:
            raise FetchError(f"{host} resolves to a non-public address")


def _get(session, url: str, limit: int, *, truncate: bool = False) -> tuple[bytes, str, str]:
    """GET over HTTPS with per-hop address checks; returns (body, content type, final URL).
    With `truncate`, a long body is cut at `limit` instead of rejected (HTML heads)."""
    for _ in range(MAX_REDIRECTS + 1):
        parts = urlsplit(url)
        if parts.scheme != "https" or not parts.hostname or parts.username or parts.password:
            raise FetchError("only plain HTTPS URLs are fetched")
        if parts.port not in (None, 443):
            raise FetchError("non-standard ports are not fetched")
        _assert_public(parts.hostname)
        response = session.get(url, timeout=TIMEOUT, allow_redirects=False, stream=True,
                               headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
        try:
            if response.status_code in (301, 302, 303, 307, 308):
                url = urljoin(url, response.headers.get("Location", ""))
                continue
            if response.status_code != 200:
                raise FetchError(f"HTTP {response.status_code}")
            body = bytearray()
            for chunk in response.iter_content(16_384):
                body.extend(chunk)
                if len(body) > limit:
                    if truncate:
                        return bytes(body[:limit]), response.headers.get("Content-Type", ""), url
                    raise FetchError("response too large")
            return bytes(body), response.headers.get("Content-Type", ""), url
        finally:
            response.close()
    raise FetchError("too many redirects")


def sanitize_image(data: bytes) -> bytes:
    """Decodes untrusted bytes as a raster image and re-encodes a square PNG."""
    from PyQt6.QtCore import QBuffer, QByteArray, QIODevice, Qt
    from PyQt6.QtGui import QImage

    if not data or len(data) > MAX_CUSTOM:
        raise FetchError("image missing or too large")
    image = QImage()
    if not image.loadFromData(data) or image.isNull():
        raise FetchError("not a supported image")
    if image.width() < 16 or image.height() < 16 or image.width() > 4096 or image.height() > 4096:
        raise FetchError("unusable image size")
    image = image.convertToFormat(QImage.Format.Format_ARGB32).scaled(
        ICON_PX, ICON_PX, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    out = QByteArray()
    buffer = QBuffer(out)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    buffer.close()
    return bytes(out)


def fetch_site(host: str, session=None) -> tuple[bytes, str]:
    """Best icon (sanitized PNG) and site name for a host. Raises FetchError if none."""
    import requests

    session = session or requests.Session()
    session.trust_env = False
    session.cookies.clear()
    name = ""
    last_error: Exception = FetchError("no icon found")
    for candidate in candidate_hosts(host):
        base = f"https://{candidate}/"
        urls: list[str] = []
        try:
            page, kind, final = _get(session, base, MAX_HTML, truncate=True)
            if "html" in kind.lower():
                urls, found = parse_page(page.decode("utf-8", "replace"), final)
                name = name or found
        except FetchError as error:
            last_error = error
        urls += [urljoin(base, "/apple-touch-icon.png"), urljoin(base, "/favicon.ico")]
        for url in dict.fromkeys(urls[:6]):
            try:
                if url.startswith("data:image/"):
                    data = base64.b64decode(url.split(",", 1)[1][: MAX_IMAGE * 2], validate=False)
                else:
                    data, _, _ = _get(session, url, MAX_IMAGE)
                return sanitize_image(data), name
            except (FetchError, ValueError, OSError) as error:
                last_error = error
            except Exception as error:  # noqa: BLE001 - network library errors
                last_error = FetchError(type(error).__name__)
    raise FetchError(str(last_error))


# ---- encrypted cache ---------------------------------------------------------------------
class IconStore:
    """Encrypted icon PNGs and site metadata under ~/.config/icp/icons (0700/0600)."""

    def __init__(self, directory: Path | None = None, key: bytes | None = None):
        if directory is None or key is None:
            from .. import paths
            from ..auth.session import _master_key
            directory = directory or paths.vault_file().parent / "icons"
            key = key or _master_key()
        self.dir = Path(directory)
        self.dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(self.dir, 0o700)
        self._box = nacl.secret.SecretBox(key)
        self._name_key = hashlib.sha256(b"icp-icon-names" + key).digest()
        self._lock = threading.Lock()
        self._png: dict[str, bytes | None] = {}
        self.meta: dict[str, dict] = self._read_meta()

    def key_for(self, subject: str) -> str:
        return hmac.new(self._name_key, subject.encode(), hashlib.sha256).hexdigest()[:32]

    def _write(self, path: Path, data: bytes) -> None:
        tmp = path.with_suffix(".tmp")
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "wb") as handle:
            handle.write(self._box.encrypt(data))
        os.replace(tmp, path)

    def _read(self, path: Path) -> bytes | None:
        try:
            return self._box.decrypt(path.read_bytes())
        except (OSError, nacl.exceptions.CryptoError):
            return None

    def _read_meta(self) -> dict:
        raw = self._read(self.dir / "meta.bin")
        try:
            return json.loads(raw) if raw else {}
        except ValueError:
            return {}

    def _save_meta(self) -> None:
        self._write(self.dir / "meta.bin", json.dumps(self.meta).encode())

    def png(self, key: str) -> bytes | None:
        with self._lock:
            if key not in self._png:
                self._png[key] = self._read(self.dir / f"{key}.bin")
            return self._png[key]

    def put(self, key: str, png: bytes | None, *, name: str = "", custom: bool = False) -> None:
        with self._lock:
            entry = self.meta.get(key, {})
            if entry.get("custom") and not custom and png is not None:
                return  # never replace a user's own choice with a fetched icon
            if png is not None:
                self._write(self.dir / f"{key}.bin", png)
                self._png[key] = png
            entry.update({"ok": png is not None or entry.get("ok", False), "at": time.time(),
                          "custom": custom or entry.get("custom", False)})
            if name:
                entry["name"] = clean_name(name)
            entry["v"] = entry.get("v", 0) + 1
            self.meta[key] = entry
            self._save_meta()

    def remove(self, key: str) -> None:
        with self._lock:
            self._png.pop(key, None)
            try:
                (self.dir / f"{key}.bin").unlink()
            except OSError:
                pass
            if key in self.meta:
                self.meta[key] = {"ok": False, "at": 0, "v": self.meta[key].get("v", 0) + 1}
            self._save_meta()

    def clear(self) -> None:
        """Deletes every cached icon and name, custom ones included."""
        with self._lock:
            for path in self.dir.glob("*.bin"):
                try:
                    path.unlink()
                except OSError:
                    pass
            self._png.clear()
            self.meta = {}

    def needs_fetch(self, key: str) -> bool:
        entry = self.meta.get(key)
        if not entry:
            return True
        return not entry.get("ok") and not entry.get("custom") and time.time() - entry.get("at", 0) > RETRY_FAILED_AFTER
