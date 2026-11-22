#!/usr/bin/env python3
"""Qt 6 window for icp: sign-in, keychain join, and the password vault."""

from __future__ import annotations

import argparse
import os
import re
import sys

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QApplication, QFrame, QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QMessageBox, QPushButton, QScrollArea,
    QStackedWidget, QVBoxLayout, QWidget,
)

from .bridge import IcpBridge

STYLE = """
QWidget { color: #eef4fc; background: transparent; font: 14px 'Noto Sans'; }
QMainWindow, QWidget#root { background: qradialgradient(cx:0.72, cy:0.14, radius:1.1,
    stop:0 #172b3f, stop:0.44 #101c2b, stop:1 #09111c); }
QFrame#rail { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
    stop:0 rgba(23,42,60,228), stop:1 rgba(12,25,40,242));
    border-right: 1px solid rgba(185,222,255,55); }
QFrame#glass { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
    stop:0 rgba(111,157,190,128), stop:0.08 rgba(52,84,114,169),
    stop:0.57 rgba(31,55,81,194), stop:1 rgba(20,38,61,210));
    border: 1px solid rgba(205,232,252,115); border-radius: 18px; }
QFrame#soft { background: rgba(30, 48, 68, 180); border: 1px solid rgba(169,206,234,76);
               border-radius: 14px; }
QLabel#brand { color: #f4f8fe; font: 700 20px 'Noto Sans'; }
QLabel#title { color: #f4f8fe; font: 700 30px 'Noto Sans'; }
QLabel#section { color: #ecf4ff; font: 600 17px 'Noto Sans'; }
QLabel#body { color: #aec2d8; font: 13px 'Noto Sans'; }
QLabel#eyebrow { color: #8dbde7; font: 600 11px 'Noto Sans'; }
QPushButton { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
    stop:0 rgba(95,131,161,176), stop:0.12 rgba(55,84,114,218), stop:1 rgba(35,62,89,235));
    border: 1px solid rgba(192,225,249,120); border-radius: 11px;
              padding: 10px 15px; color: #eef5fe; font-weight: 600; }
QPushButton:hover { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
    stop:0 rgba(131,174,205,210), stop:0.17 rgba(70,112,151,230), stop:1 rgba(44,80,112,245));
    border-color: #b5defc; }
QPushButton:pressed { background: #1a3049; }
QPushButton:disabled { background: #1b2a3b; border-color: #2c4056; color: #72889f; }
QPushButton#primary { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
    stop:0 #f5fbff, stop:0.3 #d7ecff, stop:1 #abd1f3);
    color: #172a3f; border-color: #ffffff; }
QPushButton#primary:hover { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
    stop:0 #ffffff, stop:0.3 #ebf7ff, stop:1 #c3e1fa); }
QPushButton#nav { background: transparent; border: 1px solid transparent;
                  text-align: left; padding: 12px 15px; color: #aac0d6; }
QPushButton#nav:hover { background: #1b2e44; }
QPushButton#nav[active="true"] { background: #263e59; border-color: #547b9f;
                                  color: #f4f9ff; }
QLineEdit { background: #101d2d; border: 1px solid #486782; border-radius: 10px;
            color: #f5f9ff; padding: 11px 13px; selection-background-color: #5a89b5; }
QLineEdit:focus { border-color: #b0d9fa; }
QListWidget { background: rgba(13,28,45,172); border: 1px solid rgba(173,215,248,96);
    border-radius: 14px; padding: 9px; outline: none; }
QListWidget::item { padding: 12px 14px; border-radius: 9px; }
QListWidget::item:hover { background: rgba(110,161,203,74); }
QListWidget::item:selected { background: rgba(125,179,221,112); color: #ffffff; }
QScrollArea { border: none; }
"""


class GlassButton(QPushButton):
    def __init__(self, text: str):
        super().__init__(text)
        self.setObjectName("primary")
        effect = QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(15)
        effect.setOffset(0, 5)
        effect.setColor(QColor(82, 148, 201, 95))
        self.setGraphicsEffect(effect)
        self._glow = QPropertyAnimation(effect, b"blurRadius", self)
        self._glow.setDuration(190)
        self._glow.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _animate_glow(self, target: int) -> None:
        if os.environ.get("ICP_REDUCED_MOTION") == "1":
            return
        self._glow.stop()
        self._glow.setStartValue(self.graphicsEffect().blurRadius())
        self._glow.setEndValue(target)
        self._glow.start()

    def enterEvent(self, event) -> None:
        self._animate_glow(27)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._animate_glow(15)
        super().leaveEvent(event)


def label(text: str, role: str, *, wrap: bool = False) -> QLabel:
    widget = QLabel(text)
    widget.setObjectName(role)
    widget.setWordWrap(wrap)
    return widget


def validated_response(kind: str, value: str, methods: set[str]) -> str:
    if kind in {"password", "passcode"}:
        if not value:
            raise ValueError("This field cannot be empty")
        return value
    if kind in {"username", "text"}:
        return value.strip()
    if kind == "code":
        code = re.sub(r"[\s-]", "", value)
        if not re.fullmatch(r"[0-9]{6}", code):
            raise ValueError("Enter exactly six digits")
        return code
    if kind in {"method", "device"}:
        method = value.strip()
        if method not in methods:
            raise ValueError("Choose one of the numbers shown")
        return method
    raise ValueError("No active prompt")


class Window(QMainWindow):
    def __init__(self, anisette_url: str | None, smoke: bool):
        super().__init__()
        self.setWindowTitle("iCloud Keychain")
        self.resize(1120, 740)
        self.setMinimumSize(850, 600)
        self.bridge = IcpBridge(anisette_url)
        self.bridge.message.connect(self.on_event)
        self.bridge.finished.connect(self.on_finished)
        self.active_prompt = ""
        self.offered_choices: set[str] = set()
        self.passwords: list[dict] = []
        self._pending_passwords: list[dict] | None = None
        self._had_error = False
        self._revealed = False
        self._animation = None

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        shell = QHBoxLayout(root)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(0)

        rail = QFrame()
        rail.setObjectName("rail")
        rail.setFixedWidth(224)
        rail_layout = QVBoxLayout(rail)
        rail_layout.setContentsMargins(20, 30, 20, 24)
        rail_layout.setSpacing(10)
        rail_layout.addWidget(label("iCloud Keychain", "brand"))
        rail_layout.addSpacing(28)
        self.nav = []
        for text, index in (("All passwords", 0), ("Apple Account", 1), ("Settings", 2)):
            button = QPushButton(text)
            button.setObjectName("nav")
            button.setProperty("active", False)
            button.clicked.connect(lambda _=False, i=index: self.show_page(i))
            rail_layout.addWidget(button)
            self.nav.append(button)
        rail_layout.addStretch()
        rail_layout.addWidget(label("Linux · Wayland", "eyebrow"))
        rail_layout.addWidget(label("Private keychain client", "body"))
        shell.addWidget(rail)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(36, 24, 36, 28)
        content_layout.setSpacing(24)
        top = QHBoxLayout()
        top.addWidget(label("Private by design", "eyebrow"))
        top.addStretch()
        self.status = label("Not connected", "body")
        top.addWidget(self.status)
        content_layout.addLayout(top)
        self.pages = QStackedWidget()
        content_layout.addWidget(self.pages, 1)
        shell.addWidget(content, 1)

        self.pages.addWidget(self._vault_page())
        self.pages.addWidget(self._account_page())
        self.pages.addWidget(self._settings_page())
        self.show_page(0)
        self.load_saved_vault()
        if smoke:
            QTimer.singleShot(2500, QApplication.instance().quit)

    def _glass(self, title: str, body: str) -> QFrame:
        card = QFrame()
        card.setObjectName("glass")
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(34)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(2, 10, 20, 155))
        card.setGraphicsEffect(shadow)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 26, 28, 28)
        layout.setSpacing(12)
        layout.addWidget(label(title, "section"))
        layout.addWidget(label(body, "body", wrap=True))
        return card

    def _vault_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.addWidget(label("Passwords", "title"))
        layout.addWidget(label("Your iCloud Keychain on this computer", "body"))
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search passwords")
        self.search.setEnabled(False)
        self.search.textChanged.connect(self.filter_passwords)
        layout.addWidget(self.search)
        empty = self._glass(
            "Keychain is locked",
            "No passwords are available yet. Apple Account sign-in alone does not unlock "
            "end-to-end encrypted keychain records; device approval and recovery must be verified.",
        )
        empty.setMinimumSize(550, 190)
        empty.setMaximumWidth(640)
        self.empty_card = empty
        self.empty_title = empty.layout().itemAt(0).widget()
        self.empty_body = empty.layout().itemAt(1).widget()
        layout.addWidget(empty, 0, Qt.AlignmentFlag.AlignHCenter)
        self.open_account = GlassButton("Open Apple Account")
        self.open_account.clicked.connect(lambda: self.show_page(1))
        layout.addWidget(self.open_account, 0, Qt.AlignmentFlag.AlignHCenter)
        self.sync_button = QPushButton("Sync now")
        self.sync_button.clicked.connect(self.start_sync)
        self.sync_button.setVisible(False)
        layout.addWidget(self.sync_button, 0, Qt.AlignmentFlag.AlignRight)
        self.vault_list = QListWidget()
        self.vault_list.setVisible(False)
        self.vault_list.currentRowChanged.connect(self.show_password_details)
        layout.addWidget(self.vault_list, 1)
        self.detail_card = QFrame()
        self.detail_card.setObjectName("glass")
        detail_layout = QVBoxLayout(self.detail_card)
        detail_layout.setContentsMargins(24, 20, 24, 20)
        self.detail_title = label("Select a password", "section")
        self.detail_username = label("", "body")
        self.secret_label = label("", "body")
        self.totp_label = label("", "body")
        self.secret_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        detail_layout.addWidget(self.detail_title)
        detail_layout.addWidget(self.detail_username)
        detail_layout.addWidget(self.secret_label)
        detail_layout.addWidget(self.totp_label)
        reveal_actions = QHBoxLayout()
        self.reveal_button = QPushButton("Reveal password")
        self.reveal_button.clicked.connect(self.toggle_reveal)
        self.copy_button = QPushButton("Copy password")
        self.copy_button.clicked.connect(self.copy_password)
        reveal_actions.addWidget(self.reveal_button)
        reveal_actions.addWidget(self.copy_button)
        reveal_actions.addStretch()
        detail_layout.addLayout(reveal_actions)
        self.detail_card.setVisible(False)
        layout.addWidget(self.detail_card)
        layout.addStretch()
        return page

    def _account_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(18)
        layout.addWidget(label("Apple Account", "title"))
        layout.addWidget(label("Connect this Linux device and unlock your own iCloud Keychain.", "body"))
        card = self._glass("Sign in", "This computer joins your iCloud Keychain as a new device. Your password, "
                           "verification code and device passcode are only used in this process. "
                           "The device passcode step spends one of about ten recovery attempts.")
        form = card.layout()
        self.email = QLineEdit()
        self.email.setPlaceholderText("Apple Account email")
        self.email.setInputMethodHints(Qt.InputMethodHint.ImhEmailCharactersOnly)
        form.addWidget(self.email)
        self.sign_in = GlassButton("Connect and load passwords")
        self.sign_in.clicked.connect(self.start_login)
        form.addWidget(self.sign_in, 0, Qt.AlignmentFlag.AlignLeft)
        self.prompt_hint = label("Waiting for sign-in", "body")
        form.addWidget(self.prompt_hint)
        self.answer = QLineEdit()
        self.answer.setPlaceholderText("Apple verification response")
        self.answer.setEnabled(False)
        self.answer.returnPressed.connect(self.respond)
        form.addWidget(self.answer)
        self.continue_button = QPushButton("Continue")
        self.continue_button.setEnabled(False)
        self.continue_button.clicked.connect(self.respond)
        form.addWidget(self.continue_button, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(card)
        actions = QHBoxLayout()
        self.check_button = QPushButton("Try again")
        self.check_button.clicked.connect(self.start_login)
        actions.addWidget(self.check_button)
        self.cancel_button = QPushButton("Cancel operation")
        self.cancel_button.clicked.connect(self.bridge.cancel)
        actions.addWidget(self.cancel_button)
        actions.addStretch()
        layout.addLayout(actions)
        self.activity = label("No operation running", "body", wrap=True)
        self.activity.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.activity)
        layout.addStretch()
        return page

    def _settings_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(18)
        layout.addWidget(label("Settings", "title"))
        layout.addWidget(label("Data directory", "section"))
        layout.addWidget(label(str(_data_dir()), "body", wrap=True))
        layout.addWidget(label("Anisette service", "section"))
        layout.addWidget(label(self.bridge.anisette_url, "body", wrap=True))
        layout.addStretch()
        return page

    def show_page(self, index: int) -> None:
        self.pages.setCurrentIndex(index)
        for i, button in enumerate(self.nav):
            button.setProperty("active", i == index)
            button.style().unpolish(button)
            button.style().polish(button)
        if not self.isVisible() or os.environ.get("ICP_REDUCED_MOTION") == "1":
            return
        page = self.pages.currentWidget()
        effect = QGraphicsOpacityEffect(page)
        page.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity", self)
        animation.setDuration(180)
        animation.setStartValue(0.75)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.finished.connect(lambda: page.setGraphicsEffect(None))
        self._animation = animation
        animation.start()

    def load_saved_vault(self) -> None:
        try:
            items = self.bridge.load_vault()
        except Exception as error:  # noqa: BLE001 - a missing engine or keyring leaves the vault locked
            self.activity.setText(f"Saved vault unavailable: {error}")
            return
        if items:
            self.load_passwords(items)
            self.status.setText("Vault unlocked")

    def start_sync(self) -> None:
        if self.bridge.busy:
            return
        self._had_error = False
        self._pending_passwords = None
        self.status.setText("Syncing…")
        self.bridge.sync()

    def start_login(self) -> None:
        if self.bridge.busy:
            return
        if not self.email.text().strip():
            QMessageBox.warning(self, "Apple Account required", "Enter your Apple Account email address first.")
            return
        self.on_prompt("password", "Enter your Apple Account password", [])
        self.show_page(1)

    def on_prompt(self, kind: str, message: str, devices: list[dict]) -> None:
        self.show_page(1)
        if kind == "confirm":
            reply = QMessageBox.question(
                self, "Join iCloud Keychain", f"{self.activity.text()}\n\n{message}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            self.bridge.respond("confirm", reply == QMessageBox.StandardButton.Yes)
            return
        self.active_prompt = kind
        self.answer.setEnabled(True)
        self.continue_button.setEnabled(True)
        self.prompt_hint.setText(message)
        self.offered_choices = {str(item.get("index")) for item in devices}
        if kind == "password":
            self.answer.setEchoMode(QLineEdit.EchoMode.Password)
            self.answer.setPlaceholderText("Password")
        elif kind == "device":
            self.answer.setEchoMode(QLineEdit.EchoMode.Normal)
            self.answer.setPlaceholderText("Device number")
            self.activity.setText("\n".join(f"{item.get('index')}: {item.get('name') or item.get('model') or 'Trusted device'}" for item in devices))
        elif kind == "passcode":
            self.answer.setEchoMode(QLineEdit.EchoMode.Password)
            self.answer.setPlaceholderText("Device unlock passcode")
        elif kind in {"username", "text"}:
            self.answer.setEchoMode(QLineEdit.EchoMode.Normal)
            self.answer.setPlaceholderText("Answer")
        else:
            self.answer.setEchoMode(QLineEdit.EchoMode.Password)
            self.answer.setPlaceholderText("Six-digit code")
        self.answer.setFocus()

    def respond(self) -> None:
        if not self.active_prompt:
            return
        try:
            value = validated_response(self.active_prompt, self.answer.text(), self.offered_choices)
        except ValueError as error:
            self.prompt_hint.setText(str(error))
            return
        try:
            if self.active_prompt == "password":
                self.bridge.start(self.email.text().strip(), value)
                self.status.setText("Connecting…")
                self._had_error = False
                self._pending_passwords = None
                self.load_passwords([])
            else:
                self.bridge.respond(self.active_prompt, value)
                self.status.setText("Working…")
        except (OSError, RuntimeError, ValueError) as error:
            QMessageBox.warning(self, "Prompt expired", str(error))
        finally:
            self.answer.clear()
            self.answer.setEnabled(False)
            self.continue_button.setEnabled(False)
            self.active_prompt = ""

    def on_event(self, event: dict) -> None:
        kind = event.get("type")
        if kind == "status":
            self.status.setText(str(event.get("message", "Working…")))
            self.activity.setText(str(event.get("message", "")))
        elif kind == "prompt":
            self.on_prompt(str(event.get("kind", "")), str(event.get("message", "")), event.get("devices") or [])
        elif kind == "passwords":
            items = event.get("items")
            if not isinstance(items, list):
                self._had_error = True
                self.activity.setText("Invalid password response from local bridge")
                return
            self._pending_passwords = items
            self.activity.setText(f"Decrypted {len(items)} passwords.")
        elif kind == "error":
            self._had_error = True
            self.status.setText("Could not open keychain")
            self.prompt_hint.setText("Stopped")
            self.activity.setText(str(event.get("message", "An unknown error occurred"))[:500])

    def load_passwords(self, items: list[dict]) -> None:
        self.passwords = [item for item in items if isinstance(item, dict) and not item.get("deleted")]
        self.vault_list.clear()
        for index, item in enumerate(self.passwords):
            title = str(item.get("name") or item.get("domain") or "Untitled password")
            row = QListWidgetItem(f"{title}    ·    {item.get('username', '')}")
            row.setData(Qt.ItemDataRole.UserRole, index)
            self.vault_list.addItem(row)
        has_items = bool(self.passwords)
        self.search.setEnabled(has_items)
        self.vault_list.setVisible(has_items)
        self.empty_card.setVisible(not has_items)
        self.open_account.setVisible(not has_items)
        self.sync_button.setVisible(has_items or self.bridge.signed_in())
        self.detail_card.setVisible(False)
        if not has_items:
            self.empty_title.setText("No passwords found")
            self.empty_body.setText("The keychain request completed, but no active website passwords were returned.")

    def filter_passwords(self, query: str) -> None:
        needle = query.casefold()
        for row in range(self.vault_list.count()):
            item = self.vault_list.item(row)
            item.setHidden(needle not in item.text().casefold())

    def _selected_password(self) -> dict | None:
        item = self.vault_list.currentItem()
        if item is None:
            return None
        index = item.data(Qt.ItemDataRole.UserRole)
        return self.passwords[index] if isinstance(index, int) and 0 <= index < len(self.passwords) else None

    def show_password_details(self, _row: int) -> None:
        entry = self._selected_password()
        self.detail_card.setVisible(entry is not None)
        if entry is None:
            return
        self.detail_title.setText(str(entry.get("name") or entry.get("domain") or "Password"))
        self.detail_username.setText(f"{entry.get('domain', '')}    ·    {entry.get('username', '')}")
        self.totp_label.setText(self._totp_text(str(entry.get("totp") or "")))
        self.hide_secret()

    @staticmethod
    def _totp_text(uri: str) -> str:
        if not uri:
            return ""
        try:
            from icp.totp import generate
            current = generate(uri) or {}
        except Exception:  # noqa: BLE001 - a malformed TOTP never blocks the password view
            return ""
        return f"Verification code: {current.get('code', '')}" if current.get("code") else ""

    def hide_secret(self) -> None:
        self._revealed = False
        self.secret_label.setText("••••••••")
        self.reveal_button.setText("Reveal password")

    def toggle_reveal(self) -> None:
        entry = self._selected_password()
        if entry is None:
            return
        if self._revealed:
            self.hide_secret()
            return
        self._revealed = True
        self.secret_label.setText(str(entry.get("password", "")))
        self.reveal_button.setText("Hide password")
        QTimer.singleShot(20000, self.hide_secret)

    def copy_password(self) -> None:
        entry = self._selected_password()
        if entry is None:
            return
        secret = str(entry.get("password", ""))
        clipboard = QApplication.clipboard()
        clipboard.setText(secret)
        QTimer.singleShot(30000, lambda: clipboard.clear() if clipboard.text() == secret else None)

    def on_finished(self, code: int) -> None:
        self.answer.clear()
        self.answer.setEnabled(False)
        self.continue_button.setEnabled(False)
        self.active_prompt = ""
        if code == 0 and self._pending_passwords is not None:
            self.load_passwords(self._pending_passwords)
            self.status.setText("Vault unlocked" if self.passwords else "Keychain query completed")
            self.prompt_hint.setText("Read-only retrieval complete")
            self.show_page(0)
        elif not self._had_error:
            self.status.setText("Operation stopped")
            self.prompt_hint.setText(f"The keychain operation did not complete (exit {code}).")
        self._pending_passwords = None

    def closeEvent(self, event) -> None:
        self.bridge.cancel()
        super().closeEvent(event)


def _data_dir():
    from .. import paths
    return paths.vault_file().parent


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--anisette", help="anisette service URL (default: $ICP_ANISETTE_URL "
                        "or http://127.0.0.1:6969)")
    parser.add_argument("--smoke-test", action="store_true")
    args = parser.parse_args(argv)
    app = QApplication(sys.argv[:1])
    app.setApplicationName("iCloud Keychain")
    app.setStyleSheet(STYLE)
    font = QFont("Noto Sans", 10)
    app.setFont(font)
    window = Window(args.anisette, args.smoke_test)
    window.show()
    print(f"QT_PLATFORM={app.platformName()}", flush=True)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
