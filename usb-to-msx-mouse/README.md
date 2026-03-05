# USB-to-MSX mouse adapter for Roland S-760

Open-source hardware adapter that lets you use a standard USB mouse (like the Logitech Trackman Marble) with the Roland S-760 sampler.

The S-760 uses the MSX mouse protocol on a DB-9 joystick port.
Original Roland MU-1 mice are rare and expensive.
This adapter is a custom PCB with an RP2040 microcontroller that translates USB HID mouse reports into MSX nibble protocol in real time.

## Features

- **Plug and forget** — no drivers, no configuration
- **USB-A input** — works with any standard USB mouse (boot protocol)
- **DB-9 output** — connects to the S-760's mouse port via standard serial cable
- **Custom PCB** — RP2040 directly on board (not a Pico module), ~20×40mm
- **JLCPCB-ready** — full production files included (Gerbers, BOM, CPL)
- **Under $16 NZD per unit** (in batches of 5)

## How it works

```
USB Mouse → [USB-A] → RP2040 (TinyUSB host) → 74HCT245 → [DB-9] → S-760
              ↑                                    ↑
           USB HID                           3.3V → 5V
         boot protocol                     level shifting
```

1. The RP2040 runs TinyUSB in USB host mode, receiving HID boot-protocol mouse reports
1. Mouse X/Y deltas accumulate between read cycles, scaled from USB DPI to MSX ~200 DPI
1. When the S-760 toggles the strobe line (DB-9 pin 8), a GPIO interrupt handler serves 4 nibbles of position data
1. Button state is output continuously on DB-9 pins 6 and 7
1. A 74HCT245 level shifter converts all outputs from 3.3V to 5V MSX levels

## Project structure

```
usb-to-msx-mouse/
├── firmware/           Pico SDK C project (TinyUSB host + MSX protocol)
│   ├── CMakeLists.txt
│   ├── src/            main.c, hid_app.c, mouse.c, config.h
│   └── include/        tusb_config.h
├── hardware/
│   ├── kicad/          KiCad 8 schematic and PCB layout
│   ├── bom.csv         Bill of materials with JLCPCB part numbers
│   ├── gerbers/        Production Gerber files
│   └── jlcpcb/         JLCPCB assembly files (BOM + CPL)
├── case/               3D printable snap-fit enclosure (STEP + STL)
├── docs/
│   ├── pinout.md       GPIO to DB-9 pin mapping
│   └── build-guide.md  Order, flash, assemble, test
├── LICENSE             MIT
└── README.md
```

## Quick start

### Build firmware

```bash
export PICO_SDK_PATH=/path/to/pico-sdk
cd firmware
mkdir build && cd build
cmake ..
make -j$(nproc)
```

### Flash

1. Hold BOOTSEL button on the PCB
1. Connect USB-A to USB-A cable between computer and adapter
1. Release BOOTSEL — adapter appears as `RPI-RP2` drive
1. Copy `build/usb-to-msx-mouse.uf2` to the drive

### Connect

1. DB-9 cable from adapter to S-760 mouse port
1. Plug USB mouse into adapter's USB-A port
1. Green LED lights up when mouse is recognized
1. Power on S-760 — cursor should work

See [docs/build-guide.md](docs/build-guide.md) for full step-by-step instructions.

## Configuration

Edit `firmware/src/config.h` to adjust:

- **`MOUSE_DPI`** — match your mouse's native DPI (300 for Trackman Marble, 800 for typical optical)
- **`MOUSE_DATA_REVERSE`** — set to 1 if data lines are wired in reverse order
- **Pin assignments** — if modifying the PCB layout

## Hardware specifications

- **MCU**: RP2040 (QFN-56, dual-core Cortex-M0+, 133 MHz)
- **Flash**: W25Q16JVSNIQ (2MB QSPI)
- **Level shifter**: 74HCT245 (SOIC-20)
- **Power**: 5V from MSX DB-9 pin 5 (USB-C fallback pads on PCB)
- **Board size**: ~20×40mm, 2-layer
- **Connectors**: USB-A female (TH), DB-9 male (TH) — hand-soldered

## Cost breakdown (5 units)

| Item | Cost (NZD) |
| --- | --- |
| PCB fabrication (5x) | $4 |
| SMT assembly + components | $40 |
| 3D printed cases (5x) | $15 |
| Shipping to NZ | $12 |
| Through-hole connectors | $8 |
| **Total (5 units)** | **~$79** |
| **Per unit** | **~$16** |

## Credits

Firmware based on [unz-hid-pico](https://github.com/hsshss/unz-hid-pico) by hsshss (MIT license).

## References

- [MSX Mouse/Trackball protocol](https://www.msx.org/wiki/Mouse/Trackball)
- [RP2040 hardware design guide](https://datasheets.raspberrypi.com/rp2040/hardware-design-with-rp2040.pdf)
- [TinyUSB documentation](https://docs.tinyusb.org/)

## License

[MIT](LICENSE)
