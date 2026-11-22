"""Runs the icp engine in a worker thread and turns its terminal prompts into
Qt events.

icp sends every prompt and message through `icp.cli.ui`. While an operation runs, those
functions are replaced with versions that emit `message` events and block until the window
answers through `respond`. Secrets travel only in process memory."""

from __future__ import annotations

import argparse
import os
import queue
import re
import threading

from PyQt6.QtCore import QObject, pyqtSignal

DEFAULT_ANISETTE_URL = "http://127.0.0.1:6969"
_CHOICE_LINE = re.compile(r"^\s*(\d+)\)\s+(.+?)\s*$")
_HOST = re.compile(r"^(?=.*[a-z])[a-z0-9-]+(\.[a-z0-9-]+)+$", re.IGNORECASE)


class Cancelled(Exception):
    """Raised inside the worker when the window cancels the operation."""


def classify_prompt(message: str, secret: bool) -> str:
    """Maps an icp prompt text to the kind of answer the window must collect."""
    text = message.lower()
    if secret:
        return "passcode" if "passcode" in text or "security code" in text else "password"
    if "code" in text:
        return "code"
    if text.startswith("select"):
        return "device"
    if text.startswith("apple id"):
        return "username"
    return "text"


def credential_items(store) -> list[dict]:
    """The window's view of a CredentialStore: one dict per saved password."""
    items = []
    for credential in store.all():
        data = credential.public_dict()
        domain = str(data.get("domain") or "")
        data["wifi"] = domain.strip().lower() == "airport"
        data["site"] = domain if _HOST.match(domain) and not data["wifi"] else ""
        if data["wifi"]:
            data["name"] = data.get("username") or data.get("title") or "Wi-Fi"
        else:
            data["name"] = data.get("title") or data["site"] or domain or "Untitled"
        items.append(data)
    items.sort(key=lambda item: str(item["name"]).casefold())
    return items


class IcpBridge(QObject):
    message = pyqtSignal(dict)
    finished = pyqtSignal(int)

    def __init__(self, anisette_url: str | None = None):
        super().__init__()
        self.anisette_url = anisette_url or os.environ.get("ICP_ANISETTE_URL") or DEFAULT_ANISETTE_URL
        os.environ["ICP_ANISETTE_URL"] = self.anisette_url
        self._answers: queue.Queue = queue.Queue()
        self._thread: threading.Thread | None = None
        self._choices: list[dict] = []
        self._recent: list[str] = []
        self._username = ""
        self._password = ""

    @property
    def busy(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    # Window side -----------------------------------------------------------------------
    def start(self, username: str, password: str) -> None:
        self._username, self._password = username, password
        self._run(self._login)

    def sync(self) -> None:
        self._run(self._sync)

    def respond(self, kind: str, value) -> None:
        if not self.busy:
            raise RuntimeError("No operation is waiting for an answer")
        self._answers.put(value)

    def cancel(self) -> None:
        if self.busy:
            self._answers.put(Cancelled)

    def load_vault(self) -> list[dict]:
        from icp.vault.store import load_vault
        return credential_items(load_vault())

    def signed_in(self) -> bool:
        from icp.auth import session
        try:
            return bool((session.load() or {}).get("username"))
        except Exception:  # noqa: BLE001 - an unreadable session counts as signed out
            return False

    # Worker side -----------------------------------------------------------------------
    def _run(self, job) -> None:
        if self.busy:
            raise RuntimeError("Another operation is already running")
        while not self._answers.empty():
            self._answers.get_nowait()
        self._choices = []
        self._recent = []
        self._thread = threading.Thread(target=self._guarded, args=(job,), daemon=True)
        self._thread.start()

    def _guarded(self, job) -> None:
        from icp.cli import app as cli_app
        from icp.cli import ui
        saved = {name: getattr(ui, name) for name in
                 ("out", "step", "warn", "err", "ask", "secret", "confirm_yn")}
        # The window does not show Hide My Email, and fetching it signs in to a separate Apple
        # web session on every run; skipping it avoids extra (and failing) Apple sign-ins.
        saved_aliases = cli_app._fetch_aliases_best_effort
        cli_app._fetch_aliases_best_effort = lambda interactive: []
        ui.out = lambda msg="": self._status(msg)
        ui.step = self._step
        ui.warn = lambda msg: self._status(f"Warning: {msg}")
        ui.err = lambda msg: self.message.emit({"type": "error", "message": str(msg)})
        ui.ask = lambda msg: self._ask(msg, secret=False)
        ui.secret = lambda msg: self._ask(msg, secret=True)
        ui.confirm_yn = self._confirm
        code = 1
        try:
            code = job()
        except Cancelled:
            self.message.emit({"type": "error", "message": "Operation cancelled"})
        except Exception as error:  # noqa: BLE001 - surface any engine failure in the window
            self.message.emit({"type": "error", "message": f"{type(error).__name__}: {error}"})
        finally:
            for name, function in saved.items():
                setattr(ui, name, function)
            cli_app._fetch_aliases_best_effort = saved_aliases
            self._password = ""
            self.finished.emit(code)

    def _status(self, msg: str) -> None:
        if msg:
            self._recent = (self._recent + [str(msg)])[-4:]
            self.message.emit({"type": "status", "message": str(msg)})

    def _step(self, msg: str) -> None:
        match = _CHOICE_LINE.match(msg or "")
        if match:
            self._choices.append({"index": match.group(1), "name": match.group(2)})
            return
        self._status(msg)

    def _wait(self):
        answer = self._answers.get()
        if answer is Cancelled:
            raise Cancelled()
        return answer

    def _ask(self, msg: str, *, secret: bool) -> str:
        kind = classify_prompt(msg, secret)
        if kind == "username" and self._username:
            return self._username
        if kind == "password" and self._password:
            password, self._password = self._password, ""
            return password
        devices, self._choices = self._choices, []
        self._recent = []
        self.message.emit({"type": "prompt", "kind": kind, "message": msg.strip(), "devices": devices})
        return str(self._wait())

    def _confirm(self, msg: str) -> bool:
        context, self._recent = self._recent, []
        detail = "\n".join(context + [msg.strip()])
        self.message.emit({"type": "prompt", "kind": "confirm", "message": detail, "devices": []})
        return bool(self._wait())

    def _login(self) -> int:
        from icp.cli.app import cmd_login
        args = argparse.Namespace(anisette=self.anisette_url, username=self._username,
                                  no_save_password=False, debug=False)
        code = cmd_login(args)
        if code == 0:
            self.message.emit({"type": "passwords", "items": self.load_vault()})
        return code

    def _sync(self) -> int:
        from icp.cli.app import cmd_sync
        args = argparse.Namespace(anisette=self.anisette_url, background=False, force=True)
        code = cmd_sync(args)
        if code == 0:
            self.message.emit({"type": "passwords", "items": self.load_vault()})
        return code
