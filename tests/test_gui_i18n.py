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
        self.assertEqual(i18n.translate("Sign In", "ru"), "Войти")
        self.assertEqual(i18n.translate("Sign In", "zh"), "登录")
        self.assertEqual(i18n.translate("Sign In", "ko"), "Sign In")
        self.assertEqual(i18n.translate("Some new text", "es"), "Some new text")

    def test_unsupported_system_language_means_english(self):
        with mock.patch.object(QLocale, "system", return_value=QLocale("ko_KR")):
            self.assertEqual(i18n.system_language(), "en")
            self.assertEqual(i18n.resolve("system"), "en")
        with mock.patch.object(QLocale, "system", return_value=QLocale("es_AR")):
            self.assertEqual(i18n.resolve("system"), "es")
            self.assertEqual(i18n.resolve("de"), "de")

    def test_every_interface_string_is_translated_in_every_language(self):
        used = set()
        for path in QML.glob("*.qml"):
            used |= set(re.findall(r'icp\.tr\("([^"]*)"', path.read_text(encoding="utf-8")))
        setup = (QML / "SetupCard.qml").read_text(encoding="utf-8")
        used |= set(re.findall(r'tt\("([^"]+)"\)', setup))
        used |= set(re.findall(r'label: "([^"]+)"', setup))
        used |= set(re.findall(r'^\s+"\w+": "([^"]+)"', setup, re.M))
        used |= {"All", "Codes", "Wi-Fi", "Account", "Code", "Device", "Passcode", "Website", "Title",
                 "Date Edited", "Date Created", "Full", "Compact", "Hidden"}
        missing = sorted(text for text in used if text not in i18n._T)
        self.assertEqual(missing, [])
        for text, row in i18n._T.items():
            self.assertEqual(len(row), len(i18n._ORDER), text)
            self.assertTrue(all(part.strip() for part in row), text)
            for translated in row:
                self.assertEqual(set(re.findall(r"\{\w+\}", text)), set(re.findall(r"\{\w+\}", translated)), text)


if __name__ == "__main__":
    unittest.main()


class EngineMessageTests(unittest.TestCase):
    def test_engine_messages_are_shown_in_the_chosen_language(self):
        self.assertEqual(i18n.translate_engine("Already joined; syncing...", "es"), "Ya estás unido; sincronizando…")
        self.assertEqual(i18n.translate_engine("Synced 42 credential(s) into the vault.", "de"), "42 Passwörter entschlüsselt.")
        self.assertEqual(i18n.translate_engine("Joining iCloud Keychain will use the passcode of: iPhone (A1)", "en"),
                         "You'll need the passcode of iPhone (A1).")
        self.assertEqual(i18n.translate_engine("sign-in failed: HTTP 500", "fr"), "Échec de la connexion : HTTP 500")
        self.assertEqual(i18n.translate_engine("something unexpected", "es"), "something unexpected")
