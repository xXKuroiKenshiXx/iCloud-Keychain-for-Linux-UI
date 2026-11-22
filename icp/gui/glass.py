"""Liquid Glass window (Qt Quick). `Controller` exposes the IcpBridge to QML: the sign-in
flow, the vault, verification codes, and a live debug log of everything the engine does."""

from __future__ import annotations

import argparse
import csv
import secrets
import string
import json
import logging
import re
import os
import sys
import threading
import time
from pathlib import Path

from PyQt6.QtCore import QCoreApplication, QEvent, QObject, QTimer, QUrl, pyqtProperty, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QGuiApplication, QIcon, QImage
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt6.QtQml import QQmlApplicationEngine, QQmlNetworkAccessManagerFactory
from PyQt6.QtQuick import QQuickImageProvider

from . import i18n, icons
from . import setup as anisette_setup
from .bridge import IcpBridge

QML_DIR = Path(__file__).resolve().parent / "qml"
LOG_LIMIT = 2000
CLIPBOARD_CLEAR_MS = 30_000


def mask_account(value: str) -> str:
    """Keeps an Apple Account recognizable in logs without writing it out."""
    name, at, domain = (value or "").partition("@")
    return (name[:2] + "***" + at + domain) if at else (value[:2] + "***" if value else "")


def harden_process() -> None:
    """Private file modes for everything the window writes, and no core dumps that could
    hold decrypted passwords."""
    os.umask(0o077)
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    except (ImportError, ValueError, OSError):
        pass


class _LogForwarder(logging.Handler):
    """Sends engine log records to the debug console, from any thread."""

    def __init__(self, controller: "Controller"):
        super().__init__(logging.INFO)
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


SORT_KEYS = ("website", "title", "modified", "created")
SIDEBAR_MODES = ("full", "compact", "hidden")
CSV_HEADER = ["Title", "URL", "Username", "Password", "Notes", "OTPAuth"]


def generate_password() -> str:
    """A strong password in Apple's grouped style (xxxxxx-xxxxxx-xxxxxx): 18 random letters and
    digits from a cryptographic source, with at least one uppercase letter and one digit."""
    alphabet = "abcdefghijkmnopqrstuvwxyz23456789"
    chars = [secrets.choice(alphabet) for _ in range(18)]
    upper, digit = secrets.SystemRandom().sample(range(18), 2)
    chars[upper] = secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ")
    chars[digit] = secrets.choice("23456789")
    text = "".join(chars)
    return "-".join(text[i:i + 6] for i in (0, 6, 12))


def export_rows(items: list[dict]) -> list[list[str]]:
    """Rows for Apple's Passwords CSV format (Title, URL, Username, Password, Notes, OTPAuth)."""
    rows = []
    for item in items:
        site = item.get("site") or ""
        rows.append([str(item.get("display") or item.get("name") or ""),
                     f"https://{site}/" if site else "",
                     str(item.get("username") or ""), str(item.get("password") or ""),
                     str(item.get("notes") or ""), str(item.get("totp") or "")])
    return rows


def friendly_error(text: str, anisette_url: str = "", tr=lambda message: message) -> str:
    """Plain-language explanation for the failures people actually hit; the raw text stays
    in the debug console."""
    low = text.lower()
    if "429" in low or "rate" in low and "limit" in low:
        return tr("Apple is limiting sign-in attempts from this computer. Wait at least an hour before trying again; retrying sooner extends the block.")
    if "503" in low:
        return tr("Apple's sign-in service refused this device identity (HTTP 503). Check that the anisette service is the Windows iCloud one and is running.")
    if "-22406" in low or "incorrect" in low and "password" in low:
        return tr("Apple says the Apple Account email or password is incorrect.")
    if "-22410" in low:
        return tr("Apple rejected the sign-in request (-22410). This usually means the anisette identity does not match; restart the anisette service and try again later.")
    if "anisette" in low or "connection refused" in low or "max retries" in low:
        return tr("The anisette service at {url} isn't answering. Start it, then try again.").format(url=anisette_url)
    if "escrow" in low and ("limit" in low or "attempt" in low):
        return tr("The device passcode was not accepted. Each wrong passcode uses one of about ten recovery attempts; check the device before trying again.")
    if "cancelled" in low:
        return tr("Cancelled. Nothing was changed.")
    return text


class Controller(QObject):
    logged = pyqtSignal(str, str)          # level, text (thread-safe entry point)
    iconFetched = pyqtSignal(str, bytes, str, bool)   # key, png, site name, ok (from worker)
    changed = pyqtSignal()
    vaultChanged = pyqtSignal()
    logChanged = pyqtSignal()
    promptChanged = pyqtSignal()
    toast = pyqtSignal(str)
    iconsChanged = pyqtSignal()
    languageChanged = pyqtSignal()
    setupChanged = pyqtSignal()
    sortChanged = pyqtSignal()
    appearanceChanged = pyqtSignal()
    setupReport = pyqtSignal(str, str)     # kind, text (from the installer thread)

    def __init__(self, anisette_url: str | None = None, bridge=None):
        super().__init__()
        self.bridge = bridge or IcpBridge(anisette_url)
        self.bridge.message.connect(self._on_message)
        self.bridge.finished.connect(self._on_finished)
        self.logged.connect(self._append_log)
        self._items: list[dict] = []
        self._log: list[dict] = []
        self._seen_once: set[str] = set()
        self._status = ""
        self._error = ""
        self._prompt = {"kind": "", "message": "", "devices": []}
        self._stage = "signin"
        self._busy = False
        self._pending: list[dict] | None = None
        self._raw: list[dict] = []
        self.icon_store: icons.IconStore | None = None
        self._prefs = self._read_prefs()
        self._language = i18n.resolve(self._prefs.get("language", "system"))
        self._language_revision = 0
        self._icon_jobs: list[tuple[str, str]] = []
        self._icon_lock = threading.Lock()
        self._icon_thread: threading.Thread | None = None
        self._icon_revision = 0
        self._anisette_state = -1          # -1 unknown, 0 not answering, 1 answering
        self.iconFetched.connect(self._on_icon)
        self.anisetteChecked.connect(lambda ok: self._set(anisette_state=1 if ok else 0))
        self._icons_tick = QTimer(self, singleShot=True, interval=120)
        self._icons_tick.timeout.connect(self._bump_icons)
        handler = _LogForwarder(self)
        logging.getLogger("icp").addHandler(handler)
        logging.getLogger("icp").setLevel(logging.INFO)
        self._append_log("info", f"Anisette service: {self.bridge.anisette_url}")
        self._setup = {"phase": "idle", "step": "", "error": "", "missing": [], "command": "",
                       "candidates": [], "log": []}
        self.setupReport.connect(self._on_setup_report)
        configured = self._prefs.get("anisette") or {}
        if configured.get("mode") == "url" and configured.get("url") and not anisette_url:
            self._apply_url(configured["url"])
        hints = QGuiApplication.styleHints() if QGuiApplication.instance() else None
        if hints is not None and hasattr(hints, "colorSchemeChanged"):
            hints.colorSchemeChanged.connect(lambda *_: self._appearance_updated())
        QTimer.singleShot(0, self._load_saved)
        QTimer.singleShot(0, self._autostart_anisette)

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

    # ---- language ------------------------------------------------------------------------
    def _t(self, text: str) -> str:
        return i18n.translate(text, self._language)

    @pyqtSlot(str, int, result=str)
    def tr(self, text: str, revision: int) -> str:
        return self._t(text)

    @pyqtProperty(int, notify=languageChanged)
    def languageRevision(self):
        return self._language_revision

    @pyqtProperty(str, notify=languageChanged)
    def languagePreference(self):
        return self._prefs.get("language", "system") if self._prefs.get("language") in i18n.LANGUAGES else "system"

    @pyqtProperty("QVariantList", notify=languageChanged)
    def languageOptions(self):
        system = i18n.LANGUAGES[i18n.system_language()]
        options = [{"code": "system", "name": self._t("System ({lang})").format(lang=system)}]
        options += [{"code": code, "name": name} for code, name in i18n.LANGUAGES.items()]
        return options

    @pyqtSlot(str)
    def setLanguage(self, code: str) -> None:
        self._prefs["language"] = code if code in i18n.LANGUAGES else "system"
        self._write_prefs()
        self._language = i18n.resolve(self._prefs["language"])
        self._language_revision += 1
        self._append_log("info", f"Language: {self._language}")
        self.languageChanged.emit()
        self.changed.emit()

    @pyqtProperty(int, notify=iconsChanged)
    def iconRevision(self):
        return self._icon_revision

    @pyqtProperty(int, notify=changed)
    def anisetteState(self):
        return self._anisette_state

    @pyqtProperty(str, notify=appearanceChanged)
    def appearance(self):
        value = self._prefs.get("appearance", "system")
        return value if value in ("system", "light", "dark") else "system"

    @pyqtProperty(bool, notify=appearanceChanged)
    def darkMode(self):
        if self.appearance != "system":
            return self.appearance == "dark"
        try:
            from PyQt6.QtCore import Qt
            return QGuiApplication.styleHints().colorScheme() != Qt.ColorScheme.Light
        except Exception:  # noqa: BLE001 - unknown scheme means dark, the app's home look
            return True

    @pyqtSlot(str)
    def setAppearance(self, value: str) -> None:
        self._prefs["appearance"] = value if value in ("system", "light", "dark") else "system"
        self._write_prefs()
        self._appearance_updated()

    def _appearance_updated(self) -> None:
        self.appearanceChanged.emit()
        app = QGuiApplication.instance()
        if app is not None:
            app.setWindowIcon(QIcon(str(QML_DIR / ("icon-dark.svg" if self.darkMode else "icon-light.svg"))))

    @pyqtProperty(bool, notify=changed)
    def animations(self):
        return bool(self._prefs.get("animations", True))

    @pyqtProperty(str, notify=sortChanged)
    def sortKey(self):
        value = self._prefs.get("sort", "website")
        return value if value in SORT_KEYS else "website"

    @pyqtProperty(bool, notify=sortChanged)
    def sortDescending(self):
        return bool(self._prefs.get("sort_desc", False))

    @pyqtProperty(str, notify=changed)
    def sidebarStyle(self):
        value = self._prefs.get("sidebar", "full")
        return value if value in ("full", "compact") else "full"

    @pyqtProperty(str, notify=changed)
    def sidebarMode(self):
        return self.sidebarStyle if self._prefs.get("sidebar_visible", True) else "hidden"

    @pyqtSlot()
    def toggleSidebar(self) -> None:
        self._prefs["sidebar_visible"] = not self._prefs.get("sidebar_visible", True)
        self._write_prefs()
        self.changed.emit()

    @pyqtSlot(bool)
    def setAnimations(self, enabled: bool) -> None:
        self._prefs["animations"] = bool(enabled)
        self._write_prefs()
        self.changed.emit()

    @pyqtSlot(str, bool)
    def setSort(self, key: str, descending: bool) -> None:
        self._prefs["sort"] = key if key in SORT_KEYS else "website"
        self._prefs["sort_desc"] = bool(descending)
        self._write_prefs()
        self.sortChanged.emit()
        QTimer.singleShot(0, self._publish)   # after the menu has closed

    @pyqtSlot(str)
    def setSidebarMode(self, mode: str) -> None:
        if mode == "hidden":
            self._prefs["sidebar_visible"] = False
        else:
            self._prefs["sidebar"] = mode if mode in ("full", "compact") else "full"
            self._prefs["sidebar_visible"] = True
        self._write_prefs()
        self.changed.emit()

    @pyqtSlot(result=str)
    def generatePassword(self) -> str:
        return generate_password()

    @pyqtSlot(str, result=bool)
    def exportCsv(self, file_url: str) -> bool:
        """Writes every password to a CSV in Apple's format, readable only by this user."""
        path = QUrl(file_url).toLocalFile() or file_url
        if not path:
            return False
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, "w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(CSV_HEADER)
                writer.writerows(export_rows(self._items))
            os.chmod(path, 0o600)
        except OSError as error:
            self._set(error=self._t("Couldn't export: {error}").format(error=error))
            self.toast.emit(self._t("Couldn't export: {error}").format(error=error))
            return False
        self._append_log("info", f"Exported {len(self._items)} passwords to a CSV file")
        self.toast.emit(self._t("Exported {n} passwords").format(n=len(self._items)))
        return True

    @pyqtProperty(bool, notify=changed)
    def fetchIcons(self):
        return bool(self._prefs.get("fetch_icons", True))

    @pyqtProperty("QVariantMap", notify=setupChanged)
    def setup(self):
        return self._setup

    @pyqtProperty(str, notify=changed)
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
            self._set(error=self._t("Enter your Apple Account email and password."))
            return
        if self._anisette_state == 0:
            self.checkAnisette()
            self._set(error=friendly_error("anisette", self.bridge.anisette_url, self._t))
            return
        self._append_log("info", f"Sign-in started for {mask_account(email)}")
        self._pending = None
        self._set(error="", stage="working", busy=True, status=self._t("Signing in…"))
        try:
            self.bridge.start(email, password)
        except RuntimeError as error:
            self._set(error=self._t("Another operation is already running."), stage="signin", busy=False)

    @pyqtSlot()
    def sync(self) -> None:
        if self.bridge.busy:
            return
        self._append_log("info", "Sync started")
        self._pending = None
        self._set(error="", busy=True, status=self._t("Syncing…"))
        self.bridge.sync()

    @pyqtSlot(str)
    def answer(self, value: str) -> None:
        kind = self._prompt.get("kind", "")
        if kind == "code":
            value = "".join(ch for ch in value if ch.isdigit())
            if len(value) != 6:
                self._set(error=self._t("Enter the six digits shown on your device."))
                return
        elif kind == "device":
            choices = {str(d.get("index")) for d in self._prompt.get("devices", [])}
            if value not in choices:
                self._set(error=self._t("Choose one of the devices."))
                return
        elif kind in {"password", "passcode"} and not value:
            self._set(error=self._t("This field cannot be empty."))
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
        self.toast.emit(self._t("Copied — clears in 30 seconds"))

    @pyqtSlot(str, result="QVariantMap")
    def totp(self, uri: str):
        if not uri:
            return {}
        try:
            from ..totp import generate
            return generate(uri) or {}
        except Exception:  # noqa: BLE001 - a malformed code never breaks the detail view
            return {}

    # ---- anisette setup -------------------------------------------------------------------
    def _autostart_anisette(self) -> None:
        """Starts a local Anisette-on-Wine that is already installed, then checks the service."""
        configured = self._prefs.get("anisette") or {}
        if configured.get("mode") != "url":
            folder = anisette_setup.find_installed_tool()
            if folder and self.bridge.anisette_url == anisette_setup.DEFAULT_URL:
                self._append_log("info", f"Starting the local anisette service from {folder}")
                threading.Thread(target=self._start_and_check, args=(folder,), daemon=True).start()
                return
        self.checkAnisette()

    def _start_and_check(self, folder) -> None:
        try:
            anisette_setup.start_service(folder)
            for _ in range(25):
                if anisette_setup.healthy(self.bridge.anisette_url, timeout=1):
                    break
                time.sleep(1)
        except Exception as error:  # noqa: BLE001
            self.logged.emit("warning", f"anisette autostart: {error}")
        self.anisetteChecked.emit(anisette_setup.healthy(self.bridge.anisette_url, timeout=2))

    @pyqtSlot()
    def setupRefresh(self) -> None:
        missing = anisette_setup.missing_tools()
        self._setup.update({"missing": missing, "command": anisette_setup.install_command(missing),
                            "candidates": anisette_setup.find_icloud_dirs()})
        self.setupChanged.emit()

    @pyqtProperty(bool, notify=setupChanged)
    def canInstallTools(self):
        return bool(anisette_setup.install_argv(self._setup.get("missing") or []))

    @pyqtSlot()
    def setupInstallTools(self) -> None:
        if self._setup.get("phase") in ("running", "tools"):
            return
        self._setup.update({"phase": "tools", "error": "", "log": []})
        self.setupChanged.emit()
        self._append_log("info", "Installing setup tools with pkexec")
        anisette_setup.install_tools(list(self._setup.get("missing") or []),
                                     lambda kind, text: self.setupReport.emit(kind, text))

    # ---- applications menu (AppImage) -----------------------------------------------------
    @pyqtProperty(bool, constant=True)
    def runningAppImage(self):
        return bool(anisette_setup.appimage_path())

    @pyqtProperty(bool, notify=setupChanged)
    def inAppMenu(self):
        return anisette_setup.is_integrated()

    @pyqtSlot()
    def addToAppMenu(self) -> None:
        try:
            target = anisette_setup.integrate(QML_DIR / "icon-dark.svg")
        except (OSError, RuntimeError) as error:
            self._append_log("error", f"Could not add to the applications menu: {error}")
            self.toast.emit(self._t("Couldn't add to the applications menu."))
            return
        self._append_log("info", f"Added to the applications menu ({target})")
        self.toast.emit(self._t("Added to your applications menu"))
        self.setupChanged.emit()

    @pyqtSlot()
    def removeFromAppMenu(self) -> None:
        anisette_setup.unintegrate()
        self.toast.emit(self._t("Removed from your applications menu"))
        self.setupChanged.emit()

    @pyqtSlot()
    def setupReset(self) -> None:
        self._setup.update({"phase": "idle", "error": "", "log": []})
        self.setupRefresh()

    @pyqtSlot(str, result=str)
    def setupFolder(self, url: str) -> str:
        """The local path for a picked folder when it holds the iCloud libraries, else ""."""
        path = QUrl(url).toLocalFile() or url
        return path if anisette_setup.is_icloud_dir(path) else ""

    @pyqtSlot(str)
    def setupInstall(self, icloud_folder: str) -> None:
        if self._setup.get("phase") == "running":
            return
        self._setup.update({"phase": "running", "step": "copy", "error": "", "log": []})
        self.setupChanged.emit()
        self._append_log("info", "Anisette setup started")
        anisette_setup.Installer(icloud_folder, lambda kind, text: self.setupReport.emit(kind, text)).start()

    @pyqtSlot(str)
    def setupUseUrl(self, url: str) -> None:
        url = url.strip().rstrip("/")
        if not url.startswith(("http://", "https://")):
            self._setup["error"] = self._t("Enter a URL that starts with http:// or https://.")
            self.setupChanged.emit()
            return
        self._prefs["anisette"] = {"mode": "url", "url": url}
        self._write_prefs()
        self._apply_url(url)
        self._setup.update({"phase": "idle", "error": ""})
        self.setupChanged.emit()
        self.checkAnisette()

    def _apply_url(self, url: str) -> None:
        self.bridge.anisette_url = url
        os.environ["ICP_ANISETTE_URL"] = url
        self.changed.emit()

    def _on_setup_report(self, kind: str, text: str) -> None:
        if kind == "line":
            self._append_log("debug", f"setup: {text}")
            self._setup["log"] = (self._setup.get("log", []) + [text])[-6:]
        elif kind == "step":
            self._append_log("info", f"Anisette setup: {text}")
            self._setup["step"] = text
        elif kind == "done":
            self._setup.update({"phase": "done", "step": "start"})
            self._prefs["anisette"] = {"mode": "wine"}
            self._write_prefs()
            self._apply_url(anisette_setup.DEFAULT_URL)
            self._append_log("info", "Anisette setup finished")
            self._set(anisette_state=1)
        elif kind == "tools-done":
            self._setup.update({"phase": "idle", "error": ""})
            self.setupRefresh()
        elif kind == "tools-error":
            self._setup.update({"phase": "idle", "error": self._t("Couldn't install automatically. Run the command in a terminal instead.")})
            self._append_log("warning", f"pkexec install failed: {text}")
        elif kind == "error":
            self._setup.update({"phase": "error", "error": text})
            self._append_log("error", f"Anisette setup failed: {text}")
        self.setupChanged.emit()

    @pyqtSlot()
    def checkAnisette(self) -> None:
        """Probes the anisette service in the background and updates `anisetteState`."""
        def probe():
            import urllib.request
            url = self.bridge.anisette_url.rstrip("/") + "/healthz"
            try:
                with urllib.request.urlopen(url, timeout=3) as response:
                    ok = response.status == 200
            except Exception:  # noqa: BLE001 - any failure means "not answering"
                ok = False
            self.anisetteChecked.emit(ok)

        threading.Thread(target=probe, daemon=True).start()

    anisetteChecked = pyqtSignal(bool)

    @pyqtSlot(str, int, result=str)
    def iconSource(self, key: str, revision: int) -> str:
        if not key or not self.icon_store:
            return ""
        entry = self.icon_store.meta.get(key, {})
        return f"image://icons/{key}#{entry.get('v', 0)}" if entry.get("ok") else ""

    @pyqtSlot(str, str, str, int, result=str)
    def displayName(self, key: str, name: str, title: str, revision: int) -> str:
        entry = self.icon_store.meta.get(key, {}) if (key and self.icon_store) else {}
        return (entry.get("name") if not title and entry.get("name") else None) or name

    @pyqtSlot(str, int, result=bool)
    def isCustomIcon(self, key: str, revision: int) -> bool:
        return bool(key and self.icon_store and self.icon_store.meta.get(key, {}).get("custom"))

    @pyqtSlot(str, str)
    def requestIcon(self, key: str, site: str) -> None:
        """Called by rows as they appear: newest requests are fetched first."""
        host = icons.normalize_host(site)
        if host and key and self.fetchIcons and self._ensure_store() and self.icon_store.needs_fetch(key):
            self._enqueue(key, host, front=True)

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
            self._set(error=self._t("That file can't be used as an icon: {error}").format(error=error))
            return
        self.icon_store.put(key, png, custom=True, name="")
        self._append_log("info", f"Custom icon set for {display}")
        self._bump_icons()

    @pyqtSlot(str, str)
    def resetIcon(self, key: str, site: str) -> None:
        if not self._ensure_store() or not key:
            return
        self.icon_store.remove(key)
        self._bump_icons()
        host = icons.normalize_host(site)
        if host and self.fetchIcons:
            self._enqueue(key, host, front=True)

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
            self._set(stage="done", status=self._t("{n} passwords").format(n=len(items)))
            self._append_log("info", f"Opened the local vault with {len(items)} passwords")

    def _on_message(self, event: dict) -> None:
        kind = event.get("type")
        if kind == "status":
            text = str(event.get("message", ""))
            self._append_log("info", text)
            shown = i18n.translate_engine(text.splitlines()[0], self._language) if text else ""
            self._set(status=shown[:160] if shown else self._status)
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
            friendly = friendly_error(text, self.bridge.anisette_url, self._t)
            self._set(error=i18n.translate_engine(friendly, self._language) if friendly == text else friendly)
            if "anisette" in text.lower() or "connection" in text.lower():
                self.checkAnisette()

    def _on_finished(self, code: int) -> None:
        self._clear_prompt()
        self._append_log("info" if code == 0 else "error", f"Operation finished (exit {code})")
        if code == 0 and self._pending is not None:
            self._set_items(self._pending)
            self._set(stage="done", busy=False, status=self._t("{n} passwords").format(n=len(self._items)))
            if self._items:
                self.toast.emit(self._t("Keychain up to date — {n} passwords").format(n=len(self._items)))
        else:
            self._set(busy=False, stage="done" if self._items else "signin",
                      status=self._t("Stopped") if code else self._status)
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
        key = self.sortKey
        if key == "title":
            items.sort(key=lambda i: str(i["display"]).casefold())
        elif key == "modified":
            items.sort(key=lambda i: float(i.get("mdat") or 0))
        elif key == "created":
            items.sort(key=lambda i: float(i.get("cdat") or i.get("mdat") or 0))
        else:
            items.sort(key=lambda i: (str(i.get("site") or i["display"]).casefold().removeprefix("www."),
                                      str(i["display"]).casefold()))
        if self.sortDescending:
            items.reverse()
        self._items = items
        self.vaultChanged.emit()

    def _schedule_icons(self) -> None:
        """Queues every missing icon behind the ones rows asked for (explicit refresh)."""
        if not self.fetchIcons or not self._ensure_store():
            return
        for item in self._raw:
            host = icons.normalize_host(item.get("site") or "")
            if host:
                key = self.icon_store.key_for(host)
                if self.icon_store.needs_fetch(key):
                    self._enqueue(key, host, front=False)

    def _enqueue(self, key: str, host: str, *, front: bool) -> None:
        with self._icon_lock:
            self._icon_jobs = [job for job in self._icon_jobs if job[0] != key]
            if front:
                self._icon_jobs.insert(0, (key, host))
            else:
                self._icon_jobs.append((key, host))
            start = not (self._icon_thread and self._icon_thread.is_alive())
            if start:
                self._icon_thread = threading.Thread(target=self._icon_worker, daemon=True)
        if start:
            self._icon_thread.start()

    def _next_icon_job(self):
        with self._icon_lock:
            return self._icon_jobs.pop(0) if self._icon_jobs and self.fetchIcons else None

    def _icon_worker(self) -> None:
        while True:
            job = self._next_icon_job()
            if job is None:
                return
            key, host = job
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
        self._icons_tick.start()

    def _bump_icons(self) -> None:
        """Rows re-read their icon and name; the list itself is not rebuilt."""
        self._icon_revision += 1
        self.iconsChanged.emit()

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
            json.dump({"fetch_icons": bool(self._prefs.get("fetch_icons", True)),
                       "language": self._prefs.get("language", "system"),
                       "anisette": self._prefs.get("anisette") or {},
                       "animations": bool(self._prefs.get("animations", True)),
                       "sort": self.sortKey, "sort_desc": self.sortDescending,
                       "sidebar": self.sidebarStyle,
                       "sidebar_visible": bool(self._prefs.get("sidebar_visible", True)),
                       "appearance": self.appearance}, handle)

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

    _EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
    _ONCE = ("Secret Service unavailable",)

    def _append_log(self, level: str, text: str) -> None:
        text = self._EMAIL.sub(lambda m: mask_account(m.group(0)), text)
        once = next((marker for marker in self._ONCE if marker in text), None)
        if once:
            if once in self._seen_once:
                return
            self._seen_once.add(once)
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
    harden_process()
    os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")
    app = QGuiApplication(sys.argv[:1])
    app.setApplicationName("Passwords")
    app.setDesktopFileName("icloud-keychain")
    controller = Controller(args.anisette)
    controller._appearance_updated()
    engine = create_engine(controller)
    if not engine.rootObjects():
        print("QML failed to load", file=sys.stderr)
        return 1
    print(f"QT_PLATFORM={app.platformName()}", flush=True)
    if args.smoke_test:
        QTimer.singleShot(3000, app.quit)
    code = app.exec()
    # Tear the window down while the controller it reads still exists.
    for root in engine.rootObjects():
        root.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete.value)
    del engine
    return code
