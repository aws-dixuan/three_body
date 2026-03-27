#!/bin/bash
# Install Three-Body Screensaver on macOS
# Usage: ./install.sh
set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SAVER_NAME="ThreeBodySaver"
SAVER_DIR="$HOME/Library/Screen Savers/${SAVER_NAME}.saver"
CONTENTS="${SAVER_DIR}/Contents"
MACOS="${CONTENTS}/MacOS"
RESOURCES="${CONTENTS}/Resources"

echo "==> Installing Three-Body Screensaver..."

# Check for uv
if ! command -v uv &> /dev/null; then
    echo "Error: uv is required."
    echo "Install: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# Check for Xcode command line tools (need clang)
if ! command -v clang &> /dev/null; then
    echo "Error: Xcode command line tools required."
    echo "Install: xcode-select --install"
    exit 1
fi

# Install Python deps
echo "==> Installing dependencies..."
uv sync --group screensaver --project "$REPO_DIR"

VENV_PYTHON="${REPO_DIR}/.venv/bin/python"
if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: venv python not found at ${VENV_PYTHON}"
    exit 1
fi

# Build .saver bundle
echo "==> Building .saver bundle..."
rm -rf "$SAVER_DIR"
mkdir -p "$MACOS" "$RESOURCES"

# Compile the Objective-C wrapper
clang -framework ScreenSaver -framework Foundation -framework AppKit \
    -bundle -o "$MACOS/$SAVER_NAME" \
    "$REPO_DIR/screensaver/wrapper/main.m"

# Copy resources
cp "$REPO_DIR/screensaver/fullscreen_saver.py" "$RESOURCES/"
cp "$REPO_DIR/screensaver/config.toml" "$RESOURCES/"
echo "$VENV_PYTHON" > "$RESOURCES/python_path.txt"

# Create Info.plist
cat > "$CONTENTS/Info.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>$SAVER_NAME</string>
    <key>CFBundleIdentifier</key>
    <string>com.threebody.screensaver</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleExecutable</key>
    <string>$SAVER_NAME</string>
    <key>CFBundlePackageType</key>
    <string>BNDL</string>
    <key>NSPrincipalClass</key>
    <string>ThreeBodySaver</string>
</dict>
</plist>
PLIST

echo ""
echo "Installed to: $SAVER_DIR"
echo ""
echo "Next steps:"
echo "  1. Open System Settings > Screen Saver"
echo "  2. Select 'ThreeBodySaver'"
echo "  3. Test: open -a ScreenSaverEngine"
echo ""
echo "To customize: edit $RESOURCES/config.toml"
echo "To uninstall: ./uninstall.sh"
