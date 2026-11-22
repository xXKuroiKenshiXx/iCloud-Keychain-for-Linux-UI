import os
import re
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PyQt6.QtCore import QLocale
except ImportError:  # the GUI is optional
    raise unittest.SkipTest("PyQt6 is not installed")

from icp.gui import i18n

QML = Path(__file__).resolve().parents[1] / "icp" / "gui" / "qml"


class LanguageTests(unittest.TestCase):
    def test_translates_and_falls_back_to_english(self):
        self.assertEqual(i18n.translate("Sign In", "es"), "Iniciar sesión")
        self.assertEqual(i18n.translate("Sign In", "en"), "Sign In")
        self.assertEqual(i18n.translate("Sign In", "ru"), "Sign In")
        self.assertEqual(i18n.translate("Some new text", "es"), "Some new text")

    def test_unsupported_system_language_means_english(self):
        with mock.patch.object(QLocale, "system", return_value=QLocale("ru_RU")):
            self.assertEqual(i18n.system_language(), "en")
            self.assertEqual(i18n.resolve("system"), "en")
        with mock.patch.object(QLocale, "system", return_value=QLocale("es_AR")):
            self.assertEqual(i18n.resolve("system"), "es")
            self.assertEqual(i18n.resolve("de"), "de")

    def test_every_interface_string_is_translated_in_every_language(self):
        used = set()
        for path in QML.glob("*.qml"):
            used |= set(re.findall(r'icp\.tr\("([^"]*)"', path.read_text(encoding="utf-8")))
        used |= {"All", "Codes", "Wi-Fi", "Account", "Code", "Device", "Passcode"}
        missing = sorted(text for text in used if text not in i18n._T)
        self.assertEqual(missing, [])
        for text, row in i18n._T.items():
            self.assertEqual(len(row), 5, text)
            for translated in row:
                self.assertEqual(set(re.findall(r"\{\w+\}", text)), set(re.findall(r"\{\w+\}", translated)), text)


if __name__ == "__main__":
    unittest.main()
