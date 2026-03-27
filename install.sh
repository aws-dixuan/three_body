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

# Check for Xcode command line tools
if ! command -v clang &> /dev/null; then
    echo "Error: Xcode command line tools required."
    echo "Install: xcode-select --install"
    exit 1
fi

# Build .saver bundle
echo "==> Compiling..."
rm -rf "$SAVER_DIR"
mkdir -p "$MACOS" "$RESOURCES"

clang -framework ScreenSaver -framework Foundation -framework AppKit \
    -bundle -O2 -o "$MACOS/$SAVER_NAME" \
    "$REPO_DIR/screensaver/wrapper/main.m"

cp "$REPO_DIR/screensaver/config.toml" "$RESOURCES/"

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
