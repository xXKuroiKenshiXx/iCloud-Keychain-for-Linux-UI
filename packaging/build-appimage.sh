#!/usr/bin/env bash
# Builds dist/iCloud-Keychain-x86_64.AppImage: a relocatable CPython, the engine with its
# pinned dependencies and PyQt6, and the Liquid Glass window. Every download is pinned and
# checked against its published SHA-256 before use.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY_URL="https://github.com/astral-sh/python-build-standalone/releases/download/20261026/cpython-3.12.16%2B20261026-x86_64-unknown-linux-gnu-install_only.tar.gz"
PY_SHA256="6a79e922e50006b601f29e688407659da1c2b86ebcd4e9c7254cf234be8b89de"
TOOL_URL="https://github.com/AppImage/appimagetool/releases/download/1.9.1/appimagetool-x86_64.AppImage"
TOOL_SHA256="ed4ce84f0d9caff66f50bcca6ff6f35aae54ce8135408b3fa33abfc3cb384eb0"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
APPDIR="$WORK/AppDir"
mkdir -p "$APPDIR/usr" "$ROOT/dist"

fetch() {  # url sha256 destination
    curl -fsSL --proto '=https' --tlsv1.2 -o "$3" "$1"
    echo "$2  $3" | sha256sum -c -
}

fetch "$PY_URL" "$PY_SHA256" "$WORK/python.tar.gz"
tar -xzf "$WORK/python.tar.gz" -C "$APPDIR/usr"
PY="$APPDIR/usr/python/bin/python3"

"$PY" -m pip install --no-cache-dir --disable-pip-version-check --no-compile \
    -c "$ROOT/packaging/constraints.txt" "$ROOT[gui]"
find "$APPDIR/usr/python" -name '__pycache__' -type d -prune -exec rm -rf {} +
rm -rf "$APPDIR/usr/python/lib/python3.12/test" "$APPDIR/usr/python/lib/python3.12/idlelib"

install -m 755 "$ROOT/packaging/AppRun" "$APPDIR/AppRun"
install -m 644 "$ROOT/packaging/icloud-keychain.desktop" "$APPDIR/icloud-keychain.desktop"
rsvg-convert -w 256 -h 256 "$ROOT/icp/gui/qml/icon.svg" -o "$APPDIR/icloud-keychain.png"
ln -s icloud-keychain.png "$APPDIR/.DirIcon"

fetch "$TOOL_URL" "$TOOL_SHA256" "$WORK/appimagetool"
chmod +x "$WORK/appimagetool"
OUT="$ROOT/dist/iCloud-Keychain-x86_64.AppImage"
ARCH=x86_64 "$WORK/appimagetool" --appimage-extract-and-run --no-appstream "$APPDIR" "$OUT"
(cd "$ROOT/dist" && sha256sum "$(basename "$OUT")" > "$(basename "$OUT").sha256")
echo "Built $OUT"
