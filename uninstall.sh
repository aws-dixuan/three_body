#!/bin/bash
# Uninstall Three-Body Screensaver
set -e
SAVER="$HOME/Library/Screen Savers/ThreeBodySaver.saver"
APP="/Applications/Three Body Screensaver.app"
[ -d "$SAVER" ] && rm -rf "$SAVER" && echo "Removed $SAVER"
[ -d "$APP" ] && rm -rf "$APP" && echo "Removed $APP"
echo "Uninstalled."
