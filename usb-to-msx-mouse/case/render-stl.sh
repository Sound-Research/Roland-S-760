#!/bin/bash
# render-stl.sh — Render OpenSCAD case to STL files for 3D printing
#
# Requires OpenSCAD: https://openscad.org/downloads.html
# macOS: brew install --cask openscad
#
# Usage:
#   cd case/
#   ./render-stl.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCAD_FILE="${SCRIPT_DIR}/usb-to-msx-mouse-case.scad"

if ! command -v openscad &> /dev/null; then
    echo "Error: openscad not found."
    echo "Install: brew install --cask openscad"
    exit 1
fi

echo "Rendering bottom half..."
openscad -o "${SCRIPT_DIR}/case-bottom.stl" -D 'part="bottom"' "$SCAD_FILE"
echo "  → case-bottom.stl"

echo "Rendering top half..."
openscad -o "${SCRIPT_DIR}/case-top.stl" -D 'part="top"' "$SCAD_FILE"
echo "  → case-top.stl"

echo ""
echo "Done. Print both STLs with:"
echo "  Material: PLA"
echo "  Layer height: 0.2mm"
echo "  Infill: 20%"
echo "  Supports: none needed"
