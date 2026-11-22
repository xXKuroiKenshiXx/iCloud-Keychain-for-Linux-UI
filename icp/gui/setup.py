"""Guided setup of a local anisette service (Anisette-on-Wine) for the window.

Everything runs as the current user: no sudo, no system files. Missing system tools are only
reported, with the install command for the detected distribution, because installing them
needs the user's own administrator password. The Anisette-on-Wine source is cloned at a
pinned commit and verified before anything from it runs; Apple's iCloud for Windows files are
copied from a folder the user picks (they cannot be downloaded or redistributed)."""

from __future__ import annotations

import os
import shutil
import subprocess
import threading
import urllib.request
from pathlib import Path

ANISETTE_REPO = "https://github.com/Sank6/Anisette-on-Wine.git"
ANISETTE_COMMIT = "cfb858ce36e6c6a17e7230c89146deb4ff71a417"
DEFAULT_PORT = 6969
DEFAULT_URL = f"http://127.0.0.1:{DEFAULT_PORT}"
REQUIRED_DLLS = ("CoreFoundation.dll", "AOSKit.dll", "CoreADI64.dll")

TOOLS = {
    "git": ("git",),
    "wine": ("wine64", "wine"),
    "cmake": ("cmake",),
    "mingw": ("x86_64-w64-mingw32-g++",),
    "python3": ("python3",),
}
PACKAGES = {
    "apt": ("sudo apt install", {"git": "git", "wine": "wine64", "cmake": "cmake", "mingw": "g++-mingw-w64-x86-64", "python3": "python3"}),
    "dnf": ("sudo dnf install", {"git": "git", "wine": "wine", "cmake": "cmake", "mingw": "mingw64-gcc-c++", "python3": "python3"}),
    "pacman": ("sudo pacman -S", {"git": "git", "wine": "wine", "cmake": "cmake", "mingw": "mingw-w64-gcc", "python3": "python"}),
    "zypper": ("sudo zypper install", {"git": "git", "wine": "wine", "cmake": "cmake", "mingw": "mingw64-cross-gcc-c++", "python3": "python3"}),
}


def data_dir() -> Path:
    base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    return Path(base) / "icloud-keychain"


def tool_dir() -> Path:
    return data_dir() / "anisette-on-wine"


def icloud_dir() -> Path:
    return data_dir() / "icloud"


def missing_tools() -> list[str]:
    return [name for name, binaries in TOOLS.items() if not any(shutil.which(b) for b in binaries)]


def install_command(missing: list[str]) -> str:
    """The package-manager command for the missing tools, or "" when none or unknown."""
    if not missing:
        return ""
    for manager, (command, names) in PACKAGES.items():
        if shutil.which(manager):
            return f"{command} " + " ".join(names[tool] for tool in missing)
    return ""


def is_icloud_dir(path: str | Path) -> bool:
    folder = Path(path)
    return folder.is_dir() and all((folder / dll).is_file() for dll in REQUIRED_DLLS)


def find_icloud_dirs() -> list[str]:
    """iCloud for Windows folders this computer can already see (WSL drives, earlier copies)."""
    found: list[str] = []
    candidates = [icloud_dir()]
    apps = Path("/mnt/c/Program Files/WindowsApps")
    try:
        candidates += sorted(apps.glob("AppleInc.iCloud_*_x64__*/iCloud"), reverse=True)
    except OSError:
        pass
    candidates.append(Path.home() / ".local/share/icloud-dlls/iCloud")
    for folder in candidates:
        try:
            if is_icloud_dir(folder) and str(folder) not in found:
                found.append(str(folder))
        except OSError:
            continue
    return found


def find_installed_tool() -> Path | None:
    """An Anisette-on-Wine checkout that is already provisioned, if any."""
    prefix = Path(os.environ.get("ANISETTE_ON_WINE_HOME") or Path.home() / ".local/share/anisette-on-wine") / "prefix"
    if not prefix.is_dir():
        return None
    for folder in (tool_dir(), Path.home() / "apps/anisette-on-wine"):
        if (folder / "anisette-on-wine").is_file() and (folder / "bin/anisette-helper.exe").is_file():
            return folder
    return None


def healthy(url: str = DEFAULT_URL, timeout: float = 3) -> bool:
    try:
        with urllib.request.urlopen(url.rstrip("/") + "/healthz", timeout=timeout) as response:
            return response.status == 200
    except Exception:  # noqa: BLE001 - any failure means "not answering"
        return False


def start_service(folder: Path, port: int = DEFAULT_PORT) -> None:
    """Starts `anisette-on-wine serve` on loopback in the background (no-op if answering)."""
    if healthy(f"http://127.0.0.1:{port}", timeout=1):
        return
    log = open(data_dir() / "anisette.log", "ab")
    subprocess.Popen([str(folder / "anisette-on-wine"), "serve", "--host", "127.0.0.1", "--port", str(port)],
                     cwd=folder, stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)


def wine_path(path: Path) -> str:
    return "Z:" + str(path).replace("/", "\\")


class Installer:
    """Runs the install steps in a thread, reporting each line through `report(kind, text)`:
    kind is "step", "line", "done", or "error"."""

    def __init__(self, icloud_source: str, report):
        self.icloud_source = Path(icloud_source)
        self.report = report
        self.thread: threading.Thread | None = None

    def start(self) -> None:
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self) -> None:
        try:
            data_dir().mkdir(parents=True, exist_ok=True)
            os.chmod(data_dir(), 0o700)
            self.report("step", "copy")
            target = icloud_dir()
            if self.icloud_source.resolve() != target.resolve():
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(self.icloud_source, target)
            os.chmod(target, 0o700)
            if not is_icloud_dir(target):
                raise RuntimeError("the copied folder is missing iCloud libraries")

            self.report("step", "download")
            folder = tool_dir()
            if not (folder / ".git").is_dir():
                if folder.exists():
                    shutil.rmtree(folder)
                self._run_cmd(["git", "clone", "--quiet", ANISETTE_REPO, str(folder)], data_dir())
            self._run_cmd(["git", "-c", "advice.detachedHead=false", "checkout", "--quiet", ANISETTE_COMMIT], folder)
            head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=folder, capture_output=True, text=True, check=True).stdout.strip()
            if head != ANISETTE_COMMIT:
                raise RuntimeError("downloaded Anisette-on-Wine does not match the reviewed version")

            tool = str(folder / "anisette-on-wine")
            self.report("step", "build")
            self._run_cmd([tool, "build-helper"], folder)
            self.report("step", "prepare")
            if not (Path.home() / ".local/share/anisette-on-wine/prefix").is_dir():
                self._run_cmd([tool, "init"], folder)
            self._run_cmd([tool, "configure", "--apple-support-dir", wine_path(target),
                           "--internet-services-dir", wine_path(target)], folder)
            self.report("step", "provision")
            self._run_cmd([tool, "provision"], folder, allow_fail=True)
            self._run_cmd([tool, "doctor"], folder)
            self.report("step", "start")
            start_service(folder)
            for _ in range(30):
                if healthy(timeout=1):
                    break
                threading.Event().wait(1)
            else:
                raise RuntimeError("the anisette service did not start; see anisette.log")
            self.report("done", str(folder))
        except Exception as error:  # noqa: BLE001 - every failure is shown in the window
            self.report("error", str(error))

    def _run_cmd(self, cmd: list[str], cwd: Path, allow_fail: bool = False) -> None:
        process = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   stdin=subprocess.DEVNULL, text=True, errors="replace")
        for line in process.stdout:
            line = line.rstrip()
            if line:
                self.report("line", line[:300])
        if process.wait() != 0 and not allow_fail:
            raise RuntimeError(f"{Path(cmd[0]).name} {cmd[1] if len(cmd) > 1 else ''} failed")
