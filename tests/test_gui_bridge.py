import os
import unittest
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PyQt6.QtCore import QEventLoop, QTimer
except ImportError:  # the GUI is optional
    raise unittest.SkipTest("PyQt6 is not installed")
from PyQt6.QtWidgets import QApplication

from icp.gui.bridge import IcpBridge, classify_prompt, credential_items
from icp.gui.window import validated_response

APP = QApplication.instance() or QApplication([])


def fake_login(args):
    """Stands in for icp's cmd_login, using the same ui prompts in the same order."""
    from icp.cli import ui
    username = args.username or ui.ask("Apple ID: ")
    password = ui.secret("Password: ")
    ui.step("A 2FA code was sent to your trusted Apple devices.")
    code = ui.ask("6-digit code: ")
    ui.step("Multiple escrow bottles found. Pick the device you want to use:\n")
    ui.step("  1)  iPhone 15 (SERIAL1)")
    ui.step("  2)  MacBook Air (SERIAL2)")
    choice = ui.ask("Select 1-2 (blank to abort): ")
    if not ui.confirm_yn("Proceed? (y/N) "):
        return 0
    passcode = ui.secret("Device passcode / iCloud Security Code for that device: ")
    fake_login.seen = (username, password, code, choice, passcode)
    ui.out("Joined the keychain. Synced 1 credential(s).")
    return 0


class FakeCredential:
    def public_dict(self):
        return {"domain": "example.com", "username": "me", "password": " p w ", "title": "",
                "totp": "", "group": ""}


class FakeStore:
    def all(self):
        return [FakeCredential()]


class PromptTests(unittest.TestCase):
    def test_prompt_kinds_follow_icp_prompt_texts(self):
        self.assertEqual(classify_prompt("Apple ID: ", False), "username")
        self.assertEqual(classify_prompt("Password: ", True), "password")
        self.assertEqual(classify_prompt("6-digit code: ", False), "code")
        self.assertEqual(classify_prompt("Select 1-3 (blank to abort): ", False), "device")
        self.assertEqual(classify_prompt("Device passcode / iCloud Security Code for that device: ", True),
                         "passcode")

    def test_password_keeps_spaces_and_code_accepts_grouping(self):
        self.assertEqual(validated_response("password", " a b ", set()), " a b ")
        self.assertEqual(validated_response("code", "123 456", set()), "123456")
        with self.assertRaises(ValueError):
            validated_response("device", "3", {"1", "2"})

    def test_credential_items_name_falls_back_to_domain(self):
        self.assertEqual(credential_items(FakeStore())[0]["name"], "example.com")


class BridgeFlowTests(unittest.TestCase):
    def test_login_answers_every_prompt_from_the_window_and_restores_ui(self):
        from icp.cli import ui
        original_ask = ui.ask
        bridge = IcpBridge("http://127.0.0.1:1")
        prompts, statuses, codes = [], [], []
        answers = {"code": "123456", "device": "2", "confirm": True, "passcode": "000000"}

        def on_message(event):
            if event["type"] == "prompt":
                prompts.append(event)
                QTimer.singleShot(0, lambda: bridge.respond(event["kind"], answers[event["kind"]]))
            elif event["type"] == "status":
                statuses.append(event["message"])

        bridge.message.connect(on_message)
        loop = QEventLoop()
        bridge.finished.connect(lambda code: (codes.append(code), loop.quit()))
        with mock.patch("icp.cli.app.cmd_login", fake_login), \
                mock.patch("icp.vault.store.load_vault", return_value=FakeStore()):
            bridge.start("me@example.com", " secret ")
            QTimer.singleShot(5000, loop.quit)
            loop.exec()

        self.assertEqual(codes, [0])
        self.assertEqual([p["kind"] for p in prompts], ["code", "device", "confirm", "passcode"])
        self.assertEqual([d["index"] for d in prompts[1]["devices"]], ["1", "2"])
        self.assertEqual(fake_login.seen, ("me@example.com", " secret ", "123456", "2", "000000"))
        self.assertIn("Joined the keychain. Synced 1 credential(s).", statuses)
        self.assertIs(ui.ask, original_ask)

    def test_cancel_stops_a_waiting_prompt(self):
        bridge = IcpBridge("http://127.0.0.1:1")
        errors, codes = [], []
        bridge.message.connect(lambda e: e["type"] == "prompt" and QTimer.singleShot(0, bridge.cancel))
        bridge.message.connect(lambda e: e["type"] == "error" and errors.append(e["message"]))
        loop = QEventLoop()
        bridge.finished.connect(lambda code: (codes.append(code), loop.quit()))
        with mock.patch("icp.cli.app.cmd_login", fake_login):
            bridge.start("me@example.com", "pw")
            QTimer.singleShot(5000, loop.quit)
            loop.exec()
        self.assertEqual(codes, [1])
        self.assertEqual(errors, ["Operation cancelled"])


if __name__ == "__main__":
    unittest.main()
