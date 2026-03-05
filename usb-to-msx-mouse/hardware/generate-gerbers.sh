#!/bin/bash
# generate-gerbers.sh — Generate Gerber and drill files from KiCad PCB
#
# Requires KiCad 8 CLI tools (kicad-cli).
# Install KiCad 8: https://www.kicad.org/download/
#
# Usage:
#   cd hardware/
#   ./generate-gerbers.sh
#
# Output goes to gerbers/ directory, ready to ZIP and upload to JLCPCB.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PCB_FILE="${SCRIPT_DIR}/kicad/usb-to-msx-mouse.kicad_pcb"
OUTPUT_DIR="${SCRIPT_DIR}/gerbers"

# Check for kicad-cli
if ! command -v kicad-cli &> /dev/null; then
    echo "Error: kicad-cli not found."
    echo "Install KiCad 8 from https://www.kicad.org/download/"
    echo ""
    echo "On macOS: brew install --cask kicad"
    echo "On Ubuntu: sudo add-apt-repository ppa:kicad/kicad-8.0-releases && sudo apt install kicad"
    exit 1
fi

# Check PCB file exists
if [ ! -f "$PCB_FILE" ]; then
    echo "Error: PCB file not found at $PCB_FILE"
    echo "Run generate_pcb.py first, then open in KiCad to finalize routing."
    exit 1
fi

# Clean output directory
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

echo "Generating Gerber files..."

# Generate Gerber files for each layer
kicad-cli pcb export gerbers \
    --output "$OUTPUT_DIR/" \
    --layers "F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts" \
    --subtract-soldermask \
    --use-drill-file-origin \
    "$PCB_FILE"

echo "Generating drill files..."

# Generate drill files
kicad-cli pcb export drill \
    --output "$OUTPUT_DIR/" \
    --format excellon \
    --drill-origin plot \
    --excellon-units mm \
    --excellon-zeros-format decimal \
    --generate-map \
    --map-format gerberx2 \
    "$PCB_FILE"

echo ""
echo "Gerber files generated in: $OUTPUT_DIR/"
echo ""
echo "To order from JLCPCB:"
echo "  1. ZIP the gerbers/ directory"
echo "  2. Upload to https://cart.jlcpcb.com/quote"
echo "  3. Select: 2 layers, 1.6mm, HASL lead-free"
echo "  4. Enable SMT Assembly (Economic, Top Side)"
echo "  5. Upload BOM: jlcpcb/bom-jlcpcb.csv"
echo "  6. Upload CPL: jlcpcb/cpl-jlcpcb.csv"
echo ""

# Create ZIP for upload
cd "$OUTPUT_DIR"
ZIP_NAME="usb-to-msx-mouse-gerbers.zip"
zip -j "../${ZIP_NAME}" ./*
echo "Created: ${ZIP_NAME}"
echo "Upload this ZIP to JLCPCB."
