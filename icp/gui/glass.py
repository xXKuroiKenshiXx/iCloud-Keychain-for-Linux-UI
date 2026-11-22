"""Liquid Glass window (Qt Quick). `Controller` exposes the IcpBridge to QML: the sign-in
flow, the vault, verification codes, and a live debug log of everything the engine does."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import threading
import time
from pathlib import Path

from PyQt6.QtCore import QObject, QTimer, QUrl, pyqtProperty, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QGuiApplication, QIcon, QImage
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt6.QtQml import QQmlApplicationEngine, QQmlNetworkAccessManagerFactory
from PyQt6.QtQuick import QQuickImageProvider

from . import icons
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


class _OfflineNetwork(QNetworkAccessManager):
    """QML may only load local files; any other URL is replaced with a dead request."""

    def createRequest(self, op, request, data=None):
        if request.url().scheme() not in ("file", "qrc"):
            request = QNetworkRequest(QUrl("file:///nonexistent/blocked"))
        return super().createRequest(op, request, data)


class _OfflineNetworkFactory(QQmlNetworkAccessManagerFactory):
    def create(self, parent):
        return _OfflineNetwork(parent)


class _IconProvider(QQuickImageProvider):
    """Serves decrypted icons from memory as image://icons/<key>#<version>."""

    def __init__(self, controller: "Controller"):
        super().__init__(QQuickImageProvider.ImageType.Image)
        self.controller = controller

    def requestImage(self, ident, size):
        key = ident.split("#", 1)[0]
        store = self.controller.icon_store
        data = store.png(key) if store and key else None
        image = QImage.fromData(data) if data else QImage()
        return image, image.size()


class Controller(QObject):
    logged = pyqtSignal(str, str)          # level, text (thread-safe entry point)
    iconFetched = pyqtSignal(str, bytes, str, bool)   # key, png, site name, ok (from worker)
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
        self._raw: list[dict] = []
        self.icon_store: icons.IconStore | None = None
        self._prefs = self._read_prefs()
        self._icon_jobs: list[tuple[str, str]] = []
        self._icon_thread: threading.Thread | None = None
        self.iconFetched.connect(self._on_icon)
        self._redecorate = QTimer(self, singleShot=True, interval=400)
        self._redecorate.timeout.connect(self._publish)
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

    @pyqtProperty(bool, notify=changed)
    def fetchIcons(self):
        return bool(self._prefs.get("fetch_icons", True))

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

    @pyqtSlot(bool)
    def setFetchIcons(self, enabled: bool) -> None:
        self._prefs["fetch_icons"] = bool(enabled)
        self._write_prefs()
        self._append_log("info", f"Website icons {'on' if enabled else 'off'}")
        self.changed.emit()
        if enabled:
            self._schedule_icons()

    @pyqtSlot()
    def refreshIcons(self) -> None:
        if not self._ensure_store():
            return
        for entry in self.icon_store.meta.values():
            if not entry.get("ok"):
                entry["at"] = 0
        self._schedule_icons()

    @pyqtSlot(str, str, str)
    def chooseIcon(self, key: str, display: str, file_url: str) -> None:
        if not self._ensure_store() or not key:
            return
        path = QUrl(file_url).toLocalFile() or file_url
        try:
            with open(path, "rb") as handle:
                data = handle.read(icons.MAX_CUSTOM + 1)
            png = icons.sanitize_image(data)
        except (OSError, icons.FetchError) as error:
            self._set(error=f"That file can't be used as an icon: {error}")
            return
        self.icon_store.put(key, png, custom=True, name="")
        self._append_log("info", f"Custom icon set for {display}")
        self._publish()

    @pyqtSlot(str, str)
    def resetIcon(self, key: str, site: str) -> None:
        if not self._ensure_store() or not key:
            return
        self.icon_store.remove(key)
        self._publish()
        if site:
            self._schedule_icons()

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
        self._set_items(items)
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
            self._set_items(self._pending)
            self._set(stage="done", busy=False, status=f"{len(self._items)} passwords")
            if self._items:
                self.toast.emit(f"Keychain up to date — {len(self._items)} passwords")
        else:
            self._set(busy=False, stage="done" if self._items else "signin",
                      status="Stopped" if code else self._status)
        self._pending = None

    # ---- icons -------------------------------------------------------------------------
    def _ensure_store(self) -> bool:
        if self.icon_store is None:
            try:
                self.icon_store = icons.IconStore()
            except Exception as error:  # noqa: BLE001 - icons are optional
                self._append_log("warning", f"Icon cache unavailable: {error}")
                return False
        return True

    @staticmethod
    def _subject(item: dict) -> str:
        site = icons.normalize_host(item.get("site") or "")
        return site or "title:" + str(item.get("name") or "").casefold()

    def _set_items(self, raw: list[dict]) -> None:
        self._raw = list(raw)
        self._publish()
        self._schedule_icons()

    def _publish(self) -> None:
        store = self.icon_store if self._ensure_store() else None
        items = []
        for raw in self._raw:
            item = dict(raw)
            key = store.key_for(self._subject(item)) if store else ""
            entry = store.meta.get(key, {}) if store else {}
            item["iconKey"] = key
            item["icon"] = f"image://icons/{key}#{entry.get('v', 0)}" if entry.get("ok") else ""
            item["display"] = (entry.get("name") if not item.get("title") and entry.get("name") else None) or item["name"]
            item["customIcon"] = bool(entry.get("custom"))
            items.append(item)
        items.sort(key=lambda i: str(i["display"]).casefold())
        self._items = items
        self.vaultChanged.emit()

    def _schedule_icons(self) -> None:
        if not self.fetchIcons or not self._ensure_store():
            return
        queued = {key for key, _ in self._icon_jobs}
        for item in self._raw:
            host = icons.normalize_host(item.get("site") or "")
            if not host:
                continue
            key = self.icon_store.key_for(host)
            if key not in queued and self.icon_store.needs_fetch(key):
                self._icon_jobs.append((key, host))
                queued.add(key)
        if self._icon_jobs and not (self._icon_thread and self._icon_thread.is_alive()):
            self._append_log("info", f"Fetching website icons for {len(self._icon_jobs)} sites")
            self._icon_thread = threading.Thread(target=self._icon_worker, daemon=True)
            self._icon_thread.start()

    def _icon_worker(self) -> None:
        while self._icon_jobs and self.fetchIcons:
            key, host = self._icon_jobs.pop(0)
            try:
                png, name = icons.fetch_site(host)
                self.iconFetched.emit(key, png, name, True)
            except Exception as error:  # noqa: BLE001 - one site never stops the others
                self.logged.emit("debug", f"icon for {host}: {error}")
                self.iconFetched.emit(key, b"", "", False)

    def _on_icon(self, key: str, png: bytes, name: str, ok: bool) -> None:
        if self.icon_store is None:
            return
        self.icon_store.put(key, png if ok else None, name=name)
        self._redecorate.start()

    def _prefs_path(self) -> Path | None:
        try:
            from .. import paths
            return paths.vault_file().parent / "gui.json"
        except Exception:  # noqa: BLE001
            return None

    def _read_prefs(self) -> dict:
        path = self._prefs_path()
        try:
            data = json.loads(path.read_text()) if path and path.exists() else {}
            return data if isinstance(data, dict) else {}
        except (OSError, ValueError):
            return {}

    def _write_prefs(self) -> None:
        path = self._prefs_path()
        if not path:
            return
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as handle:
            json.dump({"fetch_icons": bool(self._prefs.get("fetch_icons", True))}, handle)

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


def create_engine(controller: Controller) -> QQmlApplicationEngine:
    """Loads the window with the controller, the encrypted icon provider, and no network."""
    engine = QQmlApplicationEngine()
    engine._network_factory = _OfflineNetworkFactory()  # kept alive with the engine
    engine.setNetworkAccessManagerFactory(engine._network_factory)
    engine.addImageProvider("icons", _IconProvider(controller))
    engine.rootContext().setContextProperty("icp", controller)
    engine.load(QUrl.fromLocalFile(str(QML_DIR / "Main.qml")))
    return engine


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
    engine = create_engine(controller)
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
