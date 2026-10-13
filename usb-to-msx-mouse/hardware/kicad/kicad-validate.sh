#!/bin/bash
# kicad-validate.sh — Validate and normalize KiCad files via tombstone Docker
#
# Usage: ./kicad-validate.sh [command]
# Commands: drc, erc, normalize, gerbers, all (default: all)
#
# Syncs local KiCad files to tombstone, runs KiCad 9 in Docker,
# syncs results (reports + normalized files) back.

set -euo pipefail

TOMBSTONE="dyw@100.95.232.40"
REMOTE_DIR="/tmp/kicad-work"
LOCAL_DIR="$(cd "$(dirname "$0")" && pwd)"
CMD="${1:-all}"

echo "=== KiCad Validate (via tombstone Docker) ==="
echo "Local:   $LOCAL_DIR"
echo "Remote:  $TOMBSTONE:$REMOTE_DIR"
echo "Command: $CMD"
echo ""

# Sync KiCad project files to tombstone
echo "--- Uploading files ---"
ssh "$TOMBSTONE" "mkdir -p $REMOTE_DIR"
scp -q "$LOCAL_DIR"/*.kicad_pcb "$LOCAL_DIR"/*.kicad_sch "$LOCAL_DIR"/*.kicad_pro \
    "$TOMBSTONE:$REMOTE_DIR/" 2>/dev/null || true

# Run KiCad on tombstone
echo "--- Running KiCad 9 ---"
ssh "$TOMBSTONE" "~/kicad-service/run-kicad.sh $CMD $REMOTE_DIR"

# Sync results back
echo ""
echo "--- Downloading results ---"
# Get reports
scp -q "$TOMBSTONE:$REMOTE_DIR/"*-report.json "$LOCAL_DIR/" 2>/dev/null || true
# Get normalized PCB (if normalize or all)
if [ "$CMD" = "normalize" ] || [ "$CMD" = "all" ]; then
    scp -q "$TOMBSTONE:$REMOTE_DIR/"*.kicad_pcb "$LOCAL_DIR/"
    echo "Normalized PCB downloaded."
fi
# Get gerbers (if gerbers)
if [ "$CMD" = "gerbers" ]; then
    mkdir -p "$LOCAL_DIR/../../gerbers"
    scp -q -r "$TOMBSTONE:$REMOTE_DIR/gerbers/" "$LOCAL_DIR/../../gerbers/"
    echo "Gerbers downloaded."
fi

echo ""
echo "=== Done ==="
