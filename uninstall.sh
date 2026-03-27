#!/bin/bash
# Uninstall Three-Body Screensaver
set -e
SAVER="$HOME/Library/Screen Savers/ThreeBodySaver.saver"
if [ -d "$SAVER" ]; then
    rm -rf "$SAVER"
    echo "Uninstalled ThreeBodySaver."
else
    echo "Not installed."
fi
