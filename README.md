# Roland S-760

## Overview
Documentation for the Roland S-760 sampler.

## Specifications
- Type: Sampler
- Manufacturer: Roland

## Mouse

The S-760 uses a DB-9 mouse port with the **MSX mouse protocol** (nibble-clock based, originally MITSUMI).
The original Roland mouse is the MU-1, which is a rebranded MITSUMI MSX mouse.

**Important:** The MSX DB-9 pinout has **pin 5 = +5V** and **pin 9 = GND**, which is **reversed** compared to Atari/Amiga DB-9 (pin 7 = +5V, pin 8 = GND).
Atari, Amiga, and Commodore mice are **not compatible** — they use different protocols and reversed power pins.

### Compatible adapters

#### MSX PS/2 mouse interface (recommended)

- **Source**: [Gotek Retro](https://www.gotek-retro.eu/msx-ps2-mouse-interface/) or [Tindie (Denjhang)](https://www.tindie.com/products/denjhang/msx-ps2-mouse-converter/)
- **Description**: ATtiny2313-based PS/2 to MSX mouse protocol converter
- **Status**: Confirmed working with S-760
- **Note**: Pressing both mouse buttons simultaneously toggles between mouse and joystick emulation modes, so simultaneous two-button operations don't work
- **Requires**: A native PS/2 mouse, or a USB mouse with genuine PS/2 compatibility mode (not all passive USB-to-PS/2 adapters work)

#### USB-to-MSX mouse adapter

- **Source**: Occasionally available on eBay (search "USB to MSX Mouse Adapter Towns Roland")
- **Description**: Direct USB to MSX mouse protocol converter
- **Status**: Confirmed working with S-760 by users
- **Note**: Small-batch/hobbyist product, stock varies

#### Original MSX mice

Any genuine MSX mouse works (Roland MU-1, Philips MSX mouse, etc.).
Increasingly rare and expensive.

### DIY USB-to-MSX mouse adapter

Two open-source projects exist using a **Raspberry Pi Pico** (RP2040):

#### MsxUsbMouseConverter (recommended)

- **Source**: [Retro-Do-MSX/MsxUsbMouseConverter](https://github.com/Retro-Do-MSX/MsxUsbMouseConverter)
- **Description**: USB mouse to MSX mouse converter using RP2040
- **Hardware**: Raspberry Pi Pico + USB-A female connector + 2x 22-ohm resistors + DB9 cable
- **Advantage**: Operates exclusively in MSX mouse mode (no joystick toggle), so both buttons work simultaneously — unlike the PS/2 adapter above
- **Includes**: 3D-printable case files

#### unz-hid-pico

- **Source**: [hsshss/unz-hid-pico](https://github.com/hsshss/unz-hid-pico)
- **Description**: USB mouse/gamepad to FM TOWNS and MSX protocol converter
- **Hardware**: Raspberry Pi Pico + OTG adapter + DB9 cable + 3.3V-to-5V level shifter
- **Schematic**: [OSHWLab](https://oshwlab.com/hsshss/unz-hid-pico)

#### Why not other microcontrollers?

- **ESP32 (original)**: No native USB host — software USB host exists but is unreliable
- **ESP32-S2/S3**: Has USB host but no existing MSX mouse project — would need custom firmware from scratch
- **Arduino Duemilanove**: No USB host — requires a USB Host Shield (MAX3421E) add-on board
- **Raspberry Pi Zero 2 W**: Linux is not real-time enough for the MSX protocol timing (0.18 ms clock response), and GPIO is 3.3V (MSX expects 5V)

### mouSTer USB mouse adapter (not compatible)

- **Source**: [C64 OS Store](https://c64os.com/store/)
- **Status**: **Not compatible** — does not support MSX protocol (only Atari ST, Amiga, and C64 modes)
- **Note**: Previously recommended by Claude in error, purchased based on that recommendation, and confirmed not to work with the S-760. The mouSTer lacks MSX protocol support entirely.

## Video Output

The S-760 (with OP-760-1 expansion) has a digital RGB video output via an 8-pin DIN connector.

### OP-760-1 video signal specifications

- **Signal type**: TTL digital RGB (RGBS — 1 bit per channel, 8 colours max)
- **Resolution**: 640x200 (CGA-class)
- **Horizontal sync**: ~15.7 kHz
- **Vertical sync**: ~60 Hz
- **Sync type**: Separate H-Sync and V-Sync
- **Connector**: 8-pin DIN (EIAJ)

#### DIN-8 pinout

| Pin | Signal |
| --- | --- |
| 1 | +5V (do not connect to RGBtoHDMI) |
| 2 | GND |
| 3 | No connection |
| 4 | H-Sync |
| 5 | V-Sync |
| 6 | Red |
| 7 | Green |
| 8 | Blue |

**Note:** Some sources (e.g. S-550 manual) list a different pin assignment.
Verify against your hardware or use a known-good pre-made cable.

#### References

- [llamamusic.com DIY page](https://llamamusic.com/s50s550/DIY_page.html) — S-50/S-550/S-760 video output details and DIN-8 pinout
- [llamamusic.com RGB-25N cable DIY](https://llamamusic.com/s50s550/Roland_RGB-25N_Monitor_Cable_DIY.html) — cable wiring guide
- [Jim Atwood — S-760 with OP-760-1](https://jimatwood.wordpress.com/2012/02/01/roland-s-760-sampler-with-op-760-1-video-output-and-mu-1-mouse/) — working setup photos
- [s760.free.fr monitors page](http://s760.free.fr/monitor.htm) — compatible monitor list

### RGBtoHDMI

- **Source**: [hoglet67/RGBtoHDMI](https://github.com/hoglet67/RGBtoHDMI)
- **Description**: Converts retro computer RGB/YUV video signals to HDMI
- **Hardware**: Raspberry Pi Zero + custom hat with CPLD
- **License**: GPL-3.0

#### Profile selection

Use **6-12_BIT_RGB > IBM PC Compatible > CGA**.
The S-760's video output matches CGA timing and signal characteristics (TTL RGB, 15.7 kHz, 200 lines, separate H/V sync).

#### Fullscreen output

By default RGBtoHDMI may show the image in a small window with black borders.
To get fullscreen output, use the on-screen menu (active button on the hat):

1. Press **Menu** button on the RGBtoHDMI hat
2. Navigate to **Scaling** settings
3. Set scaling to **Fill** or **Integer** (integer gives pixel-perfect scaling without stretching)
4. Adjust **overscan** values if there are still black borders

You can also try different **Resolution** options in the menu — some HDMI displays respond better to specific output resolutions (e.g. 1080p vs 720p).

#### Raspberry Pi setup

The RGBtoHDMI runs bare-metal firmware on a Raspberry Pi Zero (no OS needed).

1. **Download** the latest release zip from [hoglet67/RGBtoHDMI releases](https://github.com/hoglet67/RGBtoHDMI/releases)
2. **Format** a micro SD card as FAT32
3. **Extract** the zip to the root of the SD card (files should be in the root directory, not in a subfolder)
4. **Safely eject** the SD card from the PC
5. **Insert** the SD card into the Pi Zero

- **Recommended Pi**: Raspberry Pi Zero (non-W) — the WiFi radio on the W models can cause visual artifacts
- **If using a Pi Zero W**: disable radios by adding `dtoverlay=disable-wifi` and `dtoverlay=disable-bt` to `config.txt` on the SD card
- **Avoid Pi Zero 2 W**: different GPIO timing causes compatibility issues
- **Upgrading**: wipe the SD card first, do not overwrite an existing install — old saved profiles are not guaranteed to be compatible

## SCSI Storage

The S-760 uses SCSI for external storage. A ZuluSCSI Pico Slim replaces physical SCSI drives with SD card-based disk images.

### ZuluSCSI Pico Slim

- **Source**: [SamplerZone](https://samplerzone.com/products/zuluscsi-pico-slim)
- **Description**: Ultra-compact SCSI SD card emulator with DB25 connector
- **Hardware**: Raspberry Pi Pico W in a mini plug-in case
- **Included**: Pre-configured 64GB SD card
- **Features**:
  - Supports up to 7 SCSI IDs (multiple drives simultaneously)
  - Plug-and-play via DB25 SCSI port
  - Standard SD card with disk image files
  - Compatible with Roland, Akai, Ensoniq, Emu, Kurzweil, Korg, Yamaha samplers

## Sound Loading

Chicken Systems Translator is used to convert and load sounds onto the ZuluSCSI disk images for use on the S-760.

### Chicken Systems Translator 7

- **Source**: [Chicken Systems](https://www.chickensys.com/products2/translator/index.html)
- **Description**: Professional sample library conversion software
- **Platforms**: Mac OS X, Windows
- **Features**:
  - Converts between 50+ sampler and DAW formats including Roland, Akai, Emu, Kontakt, EXS24, SFZ, GigaStudio
  - Translates wavedata, keymaps, and effects parameters
  - Built-in Instrument Player for auditioning sounds before conversion
  - Reference Manager for repairing broken sample links
  - AutoSampler for recording internal and external equipment

