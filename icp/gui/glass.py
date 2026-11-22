"""Liquid Glass window (Qt Quick). `Controller` exposes the IcpBridge to QML: the sign-in
flow, the vault, verification codes, and a live debug log of everything the engine does."""

from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from pathlib import Path

from PyQt6.QtCore import QObject, QTimer, QUrl, pyqtProperty, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QGuiApplication, QIcon
from PyQt6.QtQml import QQmlApplicationEngine

from .bridge import IcpBridge

QML_DIR = Path(__file__).resolve().parent / "qml"
LOG_LIMIT = 2000
CLIPBOARD_CLEAR_MS = 30_000


class _LogForwarder(logging.Handler):
    """Sends engine log records to the debug console, from any thread."""

    def __init__(self, controller: "Controller"):
        super().__init__(logging.DEBUG)
        self.controller = controller

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self.controller.logged.emit(record.levelname.lower(), f"{record.name}: {record.getMessage()}")
        except Exception:  # noqa: BLE001 - logging must never break the engine
            pass


class Controller(QObject):
    logged = pyqtSignal(str, str)          # level, text (thread-safe entry point)
    changed = pyqtSignal()
    vaultChanged = pyqtSignal()
    logChanged = pyqtSignal()
    promptChanged = pyqtSignal()
    toast = pyqtSignal(str)

    def __init__(self, anisette_url: str | None = None):
        super().__init__()
        self.bridge = IcpBridge(anisette_url)
        self.bridge.message.connect(self._on_message)
        self.bridge.finished.connect(self._on_finished)
        self.logged.connect(self._append_log)
        self._items: list[dict] = []
        self._log: list[dict] = []
        self._status = "Not connected"
        self._error = ""
        self._prompt = {"kind": "", "message": "", "devices": []}
        self._stage = "signin"
        self._busy = False
        self._pending: list[dict] | None = None
        handler = _LogForwarder(self)
        logging.getLogger("icp").addHandler(handler)
        logging.getLogger("icp").setLevel(logging.DEBUG)
        self._append_log("info", f"Anisette service: {self.bridge.anisette_url}")
        QTimer.singleShot(0, self._load_saved)

    # ---- properties ------------------------------------------------------------------
    @pyqtProperty("QVariantList", notify=vaultChanged)
    def items(self):
        return self._items

    @pyqtProperty("QVariantList", notify=logChanged)
    def log(self):
        return self._log

    @pyqtProperty(str, notify=changed)
    def status(self):
        return self._status

    @pyqtProperty(str, notify=changed)
    def error(self):
        return self._error

    @pyqtProperty(bool, notify=changed)
    def busy(self):
        return self._busy

    @pyqtProperty(str, notify=changed)
    def stage(self):
        """signin | working | prompt | done"""
        return self._stage

    @pyqtProperty(bool, notify=vaultChanged)
    def signedIn(self):
        return bool(self._items) or self.bridge.signed_in()

    @pyqtProperty("QVariantMap", notify=promptChanged)
    def prompt(self):
        return self._prompt

    @pyqtProperty(str, constant=True)
    def anisetteUrl(self):
        return self.bridge.anisette_url

    @pyqtProperty(str, constant=True)
    def dataDir(self):
        try:
            from .. import paths
            return str(paths.vault_file().parent)
        except Exception:  # noqa: BLE001
            return ""

    # ---- actions -----------------------------------------------------------------------
    @pyqtSlot(str, str)
    def signIn(self, email: str, password: str) -> None:
        email = email.strip()
        if not email or not password:
            self._set(error="Enter your Apple Account email and password.")
            return
        self._append_log("info", f"Sign-in started for {email}")
        self._pending = None
        self._set(error="", stage="working", busy=True, status="Signing in…")
        try:
            self.bridge.start(email, password)
        except RuntimeError as error:
            self._set(error=str(error), stage="signin", busy=False)

    @pyqtSlot()
    def sync(self) -> None:
        if self.bridge.busy:
            return
        self._append_log("info", "Sync started")
        self._pending = None
        self._set(error="", busy=True, status="Syncing…")
        self.bridge.sync()

    @pyqtSlot(str)
    def answer(self, value: str) -> None:
        kind = self._prompt.get("kind", "")
        if kind == "code":
            value = "".join(ch for ch in value if ch.isdigit())
            if len(value) != 6:
                self._set(error="Enter the six digits shown on your device.")
                return
        elif kind == "device":
            choices = {str(d.get("index")) for d in self._prompt.get("devices", [])}
            if value not in choices:
                self._set(error="Choose one of the devices.")
                return
        elif kind in {"password", "passcode"} and not value:
            self._set(error="This field cannot be empty.")
            return
        self._append_log("info", f"Answered {kind or 'prompt'}" + ("" if kind in {"password", "passcode"} else f": {value}" if kind != "code" else ""))
        self._clear_prompt()
        self.bridge.respond(kind, value)

    @pyqtSlot(bool)
    def confirm(self, accepted: bool) -> None:
        self._append_log("info", "Escrow join confirmed" if accepted else "Escrow join declined")
        self._clear_prompt()
        self.bridge.respond("confirm", accepted)

    @pyqtSlot()
    def cancel(self) -> None:
        self._append_log("warning", "Cancel requested")
        self.bridge.cancel()

    @pyqtSlot(str)
    def copy(self, text: str) -> None:
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)
        QTimer.singleShot(CLIPBOARD_CLEAR_MS, lambda: clipboard.clear() if clipboard.text() == text else None)
        self.toast.emit("Copied — clears in 30 seconds")

    @pyqtSlot(str, result="QVariantMap")
    def totp(self, uri: str):
        if not uri:
            return {}
        try:
            from ..totp import generate
            return generate(uri) or {}
        except Exception:  # noqa: BLE001 - a malformed code never breaks the detail view
            return {}

    @pyqtSlot()
    def copyLog(self) -> None:
        self.copy("\n".join(f"{e['time']} {e['level'].upper():7} {e['text']}" for e in self._log))

    @pyqtSlot()
    def clearLog(self) -> None:
        self._log = []
        self.logChanged.emit()

    # ---- engine events -----------------------------------------------------------------
    def _load_saved(self) -> None:
        try:
            items = self.bridge.load_vault()
        except Exception as error:  # noqa: BLE001
            self._append_log("warning", f"Saved vault unavailable: {error}")
            items = []
        self._items = items
        self.vaultChanged.emit()
        if items:
            self._set(stage="done", status=f"{len(items)} passwords")
            self._append_log("info", f"Opened the local vault with {len(items)} passwords")

    def _on_message(self, event: dict) -> None:
        kind = event.get("type")
        if kind == "status":
            text = str(event.get("message", ""))
            self._append_log("info", text)
            self._set(status=text.splitlines()[0][:120] if text else self._status)
        elif kind == "prompt":
            self._prompt = {"kind": str(event.get("kind", "")), "message": str(event.get("message", "")),
                            "devices": list(event.get("devices") or [])}
            self.promptChanged.emit()
            self._append_log("info", f"Waiting for {self._prompt['kind']}: {self._prompt['message'].splitlines()[-1]}")
            self._set(stage="prompt", error="")
        elif kind == "passwords":
            self._pending = list(event.get("items") or [])
        elif kind == "error":
            text = str(event.get("message", "Unknown error"))
            self._append_log("error", text)
            self._set(error=text)

    def _on_finished(self, code: int) -> None:
        self._clear_prompt()
        self._append_log("info" if code == 0 else "error", f"Operation finished (exit {code})")
        if code == 0 and self._pending is not None:
            self._items = self._pending
            self.vaultChanged.emit()
            self._set(stage="done", busy=False, status=f"{len(self._items)} passwords")
            if self._items:
                self.toast.emit(f"Keychain up to date — {len(self._items)} passwords")
        else:
            self._set(busy=False, stage="done" if self._items else "signin",
                      status="Stopped" if code else self._status)
        self._pending = None

    # ---- helpers -----------------------------------------------------------------------
    def _clear_prompt(self) -> None:
        self._prompt = {"kind": "", "message": "", "devices": []}
        self.promptChanged.emit()
        if self._stage == "prompt":
            self._set(stage="working")

    def _set(self, **values) -> None:
        for key, value in values.items():
            setattr(self, f"_{key}", value)
        self.changed.emit()

    def _append_log(self, level: str, text: str) -> None:
        stamp = time.strftime("%H:%M:%S")
        last = self._log[-1] if self._log else None
        if last and last["base"] == text and last["level"] == level:
            repeat = last["repeat"] + 1
            entry = {**last, "time": stamp, "repeat": repeat, "text": f"{text}  (×{repeat})"}
            self._log = self._log[:-1] + [entry]
        else:
            entry = {"time": stamp, "level": level, "text": text, "base": text, "repeat": 1}
            self._log = (self._log + [entry])[-LOG_LIMIT:]
        self.logChanged.emit()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="icp-gui")
    parser.add_argument("--anisette", help="anisette service URL (default: $ICP_ANISETTE_URL "
                        "or http://127.0.0.1:6969)")
    parser.add_argument("--classic", action="store_true", help="open the previous Qt Widgets window")
    parser.add_argument("--smoke-test", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.classic:
        from .window import main as classic_main
        return classic_main((["--anisette", args.anisette] if args.anisette else [])
                            + (["--smoke-test"] if args.smoke_test else []))
    os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")
    app = QGuiApplication(sys.argv[:1])
    app.setApplicationName("Passwords")
    app.setDesktopFileName("icloud-keychain")
    app.setWindowIcon(QIcon(str(QML_DIR / "icon.svg")))
    controller = Controller(args.anisette)
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("icp", controller)
    engine.load(QUrl.fromLocalFile(str(QML_DIR / "Main.qml")))
    if not engine.rootObjects():
        print("QML failed to load", file=sys.stderr)
        return 1
    print(f"QT_PLATFORM={app.platformName()}", flush=True)
    if args.smoke_test:
        QTimer.singleShot(3000, app.quit)
    code = app.exec()
    engine.deleteLater()
    del engine  # release QML bindings before the controller they read
    return code
