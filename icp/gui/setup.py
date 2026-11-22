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
    "apt": ("sudo apt install", {"git": "git", "wine": "wine64", "cmake": "cmake", "mingw": "g++-mingw-w64-x86-64", "python3": "python3", "podman": "podman", "rust": "rustup", "cc": "build-essential"}),
    "dnf": ("sudo dnf install", {"git": "git", "wine": "wine", "cmake": "cmake", "mingw": "mingw64-gcc-c++", "python3": "python3", "podman": "podman", "rust": "rustup", "cc": "gcc"}),
    "pacman": ("sudo pacman -S", {"git": "git", "wine": "wine", "cmake": "cmake", "mingw": "mingw-w64-gcc", "python3": "python", "podman": "podman", "rust": "rustup", "cc": "gcc"}),
    "zypper": ("sudo zypper install", {"git": "git", "wine": "wine", "cmake": "cmake", "mingw": "mingw64-cross-gcc-c++", "python3": "python3", "podman": "podman", "rust": "rustup", "cc": "gcc"}),
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


INSTALL_ARGS = {
    "apt": ["apt-get", "install", "-y"],
    "dnf": ["dnf", "install", "-y"],
    "pacman": ["pacman", "-S", "--noconfirm", "--needed"],
    "zypper": ["zypper", "--non-interactive", "install"],
}


def install_argv(missing: list[str]) -> list[str]:
    """`pkexec <package manager> install …` for the missing tools, or [] when not possible.
    pkexec asks for the administrator password in the desktop's own dialog; this app never
    sees or stores it."""
    if not missing or not shutil.which("pkexec"):
        return []
    for manager, (_, names) in PACKAGES.items():
        if shutil.which(manager):
            binary = shutil.which(INSTALL_ARGS[manager][0]) or INSTALL_ARGS[manager][0]
            return ["pkexec", binary, *INSTALL_ARGS[manager][1:], *[names[tool] for tool in missing]]
    return []


def install_tools(missing: list[str], report) -> None:
    """Runs the pkexec install in a thread; reports "line", then "tools-done" or "tools-error"."""
    def run():
        argv = install_argv(missing)
        if not argv:
            report("tools-error", "pkexec or a supported package manager is not available")
            return
        try:
            process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       stdin=subprocess.DEVNULL, text=True, errors="replace")
            for line in process.stdout:
                if line.strip():
                    report("line", line.rstrip()[:300])
            code = process.wait()
        except OSError as error:
            report("tools-error", str(error))
            return
        # 126/127: the user dismissed the password dialog or no authentication agent runs.
        report("tools-done" if code == 0 else "tools-error", "" if code == 0 else f"exit {code}")
    threading.Thread(target=run, daemon=True).start()


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
    """True when an anisette service answers: Anisette-on-Wine has /healthz, anisette-v3-server
    answers its root with headers."""
    for path in ("/healthz", "/"):
        try:
            with urllib.request.urlopen(url.rstrip("/") + path, timeout=timeout) as response:
                if response.status == 200:
                    return True
        except Exception:  # noqa: BLE001 - try the next form
            continue
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


# ---- desktop integration for the AppImage ---------------------------------------------------
APP_ID = "icloud-keychain"


def appimage_path() -> str:
    """The running AppImage file, or "" when not started from one."""
    path = os.environ.get("APPIMAGE", "")
    return path if path and Path(path).is_file() else ""


def _applications_dir() -> Path:
    base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    return Path(base)


def desktop_entry() -> Path:
    return _applications_dir() / "applications" / f"{APP_ID}.desktop"


def is_integrated() -> bool:
    return desktop_entry().is_file()


def integrate(icon_source: Path) -> str:
    """Copies the AppImage to ~/Applications, adds a menu entry and icon; returns the new path."""
    source = Path(appimage_path())
    if not source.is_file():
        raise RuntimeError("not running from an AppImage")
    target_dir = Path.home() / "Applications"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "iCloud-Keychain.AppImage"
    if source.resolve() != target.resolve():
        shutil.copy2(source, target)
    os.chmod(target, 0o755)
    icon_dir = _applications_dir() / "icons/hicolor/scalable/apps"
    icon_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(icon_source, icon_dir / f"{APP_ID}.svg")
    entry = desktop_entry()
    entry.parent.mkdir(parents=True, exist_ok=True)
    entry.write_text("\n".join([
        "[Desktop Entry]", "Type=Application", "Name=iCloud Keychain", "Comment=iCloud Passwords on Linux",
        f'Exec="{target}" %U', f"Icon={APP_ID}", "Categories=Utility;Security;", "Terminal=false",
        f"StartupWMClass={APP_ID}", ""]), encoding="utf-8")
    os.chmod(entry, 0o644)
    if shutil.which("update-desktop-database"):
        subprocess.run(["update-desktop-database", str(entry.parent)], capture_output=True, check=False)
    return str(target)


def unintegrate() -> None:
    for path in (desktop_entry(), _applications_dir() / f"icons/hicolor/scalable/apps/{APP_ID}.svg"):
        try:
            path.unlink()
        except OSError:
            pass


# ---- anisette-v3-server in a container ------------------------------------------------------
CONTAINER_IMAGE = ("docker.io/dadoum/anisette-v3-server@"
                   "sha256:d551c75454bcbee68dc262d4247d5f87fa309dfc8f2125644d333c648596e3c7")
CONTAINER_NAME = "icloud-keychain-anisette"


def container_runtime() -> str:
    """podman (rootless, preferred) or docker, or "" when neither is installed."""
    for name in ("podman", "docker"):
        path = shutil.which(name)
        if path:
            return path
    return ""


def container_command() -> list[str]:
    """Runs Dadoum's anisette-v3-server, reachable only from this computer, restarting with it."""
    return [container_runtime(), "run", "-d", "--restart", "unless-stopped", "--name", CONTAINER_NAME,
            "-p", f"127.0.0.1:{DEFAULT_PORT}:6969",
            "--volume", f"{CONTAINER_NAME}:/home/Alcoholic/.config/anisette-v3/lib/", CONTAINER_IMAGE]


def start_container(report) -> None:
    """Pulls the pinned image and starts the container in a thread; reports like Installer."""
    def run():
        runtime = container_runtime()
        if not runtime:
            report("error", "Docker or Podman is not installed")
            return
        try:
            report("step", "pull")
            exists = subprocess.run([runtime, "container", "inspect", CONTAINER_NAME],
                                    capture_output=True, text=True).returncode == 0
            cmd = [runtime, "start", CONTAINER_NAME] if exists else container_command()
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       stdin=subprocess.DEVNULL, text=True, errors="replace")
            for line in process.stdout:
                if line.strip():
                    report("line", line.rstrip()[:300])
            if process.wait() != 0:
                raise RuntimeError(f"{Path(runtime).name} could not start the container")
            report("step", "start")
            for _ in range(60):
                if healthy(timeout=1):
                    break
                threading.Event().wait(1)
            else:
                raise RuntimeError("the container started but the service is not answering yet")
            report("done", "container")
        except Exception as error:  # noqa: BLE001
            report("error", str(error))
    threading.Thread(target=run, daemon=True).start()


def autostart_container() -> None:
    runtime = container_runtime()
    if runtime:
        subprocess.run([runtime, "start", CONTAINER_NAME], capture_output=True, check=False)


# ---- anisette-rs (native Rust) -------------------------------------------------------------
RS_REPO = "https://github.com/Sank6/anisette-rs.git"
RS_COMMIT = "c73c5204e4eefffb0ef3100266504c4da0166305"
RS_MIN_RUST = (1, 90)
APPLE_ROOT_URL = "https://www.apple.com/appleca/AppleIncRootCertificate.cer"
APPLE_ROOT_SHA256 = "b0b1730ecbc7ff4505142c49f1295e6eda6bcaed7e2c68c5be91b5a11001f024"


def rs_dir() -> Path:
    return data_dir() / "anisette-rs"


def rs_state_dir() -> Path:
    return data_dir() / "anisette-rs-state"


def rs_binary() -> Path:
    return rs_dir() / "target" / "release" / "anisette-rs"


def cargo_path() -> str:
    for candidate in (shutil.which("cargo"), str(Path.home() / ".cargo/bin/cargo")):
        if candidate and Path(candidate).is_file():
            return candidate
    return ""


def rust_ok() -> bool:
    """True when cargo exists and is at least the version anisette-rs needs."""
    cargo = cargo_path()
    if not cargo:
        return False
    try:
        out = subprocess.run([cargo, "--version"], capture_output=True, text=True, timeout=20).stdout
        major, minor = (int(part) for part in out.split()[1].split(".")[:2])
        return (major, minor) >= RS_MIN_RUST
    except (OSError, ValueError, IndexError, subprocess.SubprocessError):
        return False


def rs_missing() -> list[str]:
    """System packages still needed. With rustup present, the toolchain is installed per user."""
    missing = [] if shutil.which("git") else ["git"]
    if not rust_ok() and not rustup_path():
        missing.append("rust")
    if not shutil.which("cc") and not shutil.which("gcc"):
        missing.append("cc")
    return missing


def rustup_path() -> str:
    for candidate in (shutil.which("rustup"), str(Path.home() / ".cargo/bin/rustup")):
        if candidate and Path(candidate).is_file():
            return candidate
    return ""


def random_windows_hardware() -> dict:
    """A plausible, random Windows machine profile for a fresh anisette-rs identity. It belongs
    to no real computer and is kept private on this one."""
    import secrets
    import uuid
    mac = [secrets.randbelow(256) for _ in range(6)]
    mac[0] = (mac[0] & 0xFC) | 0x02          # locally administered, unicast
    product = f"00330-{secrets.randbelow(90000) + 10000}-{secrets.randbelow(90000) + 10000}-AA{secrets.randbelow(900) + 100}"
    name = "DESKTOP-" + "".join(secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ0123456789") for _ in range(7))
    return {
        "mac_address": mac,
        "volume_serial": secrets.randbelow(2 ** 32),
        "product_id": list(product.encode()),
        "processor_name": list(b"Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz"),
        "bios_version": list(b"ALASKA - 1072009"),
        "computer_name": name,
        "hardware_profile_guid": "{" + str(uuid.uuid4()) + "}",
    }


def _private_write(path: Path, data: bytes) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(data)


def apple_root_certificate() -> Path:
    """Apple's root certificate, downloaded once and checked against its published SHA-256."""
    import hashlib
    target = data_dir() / "AppleIncRootCertificate.cer"
    if target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest() == APPLE_ROOT_SHA256:
        return target
    with urllib.request.urlopen(APPLE_ROOT_URL, timeout=20) as response:
        data = response.read(64 * 1024)
    if hashlib.sha256(data).hexdigest() != APPLE_ROOT_SHA256:
        raise RuntimeError("Apple's root certificate did not match its published fingerprint")
    _private_write(target, data)
    return target


def start_rs(port: int = DEFAULT_PORT) -> None:
    if healthy(f"http://127.0.0.1:{port}", timeout=1):
        return
    log = open(data_dir() / "anisette-rs.log", "ab")
    subprocess.Popen([str(rs_binary()), "--state-dir", str(rs_state_dir()), "serve",
                      "--host", "127.0.0.1", "--port", str(port)],
                     stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)


class RsInstaller(Installer):
    """Builds anisette-rs at a pinned commit, provisions a fresh private identity, serves it."""

    def __init__(self, report, port: int = DEFAULT_PORT):
        super().__init__("", report)
        self.port = port

    def _run(self) -> None:
        try:
            data_dir().mkdir(parents=True, exist_ok=True)
            os.chmod(data_dir(), 0o700)
            self.report("step", "download")
            folder = rs_dir()
            if not (folder / ".git").is_dir():
                if folder.exists():
                    shutil.rmtree(folder)
                self._run_cmd(["git", "clone", "--quiet", RS_REPO, str(folder)], data_dir())
            self._run_cmd(["git", "-c", "advice.detachedHead=false", "checkout", "--quiet", RS_COMMIT], folder)
            head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=folder, capture_output=True, text=True, check=True).stdout.strip()
            if head != RS_COMMIT:
                raise RuntimeError("downloaded anisette-rs does not match the reviewed version")
            self.report("step", "build")
            if not rust_ok():
                rustup = rustup_path()
                if not rustup:
                    raise RuntimeError("Rust is not installed")
                self._run_cmd([rustup, "toolchain", "install", "stable", "--profile", "minimal"], folder)
                self._run_cmd([rustup, "default", "stable"], folder)
            self._run_cmd([cargo_path(), "build", "--release", "--locked"], folder)
            self.report("step", "provision")
            state = rs_state_dir()
            state.mkdir(parents=True, exist_ok=True)
            os.chmod(state, 0o700)
            hardware = data_dir() / "anisette-rs-hardware.json"
            if not hardware.is_file():
                import json
                _private_write(hardware, json.dumps(random_windows_hardware()).encode())
            cert = apple_root_certificate()
            self._run_cmd([str(rs_binary()), "--state-dir", str(state), "provision",
                           "--apple-root", str(cert), "--hardware", str(hardware)], folder)
            self.report("step", "start")
            start_rs(self.port)
            for _ in range(30):
                if healthy(f"http://127.0.0.1:{self.port}", timeout=1):
                    break
                threading.Event().wait(1)
            else:
                raise RuntimeError("anisette-rs did not start; see anisette-rs.log")
            self.report("done", "rs")
        except Exception as error:  # noqa: BLE001 - every failure is shown in the window
            self.report("error", str(error))


def find_rs() -> bool:
    return rs_binary().is_file() and (rs_state_dir()).is_dir()
