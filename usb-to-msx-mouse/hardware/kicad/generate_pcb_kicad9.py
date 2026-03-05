#!/usr/bin/env python3
"""
generate_pcb_kicad9.py — Generate PCB using KiCad 9 Python API (pcbnew).

This script uses KiCad's native Python bindings to create the PCB,
ensuring full compatibility with KiCad 9's file format.

Usage (requires KiCad 9 installed):
    KICAD_PYTHON="/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3"
    DYLD_FRAMEWORK_PATH="/Applications/KiCad.app/Contents/Frameworks" $KICAD_PYTHON generate_pcb_kicad9.py
"""

import sys
import os

# Add KiCad Python packages to path
sys.path.insert(0, '/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages')
import pcbnew

# ─── Helper to convert mm to KiCad internal units ──────────────────────────
def mm(val):
    """Convert mm to KiCad internal units (nanometers in KiCad 9)."""
    return pcbnew.FromMM(val)

def pt(x, y):
    """Create a KiCad point from mm coordinates."""
    return pcbnew.VECTOR2I(mm(x), mm(y))

# ─── Net definitions ───────────────────────────────────────────────────────
NET_NAMES = [
    "",            # 0 - unconnected
    "GND",         # 1
    "+5V",         # 2
    "+3V3",        # 3
    "USB_DP",      # 4
    "USB_DM",      # 5
    "GPIO2",       # 6
    "GPIO3",       # 7
    "GPIO4",       # 8
    "GPIO5",       # 9
    "GPIO6",       # 10
    "GPIO7",       # 11
    "GPIO8",       # 12
    "GPIO25",      # 13
    "QSPI_SCLK",   # 14
    "QSPI_SD0",    # 15
    "QSPI_SD1",    # 16
    "QSPI_SD2",    # 17
    "QSPI_SD3",    # 18
    "QSPI_SS",     # 19
    "XIN",         # 20
    "XOUT",        # 21
    "DVDD",        # 22
    "RUN",         # 23
    "USB_DM_R",    # 24
    "USB_DP_R",    # 25
    "VBUS_FUSED",  # 26
    "STROBE_5V",   # 27
    "GPIO8_DIV",   # 28 (= GPIO8, strobe divider midpoint)
    "DB9_D0",      # 29
    "DB9_D1",      # 30
    "DB9_D2",      # 31
    "DB9_D3",      # 32
    "DB9_LBTN",    # 33
    "DB9_RBTN",    # 34
    "5V_MSX",      # 35
    "LED_A",       # 36
]

# ─── Board parameters ─────────────────────────────────────────────────────
OX, OY = 100, 100  # Origin in mm
BW, BH = 22, 52    # Board width (Y), length (X)

def add_smd_pad(fp, num, x, y, w, h, net_code, shape=pcbnew.PAD_SHAPE_ROUNDRECT):
    """Add an SMD pad to a footprint."""
    pad = pcbnew.PAD(fp)
    pad.SetNumber(str(num))
    pad.SetShape(shape)
    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    pad.SetLayerSet(pcbnew.PAD.SMDMask())
    pad.SetPosition(pt(x, y))
    pad.SetSize(pcbnew.VECTOR2I(mm(w), mm(h)))
    if shape == pcbnew.PAD_SHAPE_ROUNDRECT:
        pad.SetRoundRectCornerRadius(mm(min(w, h) * 0.25))
    pad.SetNet(net_code)
    fp.Add(pad)
    return pad

def add_th_pad(fp, num, x, y, pad_d, drill_d, net_code, shape=pcbnew.PAD_SHAPE_CIRCLE):
    """Add a through-hole pad to a footprint."""
    pad = pcbnew.PAD(fp)
    pad.SetNumber(str(num))
    pad.SetShape(shape)
    pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
    pad.SetLayerSet(pcbnew.PAD.PTHMask())
    pad.SetPosition(pt(x, y))
    pad.SetSize(pcbnew.VECTOR2I(mm(pad_d), mm(pad_d)))
    pad.SetDrillSize(pcbnew.VECTOR2I(mm(drill_d), mm(drill_d)))
    pad.SetNet(net_code)
    fp.Add(pad)
    return pad

def create_footprint(board, ref, value, x, y, angle=0):
    """Create and add a footprint to the board."""
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(pt(x, y))
    if angle:
        fp.SetOrientationDegrees(angle)
    board.Add(fp)
    return fp

def get_net(board, net_idx):
    """Get a net info object by index."""
    return board.FindNet(NET_NAMES[net_idx]) if net_idx > 0 else board.FindNet("")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "usb-to-msx-mouse.kicad_pcb")

    # Create board
    board = pcbnew.CreateEmptyBoard()

    # ─── Add nets ──────────────────────────────────────────────────────
    netinfo = board.GetNetInfo()
    for i, name in enumerate(NET_NAMES):
        if i == 0:
            continue  # Net 0 (unconnected) already exists
        net = pcbnew.NETINFO_ITEM(board, name)
        board.Add(net)

    # ─── Board outline ─────────────────────────────────────────────────
    edge = pcbnew.PCB_SHAPE(board)
    edge.SetShape(pcbnew.SHAPE_T_RECT)
    edge.SetStart(pt(OX, OY))
    edge.SetEnd(pt(OX + BH, OY + BW))
    edge.SetLayer(pcbnew.Edge_Cuts)
    edge.SetWidth(mm(0.05))
    board.Add(edge)

    # ─── RP2040 (U1) ──────────────────────────────────────────────────
    rp_x, rp_y = OX + 18, OY + BW / 2
    u1 = create_footprint(board, "U1", "RP2040", rp_x, rp_y)

    # RP2040 pin-to-net mapping
    rp_nets = {
        1: 3, 10: 3, 17: 3, 23: 3, 34: 3, 43: 3, 50: 3,  # IOVDD → +3V3
        4: 6, 5: 7, 6: 8, 7: 9, 8: 10, 9: 11,  # GPIO2-7
        11: 12,  # GPIO8
        38: 13,  # GPIO25
        20: 1,   # TESTEN → GND
        21: 20, 22: 21,  # XIN, XOUT
        24: 22, 46: 22,  # DVDD, VREG_VOUT
        27: 23,  # RUN
        44: 3, 45: 3, 49: 3,  # ADC_AVDD, VREG_VIN, USB_VDD → +3V3
        47: 5, 48: 4,  # USB_DM, USB_DP
        51: 18, 52: 14, 53: 15, 54: 17, 55: 16, 56: 19,  # QSPI
        57: 1,  # GND pad
    }

    # QFN-56 pads: bottom(1-14), right(15-28), top(29-42), left(43-56), center(57)
    for i in range(14):  # Bottom: pins 1-14
        pnum = i + 1
        px = rp_x + (-2.6 + i * 0.4)
        py = rp_y + 3.375
        net = get_net(board, rp_nets.get(pnum, 0))
        add_smd_pad(u1, pnum, px, py, 0.2, 0.75, net)

    for i in range(14):  # Right: pins 15-28
        pnum = i + 15
        px = rp_x + 3.375
        py = rp_y + (2.6 - i * 0.4)
        net = get_net(board, rp_nets.get(pnum, 0))
        add_smd_pad(u1, pnum, px, py, 0.75, 0.2, net)

    for i in range(14):  # Top: pins 29-42
        pnum = i + 29
        px = rp_x + (2.6 - i * 0.4)
        py = rp_y - 3.375
        net = get_net(board, rp_nets.get(pnum, 0))
        add_smd_pad(u1, pnum, px, py, 0.2, 0.75, net)

    for i in range(14):  # Left: pins 43-56
        pnum = i + 43
        px = rp_x - 3.375
        py = rp_y + (-2.6 + i * 0.4)
        net = get_net(board, rp_nets.get(pnum, 0))
        add_smd_pad(u1, pnum, px, py, 0.75, 0.2, net)

    # Exposed pad (GND)
    add_smd_pad(u1, 57, rp_x, rp_y, 3.1, 3.1, get_net(board, 1), pcbnew.PAD_SHAPE_RECT)

    # ─── W25Q16 Flash (U2) ────────────────────────────────────────────
    fl_x, fl_y = rp_x, rp_y + 8
    u2 = create_footprint(board, "U2", "W25Q16", fl_x, fl_y, 90)

    fl_nets = {1: 19, 2: 16, 3: 17, 4: 1, 5: 15, 6: 14, 7: 18, 8: 3}
    for i in range(4):  # Pins 1-4
        pnum = i + 1
        px = fl_x + (-1.905 + i * 1.27)
        py = fl_y + 2.475
        add_smd_pad(u2, pnum, px, py, 0.6, 1.55, get_net(board, fl_nets[pnum]))
    for i in range(4):  # Pins 5-8 (reversed)
        pnum = 8 - i
        px = fl_x + (-1.905 + i * 1.27)
        py = fl_y - 2.475
        add_smd_pad(u2, pnum, px, py, 0.6, 1.55, get_net(board, fl_nets[pnum]))

    # ─── 74HCT245 (U3) ────────────────────────────────────────────────
    ls_x = OX + 35
    u3 = create_footprint(board, "U3", "74HCT245", ls_x, rp_y, 90)

    ls_nets = {
        1: 1, 2: 6, 3: 7, 4: 8, 5: 9, 6: 10, 7: 11, 8: 1, 9: 1, 10: 1,
        11: 0, 12: 0, 13: 34, 14: 33, 15: 32, 16: 31, 17: 30, 18: 29, 19: 1, 20: 2
    }
    for i in range(10):  # Pins 1-10
        pnum = i + 1
        px = ls_x + (-5.715 + i * 1.27)
        py = rp_y + 3.75
        add_smd_pad(u3, pnum, px, py, 0.6, 1.78, get_net(board, ls_nets[pnum]))
    for i in range(10):  # Pins 11-20 (reversed)
        pnum = 20 - i
        px = ls_x + (-5.715 + i * 1.27)
        py = rp_y - 3.75
        add_smd_pad(u3, pnum, px, py, 0.6, 1.78, get_net(board, ls_nets[pnum]))

    # ─── XC6206 LDO (U4) ──────────────────────────────────────────────
    u4 = create_footprint(board, "U4", "XC6206", rp_x - 5, rp_y - 8)
    add_smd_pad(u4, 1, rp_x - 5 - 0.95, rp_y - 8 + 1.1, 0.8, 0.9, get_net(board, 1))   # GND
    add_smd_pad(u4, 2, rp_x - 5 + 0.95, rp_y - 8 + 1.1, 0.8, 0.9, get_net(board, 3))   # VOUT
    add_smd_pad(u4, 3, rp_x - 5, rp_y - 8 - 1.1, 0.8, 0.9, get_net(board, 2))           # VIN

    # ─── Crystal Y1 ───────────────────────────────────────────────────
    y1 = create_footprint(board, "Y1", "12MHz", rp_x + 6, rp_y - 6)
    add_smd_pad(y1, 1, rp_x + 6 - 1.1, rp_y - 6 - 0.85, 1.2, 1.0, get_net(board, 20))  # XIN
    add_smd_pad(y1, 2, rp_x + 6 + 1.1, rp_y - 6 - 0.85, 1.2, 1.0, get_net(board, 1))   # GND
    add_smd_pad(y1, 3, rp_x + 6 + 1.1, rp_y - 6 + 0.85, 1.2, 1.0, get_net(board, 21))  # XOUT
    add_smd_pad(y1, 4, rp_x + 6 - 1.1, rp_y - 6 + 0.85, 1.2, 1.0, get_net(board, 1))   # GND

    # ─── BOOTSEL Switch SW1 ───────────────────────────────────────────
    sw1 = create_footprint(board, "SW1", "BOOTSEL", rp_x - 6, rp_y + 8, 90)
    add_smd_pad(sw1, 1, rp_x - 6 - 3.1, rp_y + 8, 1.8, 1.1, get_net(board, 19))  # QSPI_SS
    add_smd_pad(sw1, 2, rp_x - 6 + 3.1, rp_y + 8, 1.8, 1.1, get_net(board, 1))   # GND

    # ─── USB-A J1 (through-hole) ──────────────────────────────────────
    j1 = create_footprint(board, "J1", "USB_A", OX + 2, rp_y, 90)
    add_th_pad(j1, 1, OX + 2, rp_y + 3.5, 1.5, 0.9, get_net(board, 26))  # VBUS_FUSED
    add_th_pad(j1, 2, OX + 2, rp_y + 1.0, 1.5, 0.9, get_net(board, 24))  # USB_DM_R
    add_th_pad(j1, 3, OX + 2, rp_y - 1.0, 1.5, 0.9, get_net(board, 25))  # USB_DP_R
    add_th_pad(j1, 4, OX + 2, rp_y - 3.5, 1.5, 0.9, get_net(board, 1))   # GND
    # Shield/mounting tabs
    add_th_pad(j1, 5, OX + 2 - 4, rp_y - 6, 2.5, 1.5, get_net(board, 1))
    add_th_pad(j1, 5, OX + 2 - 4, rp_y + 6, 2.5, 1.5, get_net(board, 1))

    # ─── DB-9 J2 (through-hole) ──────────────────────────────────────
    db_x = OX + BH - 2
    j2 = create_footprint(board, "J2", "DB9_Male", db_x, rp_y, 90)
    db9_nets = {1: 29, 2: 30, 3: 31, 4: 32, 5: 35, 6: 33, 7: 34, 8: 27, 9: 1}
    for i in range(5):  # Row 1: pins 1-5
        pnum = i + 1
        px = db_x + (-5.54 + i * 2.77)
        add_th_pad(j2, pnum, px, rp_y - 1.42, 1.6, 1.0, get_net(board, db9_nets[pnum]))
    for i in range(4):  # Row 2: pins 6-9
        pnum = i + 6
        px = db_x + (-4.155 + i * 2.77)
        add_th_pad(j2, pnum, px, rp_y + 1.42, 1.6, 1.0, get_net(board, db9_nets[pnum]))
    # Mounting holes
    add_th_pad(j2, 10, db_x - 12.5, rp_y, 3.2, 2.8, get_net(board, 1))
    add_th_pad(j2, 10, db_x + 12.5, rp_y, 3.2, 2.8, get_net(board, 1))

    # ─── Passives helper ──────────────────────────────────────────────
    def add_0402(ref, val, x, y, net1, net2, angle=0):
        """Add a 0402 2-pad component."""
        fp = create_footprint(board, ref, val, x, y, angle)
        add_smd_pad(fp, 1, x - 0.48, y, 0.56, 0.5, get_net(board, net1))
        add_smd_pad(fp, 2, x + 0.48, y, 0.56, 0.5, get_net(board, net2))
        return fp

    # LED D2
    d2 = create_footprint(board, "D2", "Green", rp_x + 6, rp_y - 9)
    add_smd_pad(d2, 1, rp_x + 6 - 0.75, rp_y - 9, 0.8, 0.75, get_net(board, 36))  # Anode
    add_smd_pad(d2, 2, rp_x + 6 + 0.75, rp_y - 9, 0.8, 0.75, get_net(board, 1))   # Cathode

    # Schottky diode D1 (cathode=+5V, anode=5V_MSX)
    d1 = create_footprint(board, "D1", "BAT54", OX + BH - 10, rp_y - 8)
    add_smd_pad(d1, 1, OX + BH - 10 - 1.15, rp_y - 8, 0.8, 0.6, get_net(board, 2))  # K → +5V
    add_smd_pad(d1, 2, OX + BH - 10 + 1.15, rp_y - 8, 0.8, 0.6, get_net(board, 35)) # A → 5V_MSX

    # Polyfuse F1
    f1 = create_footprint(board, "F1", "500mA", OX + 8, rp_y - 6)
    add_smd_pad(f1, 1, OX + 8 - 0.95, rp_y - 6, 1.0, 1.0, get_net(board, 2))   # +5V
    add_smd_pad(f1, 2, OX + 8 + 0.95, rp_y - 6, 1.0, 1.0, get_net(board, 26))  # VBUS_FUSED

    # Resistors
    add_0402("R1", "27R", OX + 10, rp_y - 2, 24, 5)     # USB D- series
    add_0402("R2", "27R", OX + 10, rp_y + 2, 25, 4)     # USB D+ series
    add_0402("R3", "2.2k", OX + BH - 8, rp_y + 4, 27, 12)  # Strobe divider top
    add_0402("R4", "3.3k", OX + BH - 8, rp_y + 7, 12, 1)   # Strobe divider bot
    add_0402("R5", "1k", rp_x + 6, rp_y - 7.5, 13, 36)     # LED resistor
    add_0402("R6", "10k", rp_x - 4, rp_y + 6, 19, 3)       # Flash CS pull-up
    add_0402("R7", "10k", rp_x + 4, rp_y - 4, 23, 3)       # RUN pull-up

    # Decoupling caps C1-C10 (100nF, +3V3 → GND)
    cap_pos = [
        (rp_x - 5, rp_y - 5), (rp_x - 3, rp_y - 5), (rp_x - 1, rp_y - 5),
        (rp_x + 1, rp_y - 5), (rp_x + 3, rp_y - 5),
        (rp_x - 5, rp_y + 5), (rp_x - 3, rp_y + 5), (rp_x - 1, rp_y + 5),
        (rp_x + 1, rp_y + 5), (rp_x + 3, rp_y + 5),
    ]
    for i, (cx, cy) in enumerate(cap_pos):
        add_0402(f"C{i+1}", "100nF", cx, cy, 3, 1)

    # Crystal load caps
    add_0402("C11", "27pF", rp_x + 4, rp_y - 6, 20, 1)   # XIN
    add_0402("C12", "27pF", rp_x + 8, rp_y - 6, 21, 1)   # XOUT

    # Other caps
    add_0402("C13", "1uF", rp_x - 6, rp_y - 2, 22, 1)    # DVDD decoupling
    add_0402("C14", "1uF", rp_x + 5, rp_y + 5, 3, 1)     # USB_VDD decoupling
    add_0402("C15", "1uF", rp_x - 7, rp_y - 8, 2, 1)     # LDO input
    add_0402("C16", "1uF", rp_x - 3, rp_y - 8, 3, 1)     # LDO output

    # ─── Ground zones ─────────────────────────────────────────────────
    gnd_net = board.FindNet("GND")

    for layer in [pcbnew.B_Cu, pcbnew.F_Cu]:
        zone = pcbnew.ZONE(board)
        zone.SetNet(gnd_net)
        zone.SetLayer(layer)
        zone.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        zone.SetMinThickness(mm(0.2))
        zone.SetThermalReliefGap(mm(0.5))
        zone.SetThermalReliefSpokeWidth(mm(0.5))
        zone.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        zone.SetLocalClearance(mm(0.3))

        # Zone outline
        outline = zone.Outline()
        outline.NewOutline()
        outline.Append(mm(OX - 0.5), mm(OY - 0.5))
        outline.Append(mm(OX + BH + 0.5), mm(OY - 0.5))
        outline.Append(mm(OX + BH + 0.5), mm(OY + BW + 0.5))
        outline.Append(mm(OX - 0.5), mm(OY + BW + 0.5))

        board.Add(zone)

    # ─── Silkscreen text ──────────────────────────────────────────────
    for text_str, tx, ty, sz in [("USB-MSX Mouse", OX + BH/2, OY + 2, 1.0),
                                   ("SoundResearch", OX + BH/2, OY + BW - 1.5, 0.8)]:
        text = pcbnew.PCB_TEXT(board)
        text.SetText(text_str)
        text.SetPosition(pt(tx, ty))
        text.SetLayer(pcbnew.F_SilkS)
        text.SetTextSize(pcbnew.VECTOR2I(mm(sz), mm(sz)))
        text.SetTextThickness(mm(sz * 0.15))
        text.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
        board.Add(text)

    # ─── Save ─────────────────────────────────────────────────────────
    board.Save(output_path)
    print(f"Generated: {output_path}")
    print(f"Nets: {len(NET_NAMES)}")
    print(f"Footprints: {len(board.GetFootprints())}")
    print(f"Board size: {BH}mm x {BW}mm")


if __name__ == "__main__":
    main()
