#!/usr/bin/env python3
"""
generate_schematic.py — Generate KiCad 8 schematic for USB-to-MSX mouse adapter.

Creates usb-to-msx-mouse.kicad_sch with all components, connections, and
embedded symbol definitions. Run this once, then open in KiCad 8 to verify.

Usage:
    python3 generate_schematic.py

The generated schematic includes:
    - RP2040 (QFN-56) with QSPI flash, crystal, decoupling
    - USB-A host port with series resistors
    - 74HCT245 level shifter (3.3V → 5V)
    - DB-9 male connector for MSX output
    - Power section: 5V input, LDO to 3.3V, protection
    - BOOTSEL button, status LED
"""

import uuid
import os

def uid():
    """Generate a KiCad-style UUID."""
    return str(uuid.uuid4())

# ─── Symbol library definitions ─────────────────────────────────────────────
# These are embedded in the schematic so it's self-contained.

def sym_rp2040():
    """RP2040 microcontroller symbol — 56 pins + exposed pad."""
    # Pin definitions: (number, name, x_offset, y_offset, direction)
    # We'll arrange pins in 4 groups: left, right, top, bottom
    left_pins = [
        # GPIO pins on left side
        ("2", "GPIO0", -16.51, 22.86, "R"),
        ("3", "GPIO1", -16.51, 20.32, "R"),
        ("4", "GPIO2", -16.51, 17.78, "R"),
        ("5", "GPIO3", -16.51, 15.24, "R"),
        ("6", "GPIO4", -16.51, 12.7, "R"),
        ("7", "GPIO5", -16.51, 10.16, "R"),
        ("8", "GPIO6", -16.51, 7.62, "R"),
        ("9", "GPIO7", -16.51, 5.08, "R"),
        ("11", "GPIO8", -16.51, 2.54, "R"),
        ("12", "GPIO9", -16.51, 0, "R"),
        ("13", "GPIO10", -16.51, -2.54, "R"),
        ("14", "GPIO11", -16.51, -5.08, "R"),
        ("15", "GPIO12", -16.51, -7.62, "R"),
        ("16", "GPIO13", -16.51, -10.16, "R"),
        ("18", "GPIO14", -16.51, -12.7, "R"),
        ("19", "GPIO15", -16.51, -15.24, "R"),
    ]
    right_pins = [
        ("28", "GPIO16", 16.51, 22.86, "L"),
        ("29", "GPIO17", 16.51, 20.32, "L"),
        ("30", "GPIO18", 16.51, 17.78, "L"),
        ("31", "GPIO19", 16.51, 15.24, "L"),
        ("32", "GPIO20", 16.51, 12.7, "L"),
        ("33", "GPIO21", 16.51, 10.16, "L"),
        ("35", "GPIO22", 16.51, 7.62, "L"),
        ("36", "GPIO23", 16.51, 5.08, "L"),
        ("37", "GPIO24", 16.51, 2.54, "L"),
        ("38", "GPIO25", 16.51, 0, "L"),
        ("39", "GPIO26/ADC0", 16.51, -2.54, "L"),
        ("40", "GPIO27/ADC1", 16.51, -5.08, "L"),
        ("41", "GPIO28/ADC2", 16.51, -7.62, "L"),
        ("42", "GPIO29/ADC3", 16.51, -10.16, "L"),
        ("25", "SWCLK", 16.51, -12.7, "L"),
        ("26", "SWD", 16.51, -15.24, "L"),
    ]
    top_pins = [
        # Power pins on top
        ("1", "IOVDD", -10.16, 29.21, "D"),
        ("10", "IOVDD", -7.62, 29.21, "D"),
        ("17", "IOVDD", -5.08, 29.21, "D"),
        ("23", "IOVDD", -2.54, 29.21, "D"),
        ("34", "IOVDD", 0, 29.21, "D"),
        ("43", "IOVDD", 2.54, 29.21, "D"),
        ("50", "IOVDD", 5.08, 29.21, "D"),
        ("49", "USB_VDD", 7.62, 29.21, "D"),
        ("44", "ADC_AVDD", 10.16, 29.21, "D"),
    ]
    bottom_pins = [
        # QSPI, USB, power, control on bottom
        ("47", "USB_DM", -12.7, -21.59, "U"),
        ("48", "USB_DP", -10.16, -21.59, "U"),
        ("52", "QSPI_SCLK", -7.62, -21.59, "U"),
        ("53", "QSPI_SD0", -5.08, -21.59, "U"),
        ("55", "QSPI_SD1", -2.54, -21.59, "U"),
        ("54", "QSPI_SD2", 0, -21.59, "U"),
        ("51", "QSPI_SD3", 2.54, -21.59, "U"),
        ("56", "QSPI_SS", 5.08, -21.59, "U"),
        ("21", "XIN", 7.62, -21.59, "U"),
        ("22", "XOUT", 10.16, -21.59, "U"),
        ("24", "DVDD", -12.7, -26.67, "U"),
        ("45", "VREG_VIN", -7.62, -26.67, "U"),
        ("46", "VREG_VOUT", -2.54, -26.67, "U"),
        ("20", "TESTEN", 2.54, -26.67, "U"),
        ("27", "RUN", 7.62, -26.67, "U"),
        ("57", "GND", 12.7, -26.67, "U"),
    ]

    lines = []
    lines.append('    (symbol "usb_msx:RP2040"')
    lines.append('      (pin_names (offset 1.016))')
    lines.append('      (exclude_from_sim no)')
    lines.append('      (in_bom yes)')
    lines.append('      (on_board yes)')
    lines.append('      (property "Reference" "U" (at 0 31.75 0) (effects (font (size 1.27 1.27))))')
    lines.append('      (property "Value" "RP2040" (at 0 -29.21 0) (effects (font (size 1.27 1.27))))')
    lines.append('      (property "Footprint" "Package_DFN_QFN:QFN-56-1EP_7x7mm_P0.4mm" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append('      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append('      (property "JLCPCB" "C2040" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append('      (symbol "usb_msx:RP2040_0_1"')
    lines.append('        (rectangle (start -15.24 27.94) (end 15.24 -25.4) (stroke (width 0.254) (type default)) (fill (type background)))')
    lines.append('      )')
    lines.append('      (symbol "usb_msx:RP2040_1_1"')

    all_pins = left_pins + right_pins + top_pins + bottom_pins
    for pnum, pname, px, py, pdir in all_pins:
        ptype = "power_in" if pname in ("IOVDD", "USB_VDD", "ADC_AVDD", "DVDD", "VREG_VIN", "GND") else \
                "power_out" if pname == "VREG_VOUT" else \
                "input" if pname in ("XIN", "TESTEN", "RUN", "QSPI_SS") else \
                "bidirectional"
        lines.append(f'        (pin {ptype} line (at {px} {py} 0) (length 2.54) (name "{pname}" (effects (font (size 1.016 1.016)))) (number "{pnum}" (effects (font (size 1.016 1.016)))))')

    lines.append('      )')
    lines.append('    )')
    return '\n'.join(lines)


def sym_w25q16():
    """W25Q16JVSNIQ QSPI flash symbol — 8 pins."""
    return '''    (symbol "usb_msx:W25Q16JVSNIQ"
      (pin_names (offset 1.016))
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "U" (at 0 7.62 0) (effects (font (size 1.27 1.27))))
      (property "Value" "W25Q16JVSNIQ" (at 0 -7.62 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "JLCPCB" "C131024" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "usb_msx:W25Q16JVSNIQ_0_1"
        (rectangle (start -7.62 6.35) (end 7.62 -6.35) (stroke (width 0.254) (type default)) (fill (type background)))
      )
      (symbol "usb_msx:W25Q16JVSNIQ_1_1"
        (pin input line (at -10.16 3.81 0) (length 2.54) (name "~{CS}" (effects (font (size 1.016 1.016)))) (number "1" (effects (font (size 1.016 1.016)))))
        (pin output line (at 10.16 3.81 180) (length 2.54) (name "DO/IO1" (effects (font (size 1.016 1.016)))) (number "2" (effects (font (size 1.016 1.016)))))
        (pin input line (at 10.16 1.27 180) (length 2.54) (name "~{WP}/IO2" (effects (font (size 1.016 1.016)))) (number "3" (effects (font (size 1.016 1.016)))))
        (pin power_in line (at 0 -8.89 90) (length 2.54) (name "GND" (effects (font (size 1.016 1.016)))) (number "4" (effects (font (size 1.016 1.016)))))
        (pin input line (at -10.16 1.27 0) (length 2.54) (name "DI/IO0" (effects (font (size 1.016 1.016)))) (number "5" (effects (font (size 1.016 1.016)))))
        (pin input line (at -10.16 -1.27 0) (length 2.54) (name "CLK" (effects (font (size 1.016 1.016)))) (number "6" (effects (font (size 1.016 1.016)))))
        (pin input line (at 10.16 -1.27 180) (length 2.54) (name "~{HOLD}/IO3" (effects (font (size 1.016 1.016)))) (number "7" (effects (font (size 1.016 1.016)))))
        (pin power_in line (at 0 8.89 270) (length 2.54) (name "VCC" (effects (font (size 1.016 1.016)))) (number "8" (effects (font (size 1.016 1.016)))))
      )
    )'''


def sym_74hct245():
    """74HCT245 octal bus transceiver — 20 pins."""
    return '''    (symbol "usb_msx:74HCT245"
      (pin_names (offset 1.016))
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "U" (at 0 16.51 0) (effects (font (size 1.27 1.27))))
      (property "Value" "74HCT245" (at 0 -16.51 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "JLCPCB" "C6636" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "usb_msx:74HCT245_0_1"
        (rectangle (start -10.16 15.24) (end 10.16 -15.24) (stroke (width 0.254) (type default)) (fill (type background)))
      )
      (symbol "usb_msx:74HCT245_1_1"
        (pin input line (at -12.7 12.7 0) (length 2.54) (name "DIR" (effects (font (size 1.016 1.016)))) (number "1" (effects (font (size 1.016 1.016)))))
        (pin bidirectional line (at -12.7 10.16 0) (length 2.54) (name "A1" (effects (font (size 1.016 1.016)))) (number "2" (effects (font (size 1.016 1.016)))))
        (pin bidirectional line (at -12.7 7.62 0) (length 2.54) (name "A2" (effects (font (size 1.016 1.016)))) (number "3" (effects (font (size 1.016 1.016)))))
        (pin bidirectional line (at -12.7 5.08 0) (length 2.54) (name "A3" (effects (font (size 1.016 1.016)))) (number "4" (effects (font (size 1.016 1.016)))))
        (pin bidirectional line (at -12.7 2.54 0) (length 2.54) (name "A4" (effects (font (size 1.016 1.016)))) (number "5" (effects (font (size 1.016 1.016)))))
        (pin bidirectional line (at -12.7 0 0) (length 2.54) (name "A5" (effects (font (size 1.016 1.016)))) (number "6" (effects (font (size 1.016 1.016)))))
        (pin bidirectional line (at -12.7 -2.54 0) (length 2.54) (name "A6" (effects (font (size 1.016 1.016)))) (number "7" (effects (font (size 1.016 1.016)))))
        (pin bidirectional line (at -12.7 -5.08 0) (length 2.54) (name "A7" (effects (font (size 1.016 1.016)))) (number "8" (effects (font (size 1.016 1.016)))))
        (pin bidirectional line (at -12.7 -7.62 0) (length 2.54) (name "A8" (effects (font (size 1.016 1.016)))) (number "9" (effects (font (size 1.016 1.016)))))
        (pin power_in line (at 0 -17.78 90) (length 2.54) (name "GND" (effects (font (size 1.016 1.016)))) (number "10" (effects (font (size 1.016 1.016)))))
        (pin bidirectional line (at 12.7 -7.62 180) (length 2.54) (name "B8" (effects (font (size 1.016 1.016)))) (number "11" (effects (font (size 1.016 1.016)))))
        (pin bidirectional line (at 12.7 -5.08 180) (length 2.54) (name "B7" (effects (font (size 1.016 1.016)))) (number "12" (effects (font (size 1.016 1.016)))))
        (pin bidirectional line (at 12.7 -2.54 180) (length 2.54) (name "B6" (effects (font (size 1.016 1.016)))) (number "13" (effects (font (size 1.016 1.016)))))
        (pin bidirectional line (at 12.7 0 180) (length 2.54) (name "B5" (effects (font (size 1.016 1.016)))) (number "14" (effects (font (size 1.016 1.016)))))
        (pin bidirectional line (at 12.7 2.54 180) (length 2.54) (name "B4" (effects (font (size 1.016 1.016)))) (number "15" (effects (font (size 1.016 1.016)))))
        (pin bidirectional line (at 12.7 5.08 180) (length 2.54) (name "B3" (effects (font (size 1.016 1.016)))) (number "16" (effects (font (size 1.016 1.016)))))
        (pin bidirectional line (at 12.7 7.62 180) (length 2.54) (name "B2" (effects (font (size 1.016 1.016)))) (number "17" (effects (font (size 1.016 1.016)))))
        (pin bidirectional line (at 12.7 10.16 180) (length 2.54) (name "B1" (effects (font (size 1.016 1.016)))) (number "18" (effects (font (size 1.016 1.016)))))
        (pin input line (at -12.7 -10.16 0) (length 2.54) (name "~{OE}" (effects (font (size 1.016 1.016)))) (number "19" (effects (font (size 1.016 1.016)))))
        (pin power_in line (at 0 17.78 270) (length 2.54) (name "VCC" (effects (font (size 1.016 1.016)))) (number "20" (effects (font (size 1.016 1.016)))))
      )
    )'''


def sym_generic_2pin(name, ref, value, footprint, jlcpcb=""):
    """Generic 2-pin symbol (capacitor, resistor, LED, fuse, diode, etc.)."""
    jlc_prop = ""
    if jlcpcb:
        jlc_prop = f'\n      (property "JLCPCB" "{jlcpcb}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))'
    return f'''    (symbol "usb_msx:{name}"
      (pin_names (offset 0) hide)
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "{ref}" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "{name}" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "{footprint}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide)){jlc_prop}
      (symbol "usb_msx:{name}_0_1"
        (polyline (pts (xy 0 1.27) (xy 0 -1.27)) (stroke (width 0) (type default)) (fill (type none)))
      )
      (symbol "usb_msx:{name}_1_1"
        (pin passive line (at 0 3.81 270) (length 2.54) (name "1" (effects (font (size 1.016 1.016)))) (number "1" (effects (font (size 1.016 1.016)))))
        (pin passive line (at 0 -3.81 90) (length 2.54) (name "2" (effects (font (size 1.016 1.016)))) (number "2" (effects (font (size 1.016 1.016)))))
      )
    )'''


def sym_xc6206():
    """XC6206P332MR 3.3V LDO — 3 pins SOT-23."""
    return '''    (symbol "usb_msx:XC6206P332MR"
      (pin_names (offset 1.016))
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "U" (at 0 7.62 0) (effects (font (size 1.27 1.27))))
      (property "Value" "XC6206P332MR" (at 0 -7.62 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_TO_SOT_SMD:SOT-23" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "JLCPCB" "C5446" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "usb_msx:XC6206P332MR_0_1"
        (rectangle (start -7.62 6.35) (end 7.62 -6.35) (stroke (width 0.254) (type default)) (fill (type background)))
      )
      (symbol "usb_msx:XC6206P332MR_1_1"
        (pin power_in line (at 0 -8.89 90) (length 2.54) (name "GND" (effects (font (size 1.016 1.016)))) (number "1" (effects (font (size 1.016 1.016)))))
        (pin power_out line (at 10.16 0 180) (length 2.54) (name "VOUT" (effects (font (size 1.016 1.016)))) (number "2" (effects (font (size 1.016 1.016)))))
        (pin power_in line (at -10.16 0 0) (length 2.54) (name "VIN" (effects (font (size 1.016 1.016)))) (number "3" (effects (font (size 1.016 1.016)))))
      )
    )'''


def sym_crystal():
    """4-pin crystal symbol (3225 package)."""
    return '''    (symbol "usb_msx:Crystal_4Pin"
      (pin_names (offset 1.016) hide)
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "Y" (at 0 5.08 0) (effects (font (size 1.27 1.27))))
      (property "Value" "12MHz" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "JLCPCB" "C9002" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "usb_msx:Crystal_4Pin_0_1"
        (polyline (pts (xy -1.27 -2.54) (xy -1.27 2.54)) (stroke (width 0.254) (type default)) (fill (type none)))
        (polyline (pts (xy 1.27 -2.54) (xy 1.27 2.54)) (stroke (width 0.254) (type default)) (fill (type none)))
        (rectangle (start -0.635 2.54) (end 0.635 -2.54) (stroke (width 0.254) (type default)) (fill (type none)))
      )
      (symbol "usb_msx:Crystal_4Pin_1_1"
        (pin passive line (at -3.81 0 0) (length 2.54) (name "1" (effects (font (size 1.016 1.016)))) (number "1" (effects (font (size 1.016 1.016)))))
        (pin passive line (at 3.81 0 180) (length 2.54) (name "3" (effects (font (size 1.016 1.016)))) (number "3" (effects (font (size 1.016 1.016)))))
        (pin passive line (at 0 -3.81 90) (length 1.27) (name "2" (effects (font (size 1.016 1.016)))) (number "2" (effects (font (size 1.016 1.016)))))
        (pin passive line (at 0 -3.81 90) (length 1.27) (name "4" (effects (font (size 1.016 1.016)))) (number "4" (effects (font (size 1.016 1.016)))))
      )
    )'''


def sym_usb_a():
    """USB-A female connector — 4 signal pins + shield."""
    return '''    (symbol "usb_msx:USB_A"
      (pin_names (offset 1.016))
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "J" (at 0 8.89 0) (effects (font (size 1.27 1.27))))
      (property "Value" "USB_A" (at 0 -8.89 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Connector_USB:USB_A_Molex_67643_Horizontal" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "usb_msx:USB_A_0_1"
        (rectangle (start -5.08 7.62) (end 5.08 -7.62) (stroke (width 0.254) (type default)) (fill (type background)))
      )
      (symbol "usb_msx:USB_A_1_1"
        (pin power_out line (at 7.62 5.08 180) (length 2.54) (name "VBUS" (effects (font (size 1.016 1.016)))) (number "1" (effects (font (size 1.016 1.016)))))
        (pin bidirectional line (at 7.62 2.54 180) (length 2.54) (name "D-" (effects (font (size 1.016 1.016)))) (number "2" (effects (font (size 1.016 1.016)))))
        (pin bidirectional line (at 7.62 0 180) (length 2.54) (name "D+" (effects (font (size 1.016 1.016)))) (number "3" (effects (font (size 1.016 1.016)))))
        (pin power_in line (at 7.62 -2.54 180) (length 2.54) (name "GND" (effects (font (size 1.016 1.016)))) (number "4" (effects (font (size 1.016 1.016)))))
        (pin passive line (at 7.62 -5.08 180) (length 2.54) (name "Shield" (effects (font (size 1.016 1.016)))) (number "5" (effects (font (size 1.016 1.016)))))
      )
    )'''


def sym_db9_male():
    """DB-9 male connector for MSX mouse port."""
    return '''    (symbol "usb_msx:DB9_Male"
      (pin_names (offset 1.016))
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "J" (at 0 15.24 0) (effects (font (size 1.27 1.27))))
      (property "Value" "DB9_Male" (at 0 -15.24 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Connector_Dsub:DSUB-9_Male_Horizontal_P2.77x2.84mm_EdgePinOffset7.70mm_Housed_MountingHolesOffset9.12mm" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "usb_msx:DB9_Male_0_1"
        (rectangle (start -5.08 13.97) (end 5.08 -13.97) (stroke (width 0.254) (type default)) (fill (type background)))
      )
      (symbol "usb_msx:DB9_Male_1_1"
        (pin passive line (at 7.62 11.43 180) (length 2.54) (name "1" (effects (font (size 1.016 1.016)))) (number "1" (effects (font (size 1.016 1.016)))))
        (pin passive line (at 7.62 8.89 180) (length 2.54) (name "2" (effects (font (size 1.016 1.016)))) (number "2" (effects (font (size 1.016 1.016)))))
        (pin passive line (at 7.62 6.35 180) (length 2.54) (name "3" (effects (font (size 1.016 1.016)))) (number "3" (effects (font (size 1.016 1.016)))))
        (pin passive line (at 7.62 3.81 180) (length 2.54) (name "4" (effects (font (size 1.016 1.016)))) (number "4" (effects (font (size 1.016 1.016)))))
        (pin passive line (at 7.62 1.27 180) (length 2.54) (name "5" (effects (font (size 1.016 1.016)))) (number "5" (effects (font (size 1.016 1.016)))))
        (pin passive line (at 7.62 -1.27 180) (length 2.54) (name "6" (effects (font (size 1.016 1.016)))) (number "6" (effects (font (size 1.016 1.016)))))
        (pin passive line (at 7.62 -3.81 180) (length 2.54) (name "7" (effects (font (size 1.016 1.016)))) (number "7" (effects (font (size 1.016 1.016)))))
        (pin passive line (at 7.62 -6.35 180) (length 2.54) (name "8" (effects (font (size 1.016 1.016)))) (number "8" (effects (font (size 1.016 1.016)))))
        (pin passive line (at 7.62 -8.89 180) (length 2.54) (name "9" (effects (font (size 1.016 1.016)))) (number "9" (effects (font (size 1.016 1.016)))))
        (pin passive line (at 7.62 -11.43 180) (length 2.54) (name "10" (effects (font (size 1.016 1.016)))) (number "10" (effects (font (size 1.016 1.016)))))
      )
    )'''


def sym_sw_push():
    """Tactile push switch — 2 pins."""
    return '''    (symbol "usb_msx:SW_Push"
      (pin_names (offset 1.016) hide)
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "SW" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
      (property "Value" "SW_Push" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Button_Switch_SMD:SW_SPST_TL3342" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "usb_msx:SW_Push_0_1"
        (circle (center -2.032 0) (radius 0.508) (stroke (width 0) (type default)) (fill (type none)))
        (circle (center 2.032 0) (radius 0.508) (stroke (width 0) (type default)) (fill (type none)))
        (polyline (pts (xy -1.524 1.016) (xy 1.524 1.016)) (stroke (width 0) (type default)) (fill (type none)))
        (polyline (pts (xy 0 1.016) (xy 0 2.032)) (stroke (width 0) (type default)) (fill (type none)))
      )
      (symbol "usb_msx:SW_Push_1_1"
        (pin passive line (at -5.08 0 0) (length 2.54) (name "1" (effects (font (size 1.016 1.016)))) (number "1" (effects (font (size 1.016 1.016)))))
        (pin passive line (at 5.08 0 180) (length 2.54) (name "2" (effects (font (size 1.016 1.016)))) (number "2" (effects (font (size 1.016 1.016)))))
      )
    )'''


def sym_power(name, ptype="power_in"):
    """Power flag symbol (+5V, +3V3, GND)."""
    return f'''    (symbol "usb_msx:{name}"
      (power)
      (pin_names (offset 0) hide)
      (exclude_from_sim no)
      (in_bom no)
      (on_board yes)
      (property "Reference" "#{name}" (at 0 2.54 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "{name}" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "usb_msx:{name}_0_1"
        (polyline (pts (xy 0 0) (xy 0 1.27)) (stroke (width 0) (type default)) (fill (type none)))
        (polyline (pts (xy -0.762 1.27) (xy 0.762 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))
      )
      (symbol "usb_msx:{name}_1_1"
        (pin {ptype} line (at 0 0 90) (length 0) (name "{name}" (effects (font (size 1.016 1.016)))) (number "1" (effects (font (size 1.016 1.016)))))
      )
    )'''


# ─── Schematic generation ───────────────────────────────────────────────────

def generate_schematic():
    """Generate the complete KiCad 8 schematic file."""

    # Component instance helper
    instances = []  # (ref, unit, uuid)

    def component(lib_id, ref, value, x, y, angle=0, mirror="", properties=None):
        """Generate a component instance and return its UUID."""
        u = uid()
        inst_uuid = uid()
        instances.append((ref, 1, f"/{u}"))

        props = []
        props.append(f'    (property "Reference" "{ref}" (at {x+2} {y+2} 0) (effects (font (size 1.27 1.27))))')
        props.append(f'    (property "Value" "{value}" (at {x+2} {y-2} 0) (effects (font (size 1.27 1.27))))')

        if properties:
            for pname, pval in properties.items():
                props.append(f'    (property "{pname}" "{pval}" (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide))')

        mirror_str = f" (mirror {mirror})" if mirror else ""
        return f'''  (symbol
    (lib_id "usb_msx:{lib_id}")
    (at {x} {y} {angle})
    (uuid "{u}")
    {chr(10).join(props)}
    (instances
      (project "usb-to-msx-mouse"
        (path "/{uid()}" (reference "{ref}") (unit 1))
      )
    )
  )'''

    def wire(x1, y1, x2, y2):
        """Generate a wire segment."""
        return f'  (wire (pts (xy {x1} {y1}) (xy {x2} {y2})) (stroke (width 0) (type default)) (uuid "{uid()}"))'

    def label(name, x, y, angle=0):
        """Generate a net label."""
        return f'  (label "{name}" (at {x} {y} {angle}) (effects (font (size 1.27 1.27))) (uuid "{uid()}"))'

    def global_label(name, x, y, angle=0, shape="input"):
        """Generate a global label."""
        return f'  (global_label "{name}" (at {x} {y} {angle}) (shape {shape}) (effects (font (size 1.27 1.27))) (uuid "{uid()}"))'

    def power_sym(name, x, y, angle=0):
        """Place a power symbol."""
        u = uid()
        return f'''  (symbol
    (lib_id "usb_msx:{name}")
    (at {x} {y} {angle})
    (uuid "{u}")
    (property "Reference" "#{name}" (at {x} {y+2} 0) (effects (font (size 1.27 1.27)) hide))
    (property "Value" "{name}" (at {x} {y+3} 0) (effects (font (size 1.27 1.27))))
    (instances
      (project "usb-to-msx-mouse"
        (path "/{uid()}" (reference "#{name}") (unit 1))
      )
    )
  )'''

    def junction(x, y):
        """Generate a junction point."""
        return f'  (junction (at {x} {y}) (diameter 0) (color 0 0 0 0) (uuid "{uid()}"))'

    def no_connect(x, y):
        """Generate a no-connect marker."""
        return f'  (no_connect (at {x} {y}) (uuid "{uid()}"))'

    def text_note(text, x, y, size=2.0):
        """Generate a text note."""
        return f'  (text "{text}" (at {x} {y} 0) (effects (font (size {size} {size}))) (uuid "{uid()}"))'

    # ─── Build the schematic ────────────────────────────────────────────

    elements = []  # All schematic elements (components, wires, labels)

    # === Section: Title and notes ===
    elements.append(text_note("USB-to-MSX Mouse Adapter for Roland S-760", 20, 15))
    elements.append(text_note("RP2040 + 74HCT245 + USB-A Host + DB-9 MSX Output", 20, 20))

    # === Section: RP2040 (center of schematic) ===
    # Place RP2040 at center
    rp_x, rp_y = 130, 100
    elements.append(component("RP2040", "U1", "RP2040", rp_x, rp_y))

    # === Section: QSPI Flash (below RP2040) ===
    fl_x, fl_y = 130, 155
    elements.append(component("W25Q16JVSNIQ", "U2", "W25Q16JVSNIQ", fl_x, fl_y))

    # Flash connections to RP2040 QSPI pins
    # RP2040 QSPI_SCLK (pin 52) at rp_x-7.62, rp_y+21.59 → Flash CLK (pin 6) at fl_x-10.16, fl_y-1.27
    elements.append(label("QSPI_SCLK", rp_x - 7.62, rp_y + 21.59, 270))
    elements.append(label("QSPI_SCLK", fl_x - 13, fl_y - 1.27, 0))
    # QSPI_SD0
    elements.append(label("QSPI_SD0", rp_x - 5.08, rp_y + 21.59, 270))
    elements.append(label("QSPI_SD0", fl_x - 13, fl_y + 1.27, 0))
    # QSPI_SD1
    elements.append(label("QSPI_SD1", rp_x - 2.54, rp_y + 21.59, 270))
    elements.append(label("QSPI_SD1", fl_x + 13, fl_y + 3.81, 180))
    # QSPI_SD2
    elements.append(label("QSPI_SD2", rp_x, rp_y + 21.59, 270))
    elements.append(label("QSPI_SD2", fl_x + 13, fl_y + 1.27, 180))
    # QSPI_SD3
    elements.append(label("QSPI_SD3", rp_x + 2.54, rp_y + 21.59, 270))
    elements.append(label("QSPI_SD3", fl_x + 13, fl_y - 1.27, 180))
    # QSPI_SS → Flash ~CS
    elements.append(label("QSPI_SS", rp_x + 5.08, rp_y + 21.59, 270))
    elements.append(label("QSPI_SS", fl_x - 13, fl_y + 3.81, 0))

    # Flash power
    elements.append(power_sym("+3V3", fl_x, fl_y - 8.89, 180))
    elements.append(power_sym("GND", fl_x, fl_y + 8.89))

    # Flash CS pull-up resistor (10kΩ)
    elements.append(component("R", "R6", "10k", fl_x - 18, fl_y - 5))
    elements.append(label("QSPI_SS", fl_x - 18, fl_y - 5 + 3.81, 90))
    elements.append(power_sym("+3V3", fl_x - 18, fl_y - 5 - 3.81, 180))

    # === Section: 12MHz Crystal (below-right of RP2040) ===
    cr_x, cr_y = 155, 135
    elements.append(component("Crystal_4Pin", "Y1", "12MHz", cr_x, cr_y))

    # Crystal connections to XIN/XOUT
    elements.append(label("XIN", rp_x + 7.62, rp_y + 21.59, 270))
    elements.append(label("XIN", cr_x - 5, cr_y, 0))
    elements.append(label("XOUT", rp_x + 10.16, rp_y + 21.59, 270))
    elements.append(label("XOUT", cr_x + 5, cr_y, 180))

    # Crystal load caps (27pF each)
    elements.append(component("C", "C11", "27pF", cr_x - 5, cr_y + 8))
    elements.append(label("XIN", cr_x - 5, cr_y + 8 - 3.81, 90))
    elements.append(power_sym("GND", cr_x - 5, cr_y + 8 + 3.81))

    elements.append(component("C", "C12", "27pF", cr_x + 5, cr_y + 8))
    elements.append(label("XOUT", cr_x + 5, cr_y + 8 - 3.81, 90))
    elements.append(power_sym("GND", cr_x + 5, cr_y + 8 + 3.81))

    # Crystal GND pins
    elements.append(power_sym("GND", cr_x, cr_y + 3.81))

    # === Section: RP2040 Power Connections ===
    # IOVDD pins — all to +3V3
    for offset in [-10.16, -7.62, -5.08, -2.54, 0, 2.54, 5.08]:
        elements.append(power_sym("+3V3", rp_x + offset, rp_y - 29.21, 180))

    # USB_VDD
    elements.append(power_sym("+3V3", rp_x + 7.62, rp_y - 29.21, 180))
    # ADC_AVDD
    elements.append(power_sym("+3V3", rp_x + 10.16, rp_y - 29.21, 180))

    # DVDD — internal 1.1V core (needs 1µF decoupling, connected to VREG_VOUT)
    elements.append(label("DVDD", rp_x - 12.7, rp_y + 26.67, 270))

    # VREG_VIN — connect to 3.3V
    elements.append(power_sym("+3V3", rp_x - 7.62, rp_y + 30, 180))
    elements.append(wire(rp_x - 7.62, rp_y + 26.67, rp_x - 7.62, rp_y + 30))

    # VREG_VOUT — 1.1V core, connect to DVDD with decoupling cap
    elements.append(label("VREG_VOUT", rp_x - 2.54, rp_y + 26.67, 270))
    elements.append(label("DVDD", rp_x - 2.54, rp_y + 30, 270))
    # Connect VREG_VOUT to DVDD
    elements.append(component("C", "C13", "1uF", rp_x - 8, rp_y + 33))
    elements.append(label("DVDD", rp_x - 8, rp_y + 33 - 3.81, 90))
    elements.append(power_sym("GND", rp_x - 8, rp_y + 33 + 3.81))

    # TESTEN — tie to GND
    elements.append(power_sym("GND", rp_x + 2.54, rp_y + 30))
    elements.append(wire(rp_x + 2.54, rp_y + 26.67, rp_x + 2.54, rp_y + 30))

    # RUN — pull up to 3.3V with optional reset button
    elements.append(component("R", "R7", "10k", rp_x + 12, rp_y + 33))
    elements.append(power_sym("+3V3", rp_x + 12, rp_y + 33 - 3.81, 180))
    elements.append(wire(rp_x + 7.62, rp_y + 26.67, rp_x + 12, rp_y + 26.67))
    elements.append(wire(rp_x + 12, rp_y + 26.67, rp_x + 12, rp_y + 33 + 3.81))

    # GND (exposed pad)
    elements.append(power_sym("GND", rp_x + 12.7, rp_y + 30))
    elements.append(wire(rp_x + 12.7, rp_y + 26.67, rp_x + 12.7, rp_y + 30))

    # === Section: Decoupling capacitors for RP2040 ===
    for i, cx in enumerate(range(100, 126, 3)):
        ref = f"C{i+1}"
        elements.append(component("C", ref, "100nF", cx, rp_y - 38))
        elements.append(power_sym("+3V3", cx, rp_y - 38 - 3.81, 180))
        elements.append(power_sym("GND", cx, rp_y - 38 + 3.81))
        if i >= 9:
            break

    # 1µF cap for USB_VDD
    elements.append(component("C", "C14", "1uF", 128, rp_y - 38))
    elements.append(power_sym("+3V3", 128, rp_y - 38 - 3.81, 180))
    elements.append(power_sym("GND", 128, rp_y - 38 + 3.81))

    # === Section: BOOTSEL Button (connected to QSPI_SS) ===
    bs_x, bs_y = 100, 155
    elements.append(component("SW_Push", "SW1", "BOOTSEL", bs_x, bs_y))
    elements.append(label("QSPI_SS", bs_x - 7, bs_y, 0))
    elements.append(power_sym("GND", bs_x + 7, bs_y))

    # === Section: USB-A Host Port (left side) ===
    usb_x, usb_y = 40, 85
    elements.append(component("USB_A", "J1", "USB_A", usb_x, usb_y))

    # USB VBUS output — from 5V rail through polyfuse
    elements.append(component("Polyfuse", "F1", "500mA", usb_x + 18, usb_y - 10))
    elements.append(power_sym("+5V", usb_x + 18, usb_y - 10 - 3.81, 180))
    elements.append(wire(usb_x + 7.62, usb_y - 5.08 + 10.16, usb_x + 18, usb_y - 5.08 + 10.16))
    elements.append(wire(usb_x + 18, usb_y - 5.08 + 10.16, usb_x + 18, usb_y - 10 + 3.81))

    # USB D- with 27Ω series resistor
    elements.append(component("R", "R1", "27R", usb_x + 25, usb_y - 2))
    elements.append(label("USB_DM", usb_x + 25, usb_y - 2 - 3.81, 90))
    elements.append(wire(usb_x + 7.62, usb_y + 2.54, usb_x + 25, usb_y + 2.54))
    elements.append(wire(usb_x + 25, usb_y + 2.54, usb_x + 25, usb_y - 2 + 3.81))

    # USB D+ with 27Ω series resistor
    elements.append(component("R", "R2", "27R", usb_x + 32, usb_y - 2))
    elements.append(label("USB_DP", usb_x + 32, usb_y - 2 - 3.81, 90))
    elements.append(wire(usb_x + 7.62, usb_y, usb_x + 32, usb_y))
    elements.append(wire(usb_x + 32, usb_y, usb_x + 32, usb_y - 2 + 3.81))

    # USB D+/D- labels to RP2040
    elements.append(label("USB_DM", rp_x - 12.7, rp_y + 21.59, 270))
    elements.append(label("USB_DP", rp_x - 10.16, rp_y + 21.59, 270))

    # USB GND
    elements.append(power_sym("GND", usb_x + 7.62 + 3, usb_y + 2.54 + 5))
    elements.append(wire(usb_x + 7.62, usb_y + 2.54, usb_x + 7.62 + 3, usb_y + 2.54))
    # Shield to GND
    elements.append(wire(usb_x + 7.62, usb_y + 5.08, usb_x + 7.62 + 3, usb_y + 5.08))
    elements.append(power_sym("GND", usb_x + 7.62 + 3, usb_y + 5.08 + 2))

    # === Section: 74HCT245 Level Shifter (right side) ===
    ls_x, ls_y = 200, 100
    elements.append(component("74HCT245", "U3", "74HCT245", ls_x, ls_y))

    # 74HCT245 power
    elements.append(power_sym("+5V", ls_x, ls_y - 17.78, 180))
    elements.append(power_sym("GND", ls_x, ls_y + 17.78))

    # DIR = GND (A→B direction)
    elements.append(power_sym("GND", ls_x - 15, ls_y - 12.7))
    elements.append(wire(ls_x - 12.7, ls_y - 12.7, ls_x - 15, ls_y - 12.7))

    # OE = GND (always enabled)
    elements.append(power_sym("GND", ls_x - 15, ls_y + 10.16))
    elements.append(wire(ls_x - 12.7, ls_y + 10.16, ls_x - 15, ls_y + 10.16))

    # A-side inputs from RP2040 GPIOs (active-low driven by firmware)
    gpio_labels = [
        ("GPIO2", "A1", -10.16),   # Data 0
        ("GPIO3", "A2", -7.62),    # Data 1
        ("GPIO4", "A3", -5.08),    # Data 2
        ("GPIO5", "A4", -2.54),    # Data 3
        ("GPIO6", "A5", 0),        # Left btn
        ("GPIO7", "A6", 2.54),     # Right btn
    ]
    for gpio_name, a_pin, y_off in gpio_labels:
        elements.append(label(gpio_name, ls_x - 15, ls_y - y_off, 0))
        elements.append(wire(ls_x - 15, ls_y - y_off, ls_x - 12.7, ls_y - y_off))

    # RP2040 GPIO labels (left side of RP2040)
    rp_gpios = [
        ("GPIO2", 17.78),
        ("GPIO3", 15.24),
        ("GPIO4", 12.7),
        ("GPIO5", 10.16),
        ("GPIO6", 7.62),
        ("GPIO7", 5.08),
    ]
    for gpio_name, y_off in rp_gpios:
        elements.append(label(gpio_name, rp_x - 19, rp_y - y_off, 0))
        elements.append(wire(rp_x - 19, rp_y - y_off, rp_x - 16.51, rp_y - y_off))

    # GPIO8 label for strobe
    elements.append(label("GPIO8", rp_x - 19, rp_y - 2.54, 0))
    elements.append(wire(rp_x - 19, rp_y - 2.54, rp_x - 16.51, rp_y - 2.54))

    # GPIO25 for LED
    elements.append(label("GPIO25", rp_x + 19, rp_y, 180))
    elements.append(wire(rp_x + 16.51, rp_y, rp_x + 19, rp_y))

    # Unused A7, A8 — tie to GND
    elements.append(power_sym("GND", ls_x - 15, ls_y + 5.08))
    elements.append(wire(ls_x - 12.7, ls_y + 5.08, ls_x - 15, ls_y + 5.08))
    elements.append(power_sym("GND", ls_x - 15, ls_y + 7.62))
    elements.append(wire(ls_x - 12.7, ls_y + 7.62, ls_x - 15, ls_y + 7.62))

    # No-connect on unused B7, B8
    elements.append(no_connect(ls_x + 12.7, ls_y + 5.08))
    elements.append(no_connect(ls_x + 12.7, ls_y + 7.62))

    # === Section: DB-9 Male Connector (far right) ===
    db_x, db_y = 260, 100
    elements.append(component("DB9_Male", "J2", "DB9_Male_MSX", db_x, db_y))

    # B-side outputs to DB-9 pins
    # B1 → DB-9 pin 1 (Data 0)
    elements.append(wire(ls_x + 12.7, ls_y - 10.16, db_x - 5, ls_y - 10.16))
    elements.append(wire(db_x - 5, ls_y - 10.16, db_x - 5, db_y - 11.43))
    elements.append(wire(db_x - 5, db_y - 11.43, db_x + 7.62, db_y - 11.43))
    elements.append(text_note("Data 0", db_x + 12, db_y - 11.43, 1.0))

    # B2 → DB-9 pin 2 (Data 1)
    elements.append(wire(ls_x + 12.7, ls_y - 7.62, db_x - 7, ls_y - 7.62))
    elements.append(wire(db_x - 7, ls_y - 7.62, db_x - 7, db_y - 8.89))
    elements.append(wire(db_x - 7, db_y - 8.89, db_x + 7.62, db_y - 8.89))
    elements.append(text_note("Data 1", db_x + 12, db_y - 8.89, 1.0))

    # B3 → DB-9 pin 3 (Data 2)
    elements.append(wire(ls_x + 12.7, ls_y - 5.08, db_x - 9, ls_y - 5.08))
    elements.append(wire(db_x - 9, ls_y - 5.08, db_x - 9, db_y - 6.35))
    elements.append(wire(db_x - 9, db_y - 6.35, db_x + 7.62, db_y - 6.35))
    elements.append(text_note("Data 2", db_x + 12, db_y - 6.35, 1.0))

    # B4 → DB-9 pin 4 (Data 3)
    elements.append(wire(ls_x + 12.7, ls_y - 2.54, db_x - 11, ls_y - 2.54))
    elements.append(wire(db_x - 11, ls_y - 2.54, db_x - 11, db_y - 3.81))
    elements.append(wire(db_x - 11, db_y - 3.81, db_x + 7.62, db_y - 3.81))
    elements.append(text_note("Data 3", db_x + 12, db_y - 3.81, 1.0))

    # DB-9 pin 5 (+5V power from MSX) — through Schottky diode
    elements.append(component("D_Schottky", "D1", "BAT54", db_x + 20, db_y - 1.27))
    elements.append(wire(db_x + 7.62, db_y - 1.27, db_x + 20, db_y - 1.27 + 3.81))
    elements.append(power_sym("+5V", db_x + 20, db_y - 1.27 - 3.81, 180))
    elements.append(text_note("+5V from S-760", db_x + 12, db_y - 1.27, 1.0))

    # B5 → DB-9 pin 6 (Left button)
    elements.append(wire(ls_x + 12.7, ls_y, db_x - 13, ls_y))
    elements.append(wire(db_x - 13, ls_y, db_x - 13, db_y + 1.27))
    elements.append(wire(db_x - 13, db_y + 1.27, db_x + 7.62, db_y + 1.27))
    elements.append(text_note("Left btn", db_x + 12, db_y + 1.27, 1.0))

    # B6 → DB-9 pin 7 (Right button)
    elements.append(wire(ls_x + 12.7, ls_y + 2.54, db_x - 15, ls_y + 2.54))
    elements.append(wire(db_x - 15, ls_y + 2.54, db_x - 15, db_y + 3.81))
    elements.append(wire(db_x - 15, db_y + 3.81, db_x + 7.62, db_y + 3.81))
    elements.append(text_note("Right btn", db_x + 12, db_y + 3.81, 1.0))

    # DB-9 pin 8 (Strobe) — voltage divider to GPIO8
    # R3 (2.2kΩ) from pin 8, R4 (3.3kΩ) to GND, junction to GPIO8
    div_x, div_y = db_x + 25, db_y + 15
    elements.append(component("R", "R3", "2.2k", div_x, div_y - 5))
    elements.append(component("R", "R4", "3.3k", div_x, div_y + 5))
    elements.append(wire(db_x + 7.62, db_y + 6.35, div_x, db_y + 6.35))
    elements.append(wire(div_x, db_y + 6.35, div_x, div_y - 5 - 3.81))
    elements.append(wire(div_x, div_y - 5 + 3.81, div_x, div_y + 5 - 3.81))
    elements.append(power_sym("GND", div_x, div_y + 5 + 3.81))
    elements.append(label("GPIO8", div_x + 5, div_y, 180))
    elements.append(wire(div_x, div_y, div_x + 5, div_y))
    elements.append(junction(div_x, div_y))
    elements.append(text_note("Strobe (5V→3V divider)", db_x + 12, db_y + 6.35, 1.0))

    # DB-9 pin 9 (GND)
    elements.append(power_sym("GND", db_x + 12, db_y + 11.43))
    elements.append(wire(db_x + 7.62, db_y + 11.43, db_x + 12, db_y + 11.43))

    # DB-9 pin 10 (mounting/shield) — GND
    elements.append(power_sym("GND", db_x + 12, db_y + 13.97))
    elements.append(wire(db_x + 7.62, db_y + 13.97, db_x + 12, db_y + 13.97))

    # === Section: Power Supply ===
    # XC6206P332MR LDO (5V → 3.3V)
    pwr_x, pwr_y = 130, 35
    elements.append(component("XC6206P332MR", "U4", "XC6206P332MR", pwr_x, pwr_y))

    # LDO input — +5V
    elements.append(power_sym("+5V", pwr_x - 12, pwr_y, 90))
    elements.append(wire(pwr_x - 10.16, pwr_y, pwr_x - 12, pwr_y))

    # LDO output — +3V3
    elements.append(power_sym("+3V3", pwr_x + 12, pwr_y, 270))
    elements.append(wire(pwr_x + 10.16, pwr_y, pwr_x + 12, pwr_y))

    # LDO GND
    elements.append(power_sym("GND", pwr_x, pwr_y + 8.89))

    # Input cap (1µF)
    elements.append(component("C", "C15", "1uF", pwr_x - 18, pwr_y + 8))
    elements.append(power_sym("+5V", pwr_x - 18, pwr_y + 8 - 3.81, 180))
    elements.append(power_sym("GND", pwr_x - 18, pwr_y + 8 + 3.81))

    # Output cap (1µF)
    elements.append(component("C", "C16", "1uF", pwr_x + 18, pwr_y + 8))
    elements.append(power_sym("+3V3", pwr_x + 18, pwr_y + 8 - 3.81, 180))
    elements.append(power_sym("GND", pwr_x + 18, pwr_y + 8 + 3.81))

    # === Section: Status LED ===
    led_x, led_y = 175, 95
    elements.append(component("LED", "D2", "Green", led_x, led_y))
    elements.append(component("R", "R5", "1k", led_x, led_y - 10))
    elements.append(label("GPIO25", led_x, led_y - 10 - 3.81, 90))
    elements.append(power_sym("GND", led_x, led_y + 3.81))
    elements.append(wire(led_x, led_y - 3.81, led_x, led_y - 10 + 3.81))

    # === Section: USB-C Fallback Power Pads (optional) ===
    # Just a note — pads on PCB, no schematic symbol needed
    elements.append(text_note("USB-C 5V pads: optional fallback power (OR-diode to +5V rail)", 20, 180))

    # === Unused RP2040 GPIOs — no-connect ===
    unused_gpios_left = [
        (rp_x - 16.51, rp_y - 22.86),   # GPIO0
        (rp_x - 16.51, rp_y - 20.32),   # GPIO1
        (rp_x - 16.51, rp_y + 0),       # GPIO9
        (rp_x - 16.51, rp_y + 2.54),    # GPIO10
        (rp_x - 16.51, rp_y + 5.08),    # GPIO11
        (rp_x - 16.51, rp_y + 7.62),    # GPIO12
        (rp_x - 16.51, rp_y + 10.16),   # GPIO13
        (rp_x - 16.51, rp_y + 12.7),    # GPIO14
        (rp_x - 16.51, rp_y + 15.24),   # GPIO15
    ]
    for nx, ny in unused_gpios_left:
        elements.append(no_connect(nx, ny))

    unused_gpios_right = [
        (rp_x + 16.51, rp_y - 22.86),   # GPIO16
        (rp_x + 16.51, rp_y - 20.32),   # GPIO17
        (rp_x + 16.51, rp_y - 17.78),   # GPIO18
        (rp_x + 16.51, rp_y - 15.24),   # GPIO19
        (rp_x + 16.51, rp_y - 12.7),    # GPIO20
        (rp_x + 16.51, rp_y - 10.16),   # GPIO21
        (rp_x + 16.51, rp_y - 7.62),    # GPIO22
        (rp_x + 16.51, rp_y - 5.08),    # GPIO23
        (rp_x + 16.51, rp_y - 2.54),    # GPIO24
        # GPIO25 is used for LED
        (rp_x + 16.51, rp_y + 2.54),    # GPIO26
        (rp_x + 16.51, rp_y + 5.08),    # GPIO27
        (rp_x + 16.51, rp_y + 7.62),    # GPIO28
        (rp_x + 16.51, rp_y + 10.16),   # GPIO29
        (rp_x + 16.51, rp_y + 12.7),    # SWCLK
        (rp_x + 16.51, rp_y + 15.24),   # SWD
    ]
    for nx, ny in unused_gpios_right:
        elements.append(no_connect(nx, ny))

    # ─── Assemble the complete schematic ─────────────────────────────────

    # Build lib_symbols section
    lib_symbols = []
    lib_symbols.append(sym_rp2040())
    lib_symbols.append(sym_w25q16())
    lib_symbols.append(sym_74hct245())
    lib_symbols.append(sym_xc6206())
    lib_symbols.append(sym_crystal())
    lib_symbols.append(sym_usb_a())
    lib_symbols.append(sym_db9_male())
    lib_symbols.append(sym_sw_push())
    lib_symbols.append(sym_generic_2pin("C", "C", "C", "Capacitor_SMD:C_0402_1005Metric"))
    lib_symbols.append(sym_generic_2pin("R", "R", "R", "Resistor_SMD:R_0402_1005Metric"))
    lib_symbols.append(sym_generic_2pin("LED", "D", "LED", "LED_SMD:LED_0603_1608Metric"))
    lib_symbols.append(sym_generic_2pin("D_Schottky", "D", "D_Schottky", "Diode_SMD:D_SOD-323"))
    lib_symbols.append(sym_generic_2pin("Polyfuse", "F", "Polyfuse", "Fuse:Fuse_0805_2012Metric"))
    lib_symbols.append(sym_power("+5V"))
    lib_symbols.append(sym_power("+3V3"))
    lib_symbols.append(sym_power("GND"))

    # Final output
    sheet_uuid = "e63e39d7-6ac0-4ffd-8aa3-1841a4541b55"

    output = f'''(kicad_sch
  (version 20231120)
  (generator "usb_msx_gen")
  (generator_version "1.0")
  (uuid "{sheet_uuid}")
  (paper "A3")

  (lib_symbols
{chr(10).join(lib_symbols)}
  )

{chr(10).join(elements)}

  (sheet_instances
    (path "/"
      (page "1")
    )
  )
)
'''
    return output


# ─── Main ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "usb-to-msx-mouse.kicad_sch")

    schematic = generate_schematic()

    with open(output_path, 'w') as f:
        f.write(schematic)

    print(f"Generated: {output_path}")
    print(f"File size: {len(schematic)} bytes")
    print("Open in KiCad 8 to verify and adjust layout.")
