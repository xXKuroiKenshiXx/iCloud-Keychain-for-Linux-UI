import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PyQt6.QtWidgets import QApplication
except ImportError:  # the GUI is optional
    raise unittest.SkipTest("PyQt6 is not installed")

from icp.gui import icons, setup
from icp.gui.bridge import credential_items
from icp.gui.glass import wifi_payload

APP = QApplication.instance() or QApplication([])


class WifiTests(unittest.TestCase):
    def test_join_code_escapes_special_characters(self):
        self.assertEqual(wifi_payload("Home;Net", r'p:a"ss\ '.strip()), r'WIFI:T:WPA;S:Home\;Net;P:p\:a\"ss\\;;')
        self.assertEqual(wifi_payload("Cafe", ""), "WIFI:T:nopass;S:Cafe;;")

    def test_airport_items_are_networks_named_by_their_ssid(self):
        class Cred:
            def public_dict(self):
                return {"domain": "AirPort", "username": "Home-5G", "password": "secret", "title": ""}

        class Store:
            def all(self):
                return [Cred()]

        item = credential_items(Store())[0]
        self.assertTrue(item["wifi"])
        self.assertEqual((item["name"], item["site"]), ("Home-5G", ""))


class CacheAndContainerTests(unittest.TestCase):
    def test_clear_removes_every_cached_icon(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = icons.IconStore(Path(tmp), b"k" * 32)
            key = store.key_for("example.com")
            store.put(key, b"\x89PNG fake", name="Example")
            store.clear()
            self.assertEqual(list(Path(tmp).glob("*.bin")), [])
            self.assertIsNone(store.png(key))
            self.assertTrue(store.needs_fetch(key))

    def test_container_listens_only_locally_and_uses_the_pinned_image(self):
        with mock.patch("shutil.which", side_effect=lambda name: "/usr/bin/podman" if name == "podman" else None):
            cmd = setup.container_command()
        self.assertIn("127.0.0.1:6969:6969", cmd)
        self.assertTrue(cmd[-1].startswith("docker.io/dadoum/anisette-v3-server@sha256:"))


if __name__ == "__main__":
    unittest.main()
