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


class GlassControllerTests(unittest.TestCase):
    def test_confirm_prompt_names_the_device(self):
        bridge = IcpBridge("http://127.0.0.1:1")
        seen = []
        bridge.message.connect(lambda e: e["type"] == "prompt" and seen.append(e))
        bridge._status("Joining iCloud Keychain will use the passcode of: iPhone 15 (SERIAL1)")
        bridge._answers.put(True)
        self.assertTrue(bridge._confirm("Proceed? (y/N) "))
        self.assertIn("iPhone 15 (SERIAL1)", seen[0]["message"])

    def test_uuid_domains_are_not_shown_as_websites(self):
        class Cred:
            def __init__(self, domain, title):
                self.d = {"domain": domain, "title": title, "username": "", "password": "", "totp": ""}

            def public_dict(self):
                return dict(self.d)

        class Store:
            def all(self):
                return [Cred("0F3A9C12-7B4E-4D21-9E55-3C8A1B2D4E6F", "Home Router"), Cred("github.com", "")]

        items = credential_items(Store())
        self.assertEqual([(i["name"], i["site"]) for i in items], [("github.com", "github.com"), ("Home Router", "")])

    def test_debug_log_collapses_repeats_and_answer_validates_codes(self):
        from icp.gui.glass import Controller
        with mock.patch("icp.gui.bridge.IcpBridge.load_vault", return_value=[]):
            controller = Controller("http://127.0.0.1:1")
        controller._language = "en"
        controller._append_log("warning", "keyring unavailable")
        controller._append_log("warning", "keyring unavailable")
        self.assertEqual(controller.log[-1]["text"], "keyring unavailable  (×2)")
        controller._prompt = {"kind": "code", "message": "", "devices": []}
        with mock.patch.object(controller.bridge, "respond") as respond:
            controller.answer("12 34")
            respond.assert_not_called()
            self.assertIn("six digits", controller.error)
            controller.answer("123 456")
            respond.assert_called_once_with("code", "123456")


class SignInExperienceTests(unittest.TestCase):
    def test_known_failures_get_plain_explanations(self):
        from icp.gui.glass import friendly_error
        self.assertIn("Wait at least an hour", friendly_error("gsa: request status 429"))
        self.assertIn("HTTP 503", friendly_error("init request failed (HTTP 503)"))
        self.assertIn("incorrect", friendly_error("GSAError ec=-22406"))
        self.assertIn("127.0.0.1:6969", friendly_error("AnisetteError: connection refused", "http://127.0.0.1:6969"))
        self.assertEqual(friendly_error("something new"), "something new")

    def test_visible_rows_jump_the_icon_queue(self):
        from icp.gui.glass import Controller
        with mock.patch("icp.gui.bridge.IcpBridge.load_vault", return_value=[]):
            controller = Controller("http://127.0.0.1:1")
        controller._icon_thread = mock.Mock(is_alive=lambda: True)  # keep the worker idle
        controller._enqueue("a", "a.example", front=False)
        controller._enqueue("b", "b.example", front=False)
        controller._enqueue("b", "b.example", front=True)
        controller._enqueue("c", "c.example", front=True)
        self.assertEqual([key for key, _ in controller._icon_jobs], ["c", "b", "a"])


class WindowLoadTests(unittest.TestCase):
    def test_every_qml_file_loads(self):
        from PyQt6.QtCore import QUrl
        from PyQt6.QtQml import QQmlComponent
        from icp.gui.glass import QML_DIR, Controller, create_engine
        with mock.patch("icp.gui.bridge.IcpBridge.load_vault", return_value=[]):
            controller = Controller("http://127.0.0.1:1")
        engine = create_engine(controller)
        self.assertTrue(engine.rootObjects(), "Main.qml did not load")
        for path in sorted(QML_DIR.glob("*.qml")):
            component = QQmlComponent(engine, QUrl.fromLocalFile(str(path)))
            self.assertFalse(component.isError(), f"{path.name}: {component.errorString()}")
        for root in engine.rootObjects():
            root.deleteLater()


class ToolsTests(unittest.TestCase):
    def test_generated_passwords_follow_the_grouped_strong_format(self):
        from icp.gui.glass import generate_password
        seen = set()
        for _ in range(200):
            value = generate_password()
            self.assertEqual([len(group) for group in value.split("-")], [6, 6, 6])
            self.assertTrue(any(c.isupper() for c in value) and any(c.isdigit() for c in value))
            seen.add(value)
        self.assertEqual(len(seen), 200)

    def test_export_uses_apples_csv_columns_and_private_file_mode(self):
        import csv as csv_module
        import tempfile
        from icp.gui.glass import CSV_HEADER, Controller
        with mock.patch("icp.gui.bridge.IcpBridge.load_vault", return_value=[]):
            controller = Controller("http://127.0.0.1:1")
        controller._items = [{"display": "Example", "site": "example.com", "username": "alex",
                              "password": 'p,w"q', "notes": "line1\nline2", "totp": ""}]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "out.csv")
            self.assertTrue(controller.exportCsv(path))
            with open(path, newline="", encoding="utf-8") as handle:
                rows = list(csv_module.reader(handle))
            self.assertEqual(rows[0], CSV_HEADER)
            self.assertEqual(rows[1], ["Example", "https://example.com/", "alex", 'p,w"q', "line1\nline2", ""])
            self.assertEqual(oct(os.stat(path).st_mode & 0o777), "0o600")

    def test_sort_options_order_the_list(self):
        from icp.gui.glass import Controller
        with mock.patch("icp.gui.bridge.IcpBridge.load_vault", return_value=[]):
            controller = Controller("http://127.0.0.1:1")
            QApplication.processEvents()   # let the startup vault load run first
        controller._write_prefs = lambda: None
        controller._raw = [
            {"name": "b.com", "site": "b.com", "title": "", "mdat": 30, "cdat": 1},
            {"name": "a.com", "site": "a.com", "title": "", "mdat": 10, "cdat": 3},
            {"name": "c.com", "site": "c.com", "title": "", "mdat": 20, "cdat": 2},
        ]
        controller.setSort("website", False)
        QApplication.processEvents()
        self.assertEqual([i["name"] for i in controller.items], ["a.com", "b.com", "c.com"])
        controller.setSort("modified", True)
        QApplication.processEvents()
        self.assertEqual([i["name"] for i in controller.items], ["b.com", "c.com", "a.com"])
        controller.setSort("created", False)
        QApplication.processEvents()
        self.assertEqual([i["name"] for i in controller.items], ["b.com", "c.com", "a.com"])
