# Roland S-760

## Overview
Documentation for the Roland S-760 sampler.

## Specifications
- Type: Sampler
- Manufacturer: Roland

## Mouse

The S-760 uses a DB-9 mouse port. To use a standard USB mouse, a mouSTer adapter board is used.

### mouSTer USB Mouse Adapter

- **Source**: [C64 OS Store](https://c64os.com/store/)
- **Description**: Multi-mode universal USB input adapter
- **Compatibility**: Atari, Commodore 8-bit, Amiga, Spectrum, and other retro systems with DB-9 mouse/joystick ports
- **Features**:
  - Supports standard USB mice including wireless models with dongles
  - Scroll wheel support
  - Highly configurable for different systems and input modes
  - 3D printed black enclosure

## Video Output

The S-760 (with OP-760-1 expansion) has a digital RGB video output. To convert this to HDMI for use with modern monitors, an RGBtoHDMI adapter is used.

### RGBtoHDMI

- **Source**: [hoglet67/RGBtoHDMI](https://github.com/hoglet67/RGBtoHDMI) (pre-made kit)
- **Description**: Converts retro computer RGB/YUV video signals to HDMI
- **Hardware**: Raspberry Pi Zero + custom hat with CPLD
- **Features**:
  - Pixel-perfect video sampling and conversion
  - Supports RGB and YUV signals at various bit depths (6-bit, 8-bit, 12-bit)
  - Multiple adapter configurations for different vintage systems
  - Bare-metal firmware for accurate timing
- **License**: GPL-3.0

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

