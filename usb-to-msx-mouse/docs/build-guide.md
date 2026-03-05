# Build guide

Step-by-step instructions to order, assemble, flash, and test the USB-to-MSX mouse adapter for the Roland S-760.

## Prerequisites

- JLCPCB account (for PCB fabrication and SMT assembly)
- Soldering iron (for 2 through-hole connectors)
- USB-A to USB-A cable (for firmware flashing)
- Logitech Trackman Marble (or any standard USB mouse)
- Roland S-760 with DB-9 serial cable

## Step 1: Order PCBs from JLCPCB

1. Go to [jlcpcb.com](https://jlcpcb.com) and upload the Gerber ZIP from `hardware/gerbers/`
1. Select these options:
    - **Layers**: 2
    - **PCB thickness**: 1.6mm
    - **Surface finish**: HASL (lead-free)
    - **Qty**: 5 (minimum order)
1. Enable **SMT Assembly** (economic, top side only)
1. Upload the BOM and CPL files from `hardware/jlcpcb/`
1. Review component placements — JLCPCB will flag any out-of-stock parts
1. Add the order to cart

### Optional: 3D printed case

Add a 3D printing order from `case/` STL files using JLC3DP (ships with the PCB order).

## Step 2: Hand-solder through-hole connectors

JLCPCB assembles all SMT components, but the USB-A female socket and DB-9 male connector are through-hole — solder these yourself:

1. **USB-A female socket** — insert from the top, solder pins on the bottom.
   Large pads, easy to solder.
1. **DB-9 male connector** — insert from the top, solder pins on the bottom.
   The mounting tabs provide mechanical strength.

Both connectors have large through-hole pads — no fine-pitch work required.

## Step 3: Flash firmware

### First-time flashing (BOOTSEL mode)

1. Hold the **BOOTSEL** button on the PCB
1. Connect a **USB-A to USB-A cable** between a computer and the adapter's USB-A port
1. Release the BOOTSEL button — the adapter appears as a USB mass storage device (`RPI-RP2`)
1. Copy `firmware/build/usb-to-msx-mouse.uf2` to the `RPI-RP2` drive
1. The adapter reboots automatically with the new firmware

### Building firmware from source

```bash
# Clone the Pico SDK (if not already installed)
git clone https://github.com/raspberrypi/pico-sdk.git
cd pico-sdk && git submodule update --init && cd ..
export PICO_SDK_PATH=$(pwd)/pico-sdk

# Build the firmware
cd firmware
mkdir build && cd build
cmake ..
make -j$(nproc)

# Output: usb-to-msx-mouse.uf2
```

## Step 4: Connect and test

1. Connect the adapter's **DB-9 port** to the Roland S-760's mouse port using a straight-through DB-9 serial cable
1. Plug the **Logitech Trackman Marble** (or any USB mouse) into the adapter's USB-A port
1. The **green LED** should light up when the mouse is recognized
1. Power on the S-760 — the cursor should respond to trackball movement
1. Test both left and right mouse buttons

### Troubleshooting

- **LED doesn't light up**: Check that the DB-9 cable is providing 5V power (pin 5).
  If the S-760's port doesn't supply enough power, use the USB-C fallback pads on the PCB.
- **No cursor movement**: Verify the DB-9 cable is straight-through (not null-modem/crossover).
  Check that the cable is connected to the S-760's mouse port (not MIDI or RS-232).
- **Cursor moves wrong direction**: The axis inversion may need adjustment.
  Edit `MOUSE_DPI` in `firmware/src/config.h` and rebuild.
- **Cursor too fast/slow**: Adjust `MOUSE_DPI` to match your mouse's actual DPI.
  Trackman Marble = 300, typical optical mouse = 800.

## Step 5: Assemble case (optional)

1. Print `case/case-top.stl` and `case/case-bottom.stl` (PLA, 0.2mm layer height)
1. Place the PCB in the bottom half
1. Snap the top half on — designed for snap-fit, no screws needed
1. Both USB-A and DB-9 connectors should be accessible through the case openings
