import os
import socket
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PyQt6.QtCore import QBuffer, QByteArray, QIODevice
    from PyQt6.QtGui import QColor, QGuiApplication, QImage
except ImportError:  # the GUI is optional
    raise unittest.SkipTest("PyQt6 is not installed")

from icp.gui import icons

APP = QGuiApplication.instance() or QGuiApplication([])


def png_bytes(size=64) -> bytes:
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(QColor("#3366ff"))
    data = QByteArray()
    buffer = QBuffer(data)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(data)


class FakeResponse:
    def __init__(self, status=200, body=b"", headers=None):
        self.status_code = status
        self._body = body
        self.headers = headers or {}

    def iter_content(self, size):
        for i in range(0, len(self._body), size):
            yield self._body[i:i + size]

    def close(self):
        pass


class FakeSession:
    def __init__(self, routes):
        self.routes = routes
        self.requested = []
        self.trust_env = True
        self.cookies = mock.Mock()

    def get(self, url, **kwargs):
        self.requested.append(url)
        assert kwargs["allow_redirects"] is False
        return self.routes.get(url, FakeResponse(404))


def public_dns(host, port, type=0):
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port))]


class HostTests(unittest.TestCase):
    def test_normalize_rejects_ip_literals_and_uuid_domains(self):
        self.assertEqual(icons.normalize_host("https://www.GitHub.com/login"), "github.com")
        self.assertEqual(icons.normalize_host("127.0.0.1"), "")
        self.assertEqual(icons.normalize_host("7C1380EE-5010-4B03-BAE2-96BDC74C28E1"), "")
        self.assertEqual(icons.candidate_hosts("digital.bank.ar"), ["digital.bank.ar", "www.digital.bank.ar", "bank.ar"])

    def test_private_addresses_are_never_fetched(self):
        private = lambda host, port, type=0: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.168.1.10", port))]
        session = FakeSession({})
        with mock.patch("socket.getaddrinfo", private):
            with self.assertRaises(icons.FetchError):
                icons._get(session, "https://router.example/", 1000)
        self.assertEqual(session.requested, [])

    def test_redirect_to_plain_http_or_private_host_is_refused(self):
        session = FakeSession({"https://a.example/": FakeResponse(302, headers={"Location": "http://a.example/x"})})
        with mock.patch("socket.getaddrinfo", public_dns):
            with self.assertRaises(icons.FetchError):
                icons._get(session, "https://a.example/", 1000)

    def test_oversized_response_is_cut_off(self):
        session = FakeSession({"https://a.example/": FakeResponse(200, b"x" * 5000)})
        with mock.patch("socket.getaddrinfo", public_dns):
            with self.assertRaises(icons.FetchError):
                icons._get(session, "https://a.example/", 1000)


class PageTests(unittest.TestCase):
    def test_parse_prefers_touch_icon_and_site_name(self):
        page = """<html><head><title>Login | Banco Entre Ríos</title>
        <meta property="og:site_name" content="Banco Entre R&iacute;os">
        <link rel="icon" href="/fav-16.png" sizes="16x16">
        <link rel="apple-touch-icon" href="/touch.png" sizes="180x180">
        <link rel="icon" type="image/svg+xml" href="/logo.svg"></head></html>"""
        urls, name = icons.parse_page(page, "https://bank.ar/")
        self.assertEqual(urls[0], "https://bank.ar/touch.png")
        self.assertNotIn("https://bank.ar/logo.svg", urls)
        self.assertEqual(name, "Banco Entre Ríos")

    def test_name_is_stripped_of_control_and_bidi_characters(self):
        self.assertEqual(icons.clean_name("Pay‮Pal\x00 <b>"), "PayPal <b>")

    def test_fetch_site_returns_sanitized_png_and_name(self):
        routes = {
            "https://shop.example/": FakeResponse(200, b'<title>Shop</title><link rel="icon" href="/i.png">',
                                                  {"Content-Type": "text/html"}),
            "https://shop.example/i.png": FakeResponse(200, png_bytes(), {"Content-Type": "image/png"}),
        }
        with mock.patch("socket.getaddrinfo", public_dns):
            png, name = icons.fetch_site("shop.example", session=FakeSession(routes))
        self.assertTrue(png.startswith(b"\x89PNG"))
        self.assertEqual(name, "Shop")


class ImageTests(unittest.TestCase):
    def test_non_images_are_rejected(self):
        with self.assertRaises(icons.FetchError):
            icons.sanitize_image(b"<script>alert(1)</script>")

    def test_images_are_reencoded_small(self):
        out = icons.sanitize_image(png_bytes(512))
        image = QImage.fromData(out)
        self.assertEqual((image.width(), image.height()), (128, 128))


class StoreTests(unittest.TestCase):
    def test_cache_is_encrypted_and_file_names_hide_the_site(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = icons.IconStore(Path(tmp), b"k" * 32)
            key = store.key_for("bank.ar")
            store.put(key, png_bytes(), name="Bank")
            names = " ".join(p.name for p in Path(tmp).iterdir())
            self.assertNotIn("bank", names)
            self.assertNotIn(b"PNG", (Path(tmp) / f"{key}.bin").read_bytes()[:64])
            reopened = icons.IconStore(Path(tmp), b"k" * 32)
            self.assertTrue(reopened.png(key).startswith(b"\x89PNG"))
            self.assertEqual(reopened.meta[key]["name"], "Bank")
            self.assertEqual(oct(os.stat(Path(tmp) / f"{key}.bin").st_mode & 0o777), "0o600")

    def test_fetched_icon_never_replaces_a_custom_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = icons.IconStore(Path(tmp), b"k" * 32)
            key = store.key_for("bank.ar")
            custom = icons.sanitize_image(png_bytes(40))
            store.put(key, custom, custom=True)
            store.put(key, png_bytes(), name="Fetched")
            self.assertEqual(store.png(key), custom)
            self.assertFalse(store.needs_fetch(key))


if __name__ == "__main__":
    unittest.main()
