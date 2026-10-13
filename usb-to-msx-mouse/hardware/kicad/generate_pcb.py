#!/usr/bin/env python3
"""
generate_pcb.py — Generate KiCad 8 PCB layout for USB-to-MSX mouse adapter.

Creates usb-to-msx-mouse.kicad_pcb with:
    - Board outline: 20 x 42mm (2-layer, 1.6mm thick)
    - Compact mouSTer-like dongle form factor
    - DB9 on one short end (no mounting holes — ears overhang board edges)
    - USB-A on the opposite short end
    - All footprints placed with correct net assignments
    - Ground zones on both copper layers

Usage:
    python3 generate_pcb.py

After generation, validate with kicad-cli, normalize with pcbnew, then upload to Quilter AI.
"""

import uuid
import os

def uid():
    return str(uuid.uuid4())

# ─── Net definitions ────────────────────────────────────────────────────────
# Net number → net name. Net 0 is "unconnected" in KiCad.
NETS = {
    0: "",
    1: "GND",
    2: "+5V",
    3: "+3V3",
    4: "USB_DP",
    5: "USB_DM",
    6: "GPIO2",
    7: "GPIO3",
    8: "GPIO4",
    9: "GPIO5",
    10: "GPIO6",
    11: "GPIO7",
    12: "GPIO8",
    13: "GPIO25",
    14: "QSPI_SCLK",
    15: "QSPI_SD0",
    16: "QSPI_SD1",
    17: "QSPI_SD2",
    18: "QSPI_SD3",
    19: "QSPI_SS",
    20: "XIN",
    21: "XOUT",
    22: "DVDD",
    23: "RUN",
    24: "USB_DM_R",    # Between USB connector and series resistor
    25: "USB_DP_R",    # Between USB connector and series resistor
    26: "VBUS_FUSED",  # Between polyfuse and USB-A VBUS
    27: "STROBE_5V",   # DB-9 pin 8 before voltage divider
    28: "STROBE_DIV",  # Midpoint of voltage divider (= GPIO8)
    29: "DB9_D0",      # 74HCT245 B1 → DB-9 pin 1
    30: "DB9_D1",      # 74HCT245 B2 → DB-9 pin 2
    31: "DB9_D2",      # 74HCT245 B3 → DB-9 pin 3
    32: "DB9_D3",      # 74HCT245 B4 → DB-9 pin 4
    33: "DB9_LBTN",    # 74HCT245 B5 → DB-9 pin 6
    34: "DB9_RBTN",    # 74HCT245 B6 → DB-9 pin 7
    35: "5V_MSX",      # DB-9 pin 5 before diode
    36: "LED_A",       # Between LED resistor and LED anode
}

def net_str(net_num):
    """Format a net reference for a pad."""
    name = NETS.get(net_num, "")
    if net_num == 0:
        return '(net 0 "")'
    return f'(net {net_num} "{name}")'


# ─── Board dimensions ───────────────────────────────────────────────────────
# Compact mouSTer-like dongle: DB9 on top, USB-A on bottom, components between.
# Width 20mm: DB9 mounting ears overhang board edges (signal pins only ~11mm span).
# Length 42mm: components stack vertically since less horizontal room.
OX, OY = 100, 100  # Board origin (top-left corner)
BW = 22             # Board width (X axis — signal pins fit, mounting ears overhang)
BL = 42             # Board length (Y axis — dongle: DB9 → components → USB-A)


def board_outline():
    """Board outline as four gr_line segments (most compatible with third-party parsers)."""
    x1, y1 = OX, OY
    x2, y2 = OX + BW, OY + BL
    lines = []
    for start, end in [
        ((x1, y1), (x2, y1)),  # top
        ((x2, y1), (x2, y2)),  # right
        ((x2, y2), (x1, y2)),  # bottom
        ((x1, y2), (x1, y1)),  # left
    ]:
        lines.append(f'  (gr_line (start {start[0]} {start[1]}) (end {end[0]} {end[1]}) '
                     f'(stroke (width 0.05) (type default)) (layer "Edge.Cuts") (uuid "{uid()}"))')
    return '\n'.join(lines)


# ─── Footprint generators with net assignments ─────────────────────────────

def fmt(v):
    """Format a float with 6 decimal max, stripping trailing zeros."""
    return f"{v:.6f}".rstrip('0').rstrip('.')


def pad_smd(num, x, y, w, h, net, angle=0, shape="roundrect", layer="F.Cu"):
    """Generate a single SMD pad with net assignment."""
    layers = f'"{layer}" "{layer[0]}.Paste" "{layer[0]}.Mask"'
    rr = ' (roundrect_rratio 0.25)' if shape == "roundrect" else ""
    return f'    (pad "{num}" smd {shape} (at {fmt(x)} {fmt(y)} {angle}) (size {fmt(w)} {fmt(h)}) (layers {layers}){rr} {net_str(net)} (uuid "{uid()}"))'


def pad_th(num, x, y, pad_d, drill_d, net, angle=0, shape="circle", oval_w=None, oval_h=None):
    """Generate a single through-hole pad with net assignment."""
    if shape == "oval" and oval_w and oval_h:
        size = f"{fmt(oval_w)} {fmt(oval_h)}"
    else:
        size = f"{fmt(pad_d)} {fmt(pad_d)}"
    return f'    (pad "{num}" thru_hole {shape} (at {fmt(x)} {fmt(y)} {angle}) (size {size}) (drill {fmt(drill_d)}) (layers "*.Cu" "*.Mask") {net_str(net)} (uuid "{uid()}"))'


def fp_header(fp_lib, ref, value, x, y, angle=0, attr="smd"):
    """Footprint header boilerplate. attr should be 'smd' or 'through_hole'."""
    return f'''  (footprint "{fp_lib}"
    (layer "F.Cu")
    (uuid "{uid()}")
    (at {x} {y} {angle})
    (path "/")
    (attr {attr})
    (property "Reference" "{ref}" (at 0 -2 {angle}) (layer "F.SilkS") (uuid "{uid()}") (effects (font (size 0.8 0.8) (thickness 0.12))))
    (property "Value" "{value}" (at 0 2 {angle}) (layer "F.Fab") (uuid "{uid()}") (effects (font (size 0.8 0.8) (thickness 0.12))))
    (property "Footprint" "{fp_lib}" (at 0 0 {angle}) (layer "F.Fab") (uuid "{uid()}") (effects (font (size 1.27 1.27) (thickness 0.15)) hide))'''


def fp_0402(ref, value, x, y, nets, angle=0):
    """0402 2-pad: nets = {1: net_num, 2: net_num}."""
    lines = [fp_header("Resistor_SMD:R_0402_1005Metric", ref, value, x, y, angle)]
    lines.append(pad_smd("1", -0.48, 0, 0.56, 0.5, nets[1], angle))
    lines.append(pad_smd("2", 0.48, 0, 0.56, 0.5, nets[2], angle))
    lines.append("  )")
    return '\n'.join(lines)


def fp_0603_led(ref, value, x, y, nets, angle=0):
    """0603 LED: nets = {1: anode, 2: cathode}."""
    lines = [fp_header("LED_SMD:LED_0603_1608Metric", ref, value, x, y, angle)]
    lines.append(pad_smd("1", -0.75, 0, 0.8, 0.75, nets[1], angle))
    lines.append(pad_smd("2", 0.75, 0, 0.8, 0.75, nets[2], angle))
    lines.append("  )")
    return '\n'.join(lines)


def fp_0805_fuse(ref, value, x, y, nets, angle=0):
    lines = [fp_header("Fuse:Fuse_0805_2012Metric", ref, value, x, y, angle)]
    lines.append(pad_smd("1", -0.95, 0, 1.0, 1.0, nets[1], angle))
    lines.append(pad_smd("2", 0.95, 0, 1.0, 1.0, nets[2], angle))
    lines.append("  )")
    return '\n'.join(lines)


def fp_sod323(ref, value, x, y, nets, angle=0):
    """SOD-323 diode: nets = {1: cathode(K), 2: anode(A)}."""
    lines = [fp_header("Diode_SMD:D_SOD-323", ref, value, x, y, angle)]
    lines.append(pad_smd("1", -1.15, 0, 0.8, 0.6, nets[1], angle))
    lines.append(pad_smd("2", 1.15, 0, 0.8, 0.6, nets[2], angle))
    lines.append("  )")
    return '\n'.join(lines)


def fp_sot23_ldo(ref, value, x, y, nets, angle=0):
    """SOT-23 XC6206: pin 1=GND, pin 2=VOUT, pin 3=VIN."""
    lines = [fp_header("Package_TO_SOT_SMD:SOT-23", ref, value, x, y, angle)]
    lines.append(pad_smd("1", -0.95, 1.1, 0.8, 0.9, nets[1], angle))
    lines.append(pad_smd("2", 0.95, 1.1, 0.8, 0.9, nets[2], angle))
    lines.append(pad_smd("3", 0, -1.1, 0.8, 0.9, nets[3], angle))
    lines.append("  )")
    return '\n'.join(lines)


def fp_crystal_3225(ref, value, x, y, nets, angle=0):
    """3225 crystal: pin 1=XIN, pin 2=GND, pin 3=XOUT, pin 4=GND."""
    lines = [fp_header("Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm", ref, value, x, y, angle)]
    lines.append(pad_smd("1", -1.1, -0.85, 1.2, 1.0, nets[1], angle))
    lines.append(pad_smd("2", 1.1, -0.85, 1.2, 1.0, nets[2], angle))
    lines.append(pad_smd("3", 1.1, 0.85, 1.2, 1.0, nets[3], angle))
    lines.append(pad_smd("4", -1.1, 0.85, 1.2, 1.0, nets[4], angle))
    lines.append("  )")
    return '\n'.join(lines)


def fp_tact_switch(ref, value, x, y, nets, angle=0):
    lines = [fp_header("Button_Switch_SMD:SW_SPST_TL3342", ref, value, x, y, angle)]
    lines.append(pad_smd("1", -3.1, 0, 1.8, 1.1, nets[1], angle))
    lines.append(pad_smd("2", 3.1, 0, 1.8, 1.1, nets[2], angle))
    lines.append("  )")
    return '\n'.join(lines)


def fp_qfn56(ref, value, x, y, pin_nets, angle=0):
    """
    RP2040 QFN-56 + exposed pad.
    pin_nets: dict {pin_number: net_number} for pins 1-57.
    """
    lines = [fp_header("Package_DFN_QFN:QFN-56-1EP_7x7mm_P0.4mm", ref, value, x, y, angle)]

    # Silkscreen outline + pin 1 marker
    lines.append(f'    (fp_line (start -3.5 -3.5) (end 3.5 -3.5) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "{uid()}"))')
    lines.append(f'    (fp_line (start -3.5 3.5) (end -3.5 -3.5) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "{uid()}"))')
    lines.append(f'    (fp_line (start 3.5 -3.5) (end 3.5 3.5) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "{uid()}"))')
    lines.append(f'    (fp_line (start 3.5 3.5) (end -3.5 3.5) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "{uid()}"))')
    # Pin 1 marker dot — fp_circle does not support (fill) in KiCad 9
    lines.append(f'    (fp_circle (center -3.1 3.9) (end -3.0 3.9) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "{uid()}"))')

    # Bottom side: pins 1-14 (left to right)
    for i in range(14):
        pnum = i + 1
        px = -2.6 + i * 0.4
        py = 3.375
        net = pin_nets.get(pnum, 0)
        lines.append(pad_smd(str(pnum), px, py, 0.2, 0.75, net, angle))

    # Right side: pins 15-28 (bottom to top)
    for i in range(14):
        pnum = i + 15
        px = 3.375
        py = 2.6 - i * 0.4
        net = pin_nets.get(pnum, 0)
        lines.append(pad_smd(str(pnum), px, py, 0.75, 0.2, net, angle))

    # Top side: pins 29-42 (right to left)
    for i in range(14):
        pnum = i + 29
        px = 2.6 - i * 0.4
        py = -3.375
        net = pin_nets.get(pnum, 0)
        lines.append(pad_smd(str(pnum), px, py, 0.2, 0.75, net, angle))

    # Left side: pins 43-56 (top to bottom)
    for i in range(14):
        pnum = i + 43
        px = -3.375
        py = -2.6 + i * 0.4
        net = pin_nets.get(pnum, 0)
        lines.append(pad_smd(str(pnum), px, py, 0.75, 0.2, net, angle))

    # Exposed pad (pin 57 = GND)
    net57 = pin_nets.get(57, 1)
    lines.append(pad_smd("57", 0, 0, 3.1, 3.1, net57, angle, shape="rect"))

    lines.append("  )")
    return '\n'.join(lines)


def fp_soic8(ref, value, x, y, pin_nets, angle=0):
    """SOIC-8 W25Q16 flash. Pins 1-4 on bottom, 5-8 on top."""
    lines = [fp_header("Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", ref, value, x, y, angle)]
    lines.append(f'    (fp_line (start -2 -2.5) (end 2 -2.5) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "{uid()}"))')
    lines.append(f'    (fp_line (start -2 2.5) (end -2 -2.5) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "{uid()}"))')
    lines.append(f'    (fp_line (start 2 -2.5) (end 2 2.5) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "{uid()}"))')
    lines.append(f'    (fp_line (start 2 2.5) (end -2 2.5) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "{uid()}"))')

    # Pins 1-4 on one side
    for i in range(4):
        pnum = i + 1
        px = -1.905 + i * 1.27
        net = pin_nets.get(pnum, 0)
        lines.append(pad_smd(str(pnum), px, 2.475, 0.6, 1.55, net, angle))
    # Pins 5-8 on other side (reversed order)
    for i in range(4):
        pnum = 8 - i
        px = -1.905 + i * 1.27
        net = pin_nets.get(pnum, 0)
        lines.append(pad_smd(str(pnum), px, -2.475, 0.6, 1.55, net, angle))

    lines.append("  )")
    return '\n'.join(lines)


def fp_tssop20(ref, value, x, y, pin_nets, angle=0):
    """TSSOP-20 74HCT245 (compact package). Pins 1-10 bottom, 11-20 top.
    Body: 6.5x4.4mm, pin pitch 0.65mm, pad-to-pad span ~6.4mm."""
    lines = [fp_header("Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm", ref, value, x, y, angle)]
    # Silkscreen outline
    lines.append(f'    (fp_line (start -3.4 -2.3) (end 3.4 -2.3) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "{uid()}"))')
    lines.append(f'    (fp_line (start -3.4 2.3) (end -3.4 -2.3) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "{uid()}"))')
    lines.append(f'    (fp_line (start 3.4 -2.3) (end 3.4 2.3) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "{uid()}"))')
    lines.append(f'    (fp_line (start 3.4 2.3) (end -3.4 2.3) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "{uid()}"))')

    # TSSOP-20: 20 pins, pitch 0.65mm, 10 per side
    # Pin 1 at x = -2.925mm, each subsequent pin +0.65mm
    # Pads at y = ±3.2mm (center of pad, pad height ~1.6mm)
    for i in range(10):
        pnum = i + 1
        px = -2.925 + i * 0.65
        net = pin_nets.get(pnum, 0)
        lines.append(pad_smd(str(pnum), px, 3.2, 0.4, 1.6, net, angle))
    # Pins 11-20 on other side (reversed)
    for i in range(10):
        pnum = 20 - i
        px = -2.925 + i * 0.65
        net = pin_nets.get(pnum, 0)
        lines.append(pad_smd(str(pnum), px, -3.2, 0.4, 1.6, net, angle))

    lines.append("  )")
    return '\n'.join(lines)


def fp_usb_a(ref, value, x, y, pin_nets, angle=0):
    """USB-A female TH connector. Pins: 1=VBUS, 2=D-, 3=D+, 4=GND, 5=Shield."""
    lines = [fp_header("Connector_USB:USB_A_Molex_67643_Horizontal", ref, value, x, y, angle, attr="through_hole")]
    lines.append(pad_th("1", 0, 3.5, 1.5, 0.9, pin_nets.get(1, 0), angle))
    lines.append(pad_th("2", 0, 1.0, 1.5, 0.9, pin_nets.get(2, 0), angle))
    lines.append(pad_th("3", 0, -1.0, 1.5, 0.9, pin_nets.get(3, 0), angle))
    lines.append(pad_th("4", 0, -3.5, 1.5, 0.9, pin_nets.get(4, 0), angle))
    # Shield / mounting tabs
    lines.append(pad_th("5", -4, -6, 2.5, 1.5, pin_nets.get(5, 0), angle, shape="oval", oval_w=2.5, oval_h=2.0))
    lines.append(pad_th("5", -4, 6, 2.5, 1.5, pin_nets.get(5, 0), angle, shape="oval", oval_w=2.5, oval_h=2.0))
    lines.append("  )")
    return '\n'.join(lines)


def fp_db9_male(ref, value, x, y, pin_nets, angle=0):
    """DB-9 male TH connector — signal pins only, no mounting holes.
    Mounting ears overhang the board edges; case provides mechanical retention."""
    lines = [fp_header("Connector_Dsub:DSUB-9_Male_Horizontal_P2.77x2.84mm_EdgePinOffset7.70mm",
                        ref, value, x, y, angle, attr="through_hole")]
    # Silkscreen outline for signal pin area only (no mounting ears)
    lines.append(f'    (fp_rect (start -7 -3.5) (end 7 3.5) (stroke (width 0.12) (type solid)) (layer "F.Fab") (uuid "{uid()}"))')

    # Row 1: pins 1-5 (front row, closer to connector face)
    for i in range(5):
        pnum = i + 1
        px = -5.54 + i * 2.77
        net = pin_nets.get(pnum, 0)
        lines.append(pad_th(str(pnum), px, -1.42, 1.6, 1.0, net, angle))
    # Row 2: pins 6-9 (back row)
    for i in range(4):
        pnum = i + 6
        px = -4.155 + i * 2.77
        net = pin_nets.get(pnum, 0)
        lines.append(pad_th(str(pnum), px, 1.42, 1.6, 1.0, net, angle))
    # No mounting holes — ears overhang the board edges

    lines.append("  )")
    return '\n'.join(lines)


def ground_zone():
    """Back copper ground pour."""
    return f'''  (zone
    (net 1)
    (net_name "GND")
    (layer "B.Cu")
    (uuid "{uid()}")
    (hatch edge 0.5)
    (connect_pads (clearance 0.3))
    (min_thickness 0.2)
    (filled_areas_thickness no)
    (fill yes (thermal_gap 0.5) (thermal_bridge_width 0.5))
    (polygon (pts
      (xy {OX - 0.5} {OY - 0.5})
      (xy {OX + BW + 0.5} {OY - 0.5})
      (xy {OX + BW + 0.5} {OY + BL + 0.5})
      (xy {OX - 0.5} {OY + BL + 0.5})
    ))
  )'''


def front_ground_zone():
    """Front copper ground pour (fills unused areas)."""
    return f'''  (zone
    (net 1)
    (net_name "GND")
    (layer "F.Cu")
    (uuid "{uid()}")
    (hatch edge 0.5)
    (priority 0)
    (connect_pads (clearance 0.3))
    (min_thickness 0.2)
    (filled_areas_thickness no)
    (fill yes (thermal_gap 0.5) (thermal_bridge_width 0.5))
    (polygon (pts
      (xy {OX - 0.5} {OY - 0.5})
      (xy {OX + BW + 0.5} {OY - 0.5})
      (xy {OX + BW + 0.5} {OY + BL + 0.5})
      (xy {OX - 0.5} {OY + BL + 0.5})
    ))
  )'''


def silkscreen_text(text, x, y, size=1.0, layer="F.SilkS"):
    return f'''  (gr_text "{text}" (at {x} {y}) (layer "{layer}") (uuid "{uid()}")
    (effects (font (size {size} {size}) (thickness {size * 0.15}))))'''


def generate_pcb():
    footprints = []

    # Board center references
    cx = OX + BW / 2      # Center X (width axis) = OX + 10
    cy = OY + BL / 2      # Center Y (length axis) = OY + 21

    # ─── DONGLE LAYOUT (top-to-bottom, Y increasing) ───────────────────────
    #
    # 20mm wide mouSTer-like dongle. DB9 mounting ears overhang the board.
    # DB9 connector face extends past top edge (mating axis = Y axis).
    # USB-A connector face extends past bottom edge (mating axis = Y axis).
    # Components stack vertically since board is narrow.
    #
    # Zone map (Y offsets from OY):
    #   0..5   DB9 signal pin zone (connector body overhangs Y < OY)
    #   5..15  74HCT245 + DB9-side passives
    #  15..17  cap row (above RP2040)
    #  17..25  RP2040 + crystal (right side)
    #  25..27  cap row (below RP2040)
    #  27..33  flash + switch + LDO
    #  33..36  USB passives
    #  36..42  USB-A pin zone (connector body overhangs Y > OY+BL)

    # ─── DB-9 Male (J2) — top edge, signal pins only ──────────────────────
    # Rotation 0°: connector face extends in -Y (past top edge).
    # Signal pins span ±5.54mm in X. Mounting ears at ±12.5mm overhang the board.
    # Center at Y=OY+3 → front pin pad edge at OY+0.78 (inside board).
    db9_x = cx
    db9_y = OY + 3
    db9_nets = {
        1: 29,   # Data 0
        2: 30,   # Data 1
        3: 31,   # Data 2
        4: 32,   # Data 3
        5: 35,   # +5V from MSX (before diode)
        6: 33,   # Left button
        7: 34,   # Right button
        8: 27,   # Strobe (5V, before divider)
        9: 1,    # GND
    }
    footprints.append(fp_db9_male("J2", "DB9_Male", db9_x, db9_y, db9_nets, 0))

    # ─── 74HCT245 (U3) — TSSOP-20, near DB9 (drives DB9 signals) ───────
    # Body 6.5x4.4mm, pads extend to ±4.0mm in Y from center.
    # Centered on board (20mm wide, body 4.4mm — fits easily).
    ls_x = cx
    ls_y = OY + 11
    ls_nets = {
        1: 1,    # DIR → GND (A→B)
        2: 6,    # A1 ← GPIO2
        3: 7,    # A2 ← GPIO3
        4: 8,    # A3 ← GPIO4
        5: 9,    # A4 ← GPIO5
        6: 10,   # A5 ← GPIO6
        7: 11,   # A6 ← GPIO7
        8: 1,    # A7 → GND (unused)
        9: 1,    # A8 → GND (unused)
        10: 1,   # GND
        11: 0,   # B8 — unused (no connect)
        12: 0,   # B7 — unused (no connect)
        13: 34,  # B6 → right btn
        14: 33,  # B5 → left btn
        15: 32,  # B4 → data 3
        16: 31,  # B3 → data 2
        17: 30,  # B2 → data 1
        18: 29,  # B1 → data 0
        19: 1,   # ~OE → GND (always enabled)
        20: 2,   # VCC → +5V
    }
    footprints.append(fp_tssop20("U3", "74HCT245", ls_x, ls_y, ls_nets, 0))

    # ─── DB9-side passives — beside U3 ─────────────────────────────────
    # R3: 2.2kΩ strobe divider top (STROBE_5V → STROBE_DIV)
    footprints.append(fp_0402("R3", "2.2k", cx - 5, OY + 8, {1: 27, 2: 12}))
    # R4: 3.3kΩ strobe divider bottom (STROBE_DIV → GND)
    footprints.append(fp_0402("R4", "3.3k", cx - 5, OY + 10, {1: 12, 2: 1}))
    # D1: Schottky diode (MSX power protection)
    footprints.append(fp_sod323("D1", "BAT54", cx + 5, OY + 8, {1: 2, 2: 35}))

    # ─── RP2040 (U1) — center of board ──────────────────────────────────
    # QFN-56 body 7x7mm, pads extend to ±3.75mm from center.
    # At Y=OY+21: top pads at OY+17.25, bottom pads at OY+24.75.
    # U3 bottom pads at OY+15. Gap = 17.25-15 = 2.25mm (roomy).
    rp_x = cx
    rp_y = OY + 21

    # RP2040 pin-to-net mapping (QFN-56 numbering)
    rp_nets = {
        # IOVDD pins → +3V3
        1: 3, 10: 3, 17: 3, 23: 3, 34: 3, 43: 3, 50: 3,
        # GPIO pins used
        2: 0, 3: 0,           # GPIO0, GPIO1 — unused
        4: 6,                  # GPIO2 → data 0
        5: 7,                  # GPIO3 → data 1
        6: 8,                  # GPIO4 → data 2
        7: 9,                  # GPIO5 → data 3
        8: 10,                 # GPIO6 → left btn
        9: 11,                 # GPIO7 → right btn
        11: 12,                # GPIO8 → strobe input (via divider)
        # Unused GPIOs
        12: 0, 13: 0, 14: 0, 15: 0, 16: 0,  # GPIO9-13
        18: 0, 19: 0,         # GPIO14-15
        28: 0, 29: 0, 30: 0, 31: 0, 32: 0, 33: 0,  # GPIO16-21
        35: 0, 36: 0, 37: 0,  # GPIO22-24
        38: 13,                # GPIO25 → LED
        39: 0, 40: 0, 41: 0, 42: 0,  # GPIO26-29
        # Special pins
        20: 1,                 # TESTEN → GND
        21: 20,                # XIN → crystal
        22: 21,                # XOUT → crystal
        24: 22,                # DVDD → core voltage
        25: 0, 26: 0,         # SWCLK, SWD — unused
        27: 23,                # RUN → pull-up
        44: 3,                 # ADC_AVDD → +3V3
        45: 3,                 # VREG_VIN → +3V3
        46: 22,                # VREG_VOUT → DVDD
        47: 5,                 # USB_DM
        48: 4,                 # USB_DP
        49: 3,                 # USB_VDD → +3V3
        # QSPI flash interface
        51: 18,                # QSPI_SD3
        52: 14,                # QSPI_SCLK
        53: 15,                # QSPI_SD0
        54: 17,                # QSPI_SD2
        55: 16,                # QSPI_SD1
        56: 19,                # QSPI_SS (also BOOTSEL)
        # Exposed pad
        57: 1,                 # GND
    }
    footprints.append(fp_qfn56("U1", "RP2040", rp_x, rp_y, rp_nets))

    # ─── 12MHz Crystal (Y1) — right of RP2040, near XIN/XOUT ────────────
    # XIN = pin 21 at (rp_x+3.375, rp_y+0.2), XOUT = pin 22 at (rp_x+3.375, rp_y-0.2).
    # Crystal 3225: pads span ±1.7mm in X, ±1.35mm in Y from center.
    # At (cx+7, rp_y): inner pads at cx+5.3, RP2040 right pads at cx+3.75. Gap=1.55mm ✓
    # Outer pads at cx+8.7, board right edge cx+10. Margin=1.3mm ✓
    cr_nets = {1: 20, 2: 1, 3: 21, 4: 1}
    footprints.append(fp_crystal_3225("Y1", "12MHz", cx + 7, rp_y, cr_nets))

    # ─── W25Q16 Flash (U2) — below RP2040, slightly right ───────────────
    # SOIC-8 at 0° (unrotated). Body 3.9x4.9mm, pads at ±2.475mm in Y.
    # Can't fit beside RP2040 on 20mm board — goes below cap row instead.
    # At (cx+3, OY+30): pads Y=27.525 to 32.475. Bottom cap row at OY+26. Gap ~1.5mm ✓
    fl_nets = {
        1: 19,  # ~CS → QSPI_SS
        2: 16,  # DO/IO1 → QSPI_SD1
        3: 17,  # ~WP/IO2 → QSPI_SD2
        4: 1,   # GND
        5: 15,  # DI/IO0 → QSPI_SD0
        6: 14,  # CLK → QSPI_SCLK
        7: 18,  # ~HOLD/IO3 → QSPI_SD3
        8: 3,   # VCC → +3V3
    }
    footprints.append(fp_soic8("U2", "W25Q16", cx + 3, OY + 30, fl_nets, 0))

    # ─── BOOTSEL Switch (SW1) — left side, same Y level as flash ────────
    # TL3342 pads at ±3.1mm in X. At cx-5, pads from cx-8.1 to cx-1.9.
    # Board left edge at cx-10. Margin=1.9mm. Flash inner pad at cx+0.8. Gap ≥2.7mm ✓
    footprints.append(fp_tact_switch("SW1", "BOOTSEL", cx - 5, OY + 30, {1: 19, 2: 1}, 0))

    # ─── XC6206 LDO (U4) — left side, below switch ─────────────────────
    # SOT-23: pin 1(GND) at (-0.95,+1.1), pin 2(VOUT) at (+0.95,+1.1), pin 3(VIN) at (0,-1.1).
    # At (cx-6, OY+33): all pads well within board. Left edge at cx-6.95-0.4=cx-7.35, margin 2.65mm.
    ldo_nets = {1: 1, 2: 3, 3: 2}
    footprints.append(fp_sot23_ldo("U4", "XC6206", cx - 6, OY + 33, ldo_nets))

    # ─── USB-A Female (J1) — bottom edge ─────────────────────────────────
    # Rotation 270° (CW): mating face extends past bottom edge.
    # Data pins at (cx±3.5, usb_y). Shield tabs at (cx±6, usb_y-4).
    # At usb_y=OY+40: shield tabs at OY+36. USB passives at OY+34.
    usb_x = cx
    usb_y = OY + BL - 2      # = OY + 40
    usb_nets = {1: 26, 2: 24, 3: 25, 4: 1, 5: 1}
    footprints.append(fp_usb_a("J1", "USB_A", usb_x, usb_y, usb_nets, 270))

    # ─── Status LED (D2) + resistor — left side, between cap row and flash ─
    # D2 at cx-8 (left pad at cx-9.15, board edge cx-10, margin 0.85mm).
    # R5 at cx-5 (left pad at cx-5.76). Gap to D2 right pad (cx-6.85) = 1.09mm ✓
    footprints.append(fp_0603_led("D2", "Green", cx - 8, OY + 27, {1: 36, 2: 1}))
    footprints.append(fp_0402("R5", "1k", cx - 5, OY + 27, {1: 13, 2: 36}))

    # ─── Polyfuse F1 (USB VBUS protection) ───────────────────────────────
    # Place in gap between flash/LDO zone and USB shield tabs.
    usb_zone_y = OY + 34
    # F1 at cx-3: pad 1 at cx-3.95. LDO pin 2 at cx-5.05, right edge cx-4.65. Gap=0.7mm ✓
    footprints.append(fp_0805_fuse("F1", "500mA", cx - 3, usb_zone_y, {1: 2, 2: 26}))

    # ─── Resistors ───────────────────────────────────────────────────────
    # R1, R2: USB series resistors — in gap between flash zone and USB
    # R1 at cx+1: left pad at cx+0.24. F1 pad 2 right at cx-1.55. Gap=1.79mm ✓
    footprints.append(fp_0402("R1", "27R", cx + 1, usb_zone_y, {1: 24, 2: 5}))
    footprints.append(fp_0402("R2", "27R", cx + 4, usb_zone_y, {1: 25, 2: 4}))
    # R6: flash CS pull-up — right of flash, above
    # Flash top pads end at cx+5.2. R6 at cx+7: left pad at cx+6.24. Gap=1.04mm ✓
    footprints.append(fp_0402("R6", "10k", cx + 7, OY + 27, {1: 19, 2: 3}))
    # R7: RUN pull-up — left side, above RP2040 cap row
    footprints.append(fp_0402("R7", "10k", cx - 7, OY + 16, {1: 23, 2: 3}))

    # ─── Decoupling Capacitors ───────────────────────────────────────────
    # RP2040 pads extend to ±3.75mm from center (3.375 + 0.375 half-pad).
    # 20mm board: use rows above and below RP2040.
    #
    # Top row at rp_y-5 (=OY+16): RP2040 top pad edge at OY+17.25.
    #   Cap top edge at OY+16+0.25=OY+16.25. Gap to RP2040=1.0mm ✓
    #   U3 bottom pads at OY+15. Cap bottom edge at OY+16-0.25=OY+15.75. Gap=0.75mm ✓
    # Bottom row at rp_y+5 (=OY+26): RP2040 bottom pad edge at OY+24.75.
    #   Cap top edge at OY+26-0.25=OY+25.75. Gap=1.0mm ✓
    cap_top_y = rp_y - 5     # OY + 16
    cap_bot_y = rp_y + 5     # OY + 26

    # 5 caps per row, 2mm spacing, centered on RP2040.
    # X range: cx-4 to cx+4 = 6mm to 14mm from OX left. Board margins ≥6mm. ✓
    cap_positions = [
        # Top row: 5 caps (C1-C5)
        (cx - 4, cap_top_y),
        (cx - 2, cap_top_y),
        (cx,     cap_top_y),
        (cx + 2, cap_top_y),
        (cx + 4, cap_top_y),
        # Bottom row: 5 caps (C6-C10)
        (cx - 4, cap_bot_y),
        (cx - 2, cap_bot_y),
        (cx,     cap_bot_y),
        (cx + 2, cap_bot_y),
        (cx + 4, cap_bot_y),
    ]
    for i, (cx_pos, cy_pos) in enumerate(cap_positions):
        footprints.append(fp_0402(f"C{i+1}", "100nF", cx_pos, cy_pos, {1: 3, 2: 1}))

    # C11: 27pF crystal load cap XIN — near crystal (above)
    footprints.append(fp_0402("C11", "27pF", cx + 7, rp_y - 2.5, {1: 20, 2: 1}))
    # C12: 27pF crystal load cap XOUT — near crystal (below)
    footprints.append(fp_0402("C12", "27pF", cx + 7, rp_y + 2.5, {1: 21, 2: 1}))
    # C13: 1µF DVDD decoupling — bottom cap row, left extension
    footprints.append(fp_0402("C13", "1uF", cx - 6, cap_bot_y, {1: 22, 2: 1}))
    # C14: 1µF USB_VDD decoupling — bottom cap row, right extension
    footprints.append(fp_0402("C14", "1uF", cx + 6, cap_bot_y, {1: 3, 2: 1}))
    # C15: 1µF LDO input (+5V → GND) — near LDO VIN (left side)
    footprints.append(fp_0402("C15", "1uF", cx - 8, OY + 32, {1: 2, 2: 1}))
    # C16: 1µF LDO output (+3V3 → GND) — below LDO (clear of USB shield tabs)
    footprints.append(fp_0402("C16", "1uF", cx - 8.5, OY + 35, {1: 3, 2: 1}))

    # ─── Silkscreen text ─────────────────────────────────────────────────
    texts = []
    texts.append(silkscreen_text("USB-MSX", cx, OY + 28, 0.8))
    texts.append(silkscreen_text("SR", cx - 7, OY + 28, 0.6))

    # ─── Net declarations ────────────────────────────────────────────────
    net_decls = []
    for num, name in sorted(NETS.items()):
        if num == 0:
            net_decls.append('  (net 0 "")')
        else:
            net_decls.append(f'  (net {num} "{name}")')

    # ─── Assemble PCB ────────────────────────────────────────────────────
    output = f'''(kicad_pcb
  (version 20231014)
  (generator "usb_msx_pcb_gen")
  (generator_version "3.0")
  (general
    (thickness 1.6)
    (legacy_teardrops no)
  )
  (paper "A4")
  (layers
    (0 "F.Cu" signal)
    (31 "B.Cu" signal)
    (32 "B.Adhes" user "B.Adhesive")
    (33 "F.Adhes" user "F.Adhesive")
    (34 "B.Paste" user)
    (35 "F.Paste" user)
    (36 "B.SilkS" user "B.Silkscreen")
    (37 "F.SilkS" user "F.Silkscreen")
    (38 "B.Mask" user "B.Mask")
    (39 "F.Mask" user "F.Mask")
    (40 "Dwgs.User" user "User.Drawings")
    (41 "Cmts.User" user "User.Comments")
    (42 "Eco1.User" user "User.Eco1")
    (43 "Eco2.User" user "User.Eco2")
    (44 "Edge.Cuts" user)
    (45 "Margin" user)
    (46 "B.CrtYd" user "B.Courtyard")
    (47 "F.CrtYd" user "F.Courtyard")
    (48 "B.Fab" user "B.Fabrication")
    (49 "F.Fab" user "F.Fabrication")
  )
  (setup
    (pad_to_mask_clearance 0)
    (allow_soldermask_bridges_in_footprints no)
    (pcbplotparams
      (layerselection 0x00010fc_ffffffff)
      (plot_on_all_layers_selection 0x0000000_00000000)
      (disableapertmacros no)
      (usegerberextensions yes)
      (usegerberattributes yes)
      (usegerberadvancedattributes yes)
      (creategerberjobfile yes)
      (dashed_line_dash_ratio 12.000000)
      (dashed_line_gap_ratio 3.000000)
      (svgprecision 4)
      (plotframeref no)
      (viasonmask no)
      (mode 1)
      (useauxorigin no)
      (hpglpennumber 1)
      (hpglpenspeed 20)
      (hpglpendiameter 15.000000)
      (pdf_front_fp_property_popups yes)
      (pdf_back_fp_property_popups yes)
      (dxf_units mm)
      (dxf_use_pcbnew_font yes)
      (psnegative no)
      (psa4output no)
      (plotreference yes)
      (plotvalue no)
      (plotfptext no)
      (plotinvisibletext no)
      (sketchpadsonfab no)
      (subtractmaskfromsilk yes)
      (outputformat 1)
      (mirror no)
      (drillshape 1)
      (scaleselection 1)
      (outputdirectory "../../gerbers/")
    )
  )

{chr(10).join(net_decls)}

{board_outline()}

{chr(10).join(footprints)}

{chr(10).join(texts)}

{ground_zone()}

{front_ground_zone()}

)
'''
    return output


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "usb-to-msx-mouse.kicad_pcb")

    pcb = generate_pcb()
    with open(output_path, 'w') as f:
        f.write(pcb)

    print(f"Generated: {output_path}")
    print(f"Board size: {BW} x {BL} mm ({BW * BL} mm²)")
    print(f"File size: {len(pcb)} bytes")
    print(f"Nets defined: {len(NETS)}")
    print()
    print("All pads have net assignments. Ready for routing.")
