#!/usr/bin/env python3
"""
generate_pcb.py — Generate KiCad 8 PCB layout for USB-to-MSX mouse adapter.

Creates usb-to-msx-mouse.kicad_pcb with:
    - Board outline: ~22 x 52mm (2-layer, 1.6mm thick)
    - All footprints placed with correct net assignments
    - Ground zone on back copper
    - Net definitions for all signals

Usage:
    python3 generate_pcb.py

After generation, open in KiCad 8 to:
    1. Fill zones (Edit → Fill All Zones or 'B')
    2. Route traces (interactive router or export DSN for freerouting)
    3. Run DRC
    4. Generate Gerbers
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
OX, OY = 100, 100  # Board origin
BW, BH = 22, 52    # Width (Y), Length (X)


def board_outline():
    x1, y1 = OX, OY
    x2, y2 = OX + BH, OY + BW
    return f'''  (gr_rect (start {x1} {y1}) (end {x2} {y2})
    (stroke (width 0.05) (type default))
    (fill (type none))
    (layer "Edge.Cuts")
    (uuid "{uid()}")
  )'''


# ─── Footprint generators with net assignments ─────────────────────────────

def pad_smd(num, x, y, w, h, net, angle=0, shape="roundrect", layer="F.Cu"):
    """Generate a single SMD pad with net assignment."""
    layers = f'"{layer}" "{layer[0]}.Paste" "{layer[0]}.Mask"'
    rr = ' (roundrect_rratio 0.25)' if shape == "roundrect" else ""
    return f'    (pad "{num}" smd {shape} (at {x} {y} {angle}) (size {w} {h}) (layers {layers}){rr} {net_str(net)} (uuid "{uid()}"))'


def pad_th(num, x, y, pad_d, drill_d, net, angle=0, shape="circle", oval_w=None, oval_h=None):
    """Generate a single through-hole pad with net assignment."""
    if shape == "oval" and oval_w and oval_h:
        size = f"{oval_w} {oval_h}"
    else:
        size = f"{pad_d} {pad_d}"
    return f'    (pad "{num}" thru_hole {shape} (at {x} {y} {angle}) (size {size}) (drill {drill_d}) (layers "*.Cu" "*.Mask") {net_str(net)} (uuid "{uid()}"))'


def fp_header(fp_lib, ref, value, x, y, angle=0):
    """Footprint header boilerplate."""
    return f'''  (footprint "{fp_lib}"
    (layer "F.Cu")
    (uuid "{uid()}")
    (at {x} {y} {angle})
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
    lines.append(f'    (fp_circle (center -3.1 3.9) (end -3.0 3.9) (stroke (width 0.12) (type solid)) (fill (type solid)) (layer "F.SilkS") (uuid "{uid()}"))')

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


def fp_soic20w(ref, value, x, y, pin_nets, angle=0):
    """SOIC-20W 74HCT245. Pins 1-10 bottom, 11-20 top."""
    lines = [fp_header("Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm", ref, value, x, y, angle)]
    lines.append(f'    (fp_line (start -6.5 -4.5) (end 6.5 -4.5) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "{uid()}"))')
    lines.append(f'    (fp_line (start -6.5 4.5) (end -6.5 -4.5) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "{uid()}"))')
    lines.append(f'    (fp_line (start 6.5 -4.5) (end 6.5 4.5) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "{uid()}"))')
    lines.append(f'    (fp_line (start 6.5 4.5) (end -6.5 4.5) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "{uid()}"))')

    # Pins 1-10 on one side
    for i in range(10):
        pnum = i + 1
        px = -5.715 + i * 1.27
        net = pin_nets.get(pnum, 0)
        lines.append(pad_smd(str(pnum), px, 3.75, 0.6, 1.78, net, angle))
    # Pins 11-20 on other side (reversed)
    for i in range(10):
        pnum = 20 - i
        px = -5.715 + i * 1.27
        net = pin_nets.get(pnum, 0)
        lines.append(pad_smd(str(pnum), px, -3.75, 0.6, 1.78, net, angle))

    lines.append("  )")
    return '\n'.join(lines)


def fp_usb_a(ref, value, x, y, pin_nets, angle=0):
    """USB-A female TH connector. Pins: 1=VBUS, 2=D-, 3=D+, 4=GND, 5=Shield."""
    lines = [fp_header("Connector_USB:USB_A_Molex_67643_Horizontal", ref, value, x, y, angle)]
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
    """DB-9 male TH connector. Pins 1-9 + pin 10 for mounting holes."""
    lines = [fp_header("Connector_Dsub:DSUB-9_Male_Horizontal_P2.77x2.84mm_EdgePinOffset7.70mm_Housed_MountingHolesOffset9.12mm",
                        ref, value, x, y, angle)]
    lines.append(f'    (fp_rect (start -14 -3.5) (end 14 3.5) (stroke (width 0.12) (type solid)) (fill (type none)) (layer "F.Fab") (uuid "{uid()}"))')

    # Row 1: pins 1-5
    for i in range(5):
        pnum = i + 1
        px = -5.54 + i * 2.77
        net = pin_nets.get(pnum, 0)
        lines.append(pad_th(str(pnum), px, -1.42, 1.6, 1.0, net, angle))
    # Row 2: pins 6-9
    for i in range(4):
        pnum = i + 6
        px = -4.155 + i * 2.77
        net = pin_nets.get(pnum, 0)
        lines.append(pad_th(str(pnum), px, 1.42, 1.6, 1.0, net, angle))
    # Mounting holes (connected to GND)
    mnt_net = pin_nets.get(10, 1)
    lines.append(pad_th("10", -12.5, 0, 3.2, 2.8, mnt_net, angle))
    lines.append(pad_th("10", 12.5, 0, 3.2, 2.8, mnt_net, angle))

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
      (xy {OX + BH + 0.5} {OY - 0.5})
      (xy {OX + BH + 0.5} {OY + BW + 0.5})
      (xy {OX - 0.5} {OY + BW + 0.5})
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
      (xy {OX + BH + 0.5} {OY - 0.5})
      (xy {OX + BH + 0.5} {OY + BW + 0.5})
      (xy {OX - 0.5} {OY + BW + 0.5})
    ))
  )'''


def silkscreen_text(text, x, y, size=1.0, layer="F.SilkS"):
    return f'''  (gr_text "{text}" (at {x} {y}) (layer "{layer}") (uuid "{uid()}")
    (effects (font (size {size} {size}) (thickness {size * 0.15}))))'''


def generate_pcb():
    footprints = []

    # Board center references
    cx = OX + BH / 2
    cy = OY + BW / 2

    # ─── RP2040 (U1) — center-left of board ────────────────────────────
    rp_x = OX + 18
    rp_y = cy

    # RP2040 pin-to-net mapping (QFN-56 numbering)
    rp_nets = {
        # IOVDD pins → +3V3
        1: 3, 10: 3, 17: 3, 23: 3, 34: 3, 43: 3, 50: 3,
        # GPIO pins used by our design
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

    # ─── W25Q16 Flash (U2) — below RP2040 ──────────────────────────────
    # SOIC-8 pinout: 1=~CS, 2=DO/IO1, 3=~WP/IO2, 4=GND, 5=DI/IO0, 6=CLK, 7=~HOLD/IO3, 8=VCC
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
    footprints.append(fp_soic8("U2", "W25Q16", rp_x, rp_y + 8, fl_nets, 90))

    # ─── 74HCT245 (U3) — between RP2040 and DB-9 ──────────────────────
    ls_x = OX + 35
    # SOIC-20 pinout: 1=DIR, 2=A1..9=A8, 10=GND, 11=B8..18=B1, 19=~OE, 20=VCC
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
        13: 34,  # B6 → DB-9 pin 7 (right btn)
        14: 33,  # B5 → DB-9 pin 6 (left btn)
        15: 32,  # B4 → DB-9 pin 4 (data 3)
        16: 31,  # B3 → DB-9 pin 3 (data 2)
        17: 30,  # B2 → DB-9 pin 2 (data 1)
        18: 29,  # B1 → DB-9 pin 1 (data 0)
        19: 1,   # ~OE → GND (always enabled)
        20: 2,   # VCC → +5V
    }
    footprints.append(fp_soic20w("U3", "74HCT245", ls_x, cy, ls_nets, 90))

    # ─── XC6206 LDO (U4) — near top, power section ─────────────────────
    # SOT-23: pin 1=GND, pin 2=VOUT, pin 3=VIN
    ldo_nets = {1: 1, 2: 3, 3: 2}  # GND, +3V3, +5V
    footprints.append(fp_sot23_ldo("U4", "XC6206", rp_x - 5, rp_y - 8, ldo_nets))

    # ─── 12MHz Crystal (Y1) ────────────────────────────────────────────
    # 3225: pin 1=XIN, pin 2=GND, pin 3=XOUT, pin 4=GND
    cr_nets = {1: 20, 2: 1, 3: 21, 4: 1}
    footprints.append(fp_crystal_3225("Y1", "12MHz", rp_x + 6, rp_y - 6, cr_nets))

    # ─── BOOTSEL Switch (SW1) ──────────────────────────────────────────
    # Pin 1 → QSPI_SS, Pin 2 → GND
    footprints.append(fp_tact_switch("SW1", "BOOTSEL", rp_x - 6, rp_y + 8, {1: 19, 2: 1}, 90))

    # ─── USB-A Female (J1) — left edge ─────────────────────────────────
    # Pin 1=VBUS, 2=D-, 3=D+, 4=GND, 5=Shield
    usb_nets = {1: 26, 2: 24, 3: 25, 4: 1, 5: 1}
    footprints.append(fp_usb_a("J1", "USB_A", OX + 2, cy, usb_nets, 90))

    # ─── DB-9 Male (J2) — right edge ──────────────────────────────────
    # MSX pinout: 1=D0, 2=D1, 3=D2, 4=D3, 5=+5V, 6=LBtn, 7=RBtn, 8=Strobe, 9=GND
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
        10: 1,   # Mounting → GND
    }
    footprints.append(fp_db9_male("J2", "DB9_Male", OX + BH - 2, cy, db9_nets, 90))

    # ─── Status LED (D2) ───────────────────────────────────────────────
    # Pin 1=anode, 2=cathode(GND)
    footprints.append(fp_0603_led("D2", "Green", rp_x + 6, rp_y - 9, {1: 36, 2: 1}))

    # ─── Schottky Diode D1 (MSX power protection) ─────────────────────
    # Cathode (pin 1) → +5V rail, Anode (pin 2) → 5V_MSX
    footprints.append(fp_sod323("D1", "BAT54", OX + BH - 10, rp_y - 8, {1: 2, 2: 35}))

    # ─── Polyfuse F1 (USB VBUS protection) ─────────────────────────────
    # Pin 1 → +5V rail, Pin 2 → VBUS_FUSED (to USB-A VBUS)
    footprints.append(fp_0805_fuse("F1", "500mA", OX + 8, rp_y - 6, {1: 2, 2: 26}))

    # ─── Resistors ─────────────────────────────────────────────────────
    # R1: 27Ω USB D- series (USB_DM_R → USB_DM)
    footprints.append(fp_0402("R1", "27R", OX + 10, rp_y - 2, {1: 24, 2: 5}))
    # R2: 27Ω USB D+ series (USB_DP_R → USB_DP)
    footprints.append(fp_0402("R2", "27R", OX + 10, rp_y + 2, {1: 25, 2: 4}))
    # R3: 2.2kΩ strobe divider top (STROBE_5V → STROBE_DIV midpoint)
    footprints.append(fp_0402("R3", "2.2k", OX + BH - 8, rp_y + 4, {1: 27, 2: 12}))
    # R4: 3.3kΩ strobe divider bottom (STROBE_DIV → GND)
    footprints.append(fp_0402("R4", "3.3k", OX + BH - 8, rp_y + 7, {1: 12, 2: 1}))
    # R5: 1kΩ LED resistor (GPIO25 → LED_A)
    footprints.append(fp_0402("R5", "1k", rp_x + 6, rp_y - 7.5, {1: 13, 2: 36}))
    # R6: 10kΩ flash CS pull-up (QSPI_SS → +3V3)
    footprints.append(fp_0402("R6", "10k", rp_x - 4, rp_y + 6, {1: 19, 2: 3}))
    # R7: 10kΩ RUN pull-up (RUN → +3V3)
    footprints.append(fp_0402("R7", "10k", rp_x + 4, rp_y - 4, {1: 23, 2: 3}))

    # ─── Decoupling Capacitors ─────────────────────────────────────────
    # C1-C10: 100nF for RP2040 IOVDD/power pins (+3V3 → GND)
    cap_positions = [
        (rp_x - 5, rp_y - 5),
        (rp_x - 3, rp_y - 5),
        (rp_x - 1, rp_y - 5),
        (rp_x + 1, rp_y - 5),
        (rp_x + 3, rp_y - 5),
        (rp_x - 5, rp_y + 5),
        (rp_x - 3, rp_y + 5),
        (rp_x - 1, rp_y + 5),
        (rp_x + 1, rp_y + 5),
        (rp_x + 3, rp_y + 5),
    ]
    for i, (cx_pos, cy_pos) in enumerate(cap_positions):
        footprints.append(fp_0402(f"C{i+1}", "100nF", cx_pos, cy_pos, {1: 3, 2: 1}))

    # C11: 27pF crystal load cap XIN (XIN → GND)
    footprints.append(fp_0402("C11", "27pF", rp_x + 4, rp_y - 6, {1: 20, 2: 1}))
    # C12: 27pF crystal load cap XOUT (XOUT → GND)
    footprints.append(fp_0402("C12", "27pF", rp_x + 8, rp_y - 6, {1: 21, 2: 1}))
    # C13: 1µF DVDD decoupling (DVDD → GND)
    footprints.append(fp_0402("C13", "1uF", rp_x - 6, rp_y - 2, {1: 22, 2: 1}))
    # C14: 1µF USB_VDD decoupling (+3V3 → GND)
    footprints.append(fp_0402("C14", "1uF", rp_x + 5, rp_y + 5, {1: 3, 2: 1}))
    # C15: 1µF LDO input (+5V → GND)
    footprints.append(fp_0402("C15", "1uF", rp_x - 7, rp_y - 8, {1: 2, 2: 1}))
    # C16: 1µF LDO output (+3V3 → GND)
    footprints.append(fp_0402("C16", "1uF", rp_x - 3, rp_y - 8, {1: 3, 2: 1}))

    # ─── Silkscreen text ───────────────────────────────────────────────
    texts = []
    texts.append(silkscreen_text("USB-MSX Mouse", cx, OY + 2, 1.0))
    texts.append(silkscreen_text("SoundResearch", cx, OY + BW - 1.5, 0.8))

    # ─── Net declarations ──────────────────────────────────────────────
    net_decls = []
    for num, name in sorted(NETS.items()):
        if num == 0:
            net_decls.append('  (net 0 "")')
        else:
            net_decls.append(f'  (net {num} "{name}")')

    # ─── Assemble PCB ──────────────────────────────────────────────────
    output = f'''(kicad_pcb
  (version 20231014)
  (generator "usb_msx_pcb_gen")
  (generator_version "2.0")
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
    print(f"File size: {len(pcb)} bytes")
    print(f"Nets defined: {len(NETS)}")
    print()
    print("All pads have net assignments. Ready for routing.")
