# USB-to-MSX mouse adapter pinout

## RP2040 GPIO to DB-9 pin mapping

All output signals pass through a 74HCT245 level shifter (3.3V → 5V).
The strobe input uses a resistor voltage divider (5V → ~3.0V).

| RP2040 GPIO | 74HCT245 channel | DB-9 pin | Signal | Direction |
| --- | --- | --- | --- | --- |
| GPIO 2 | A1 → B1 | Pin 1 | Data bit 0 | Output |
| GPIO 3 | A2 → B2 | Pin 2 | Data bit 1 | Output |
| GPIO 4 | A3 → B3 | Pin 3 | Data bit 2 | Output |
| GPIO 5 | A4 → B4 | Pin 4 | Data bit 3 | Output |
| GPIO 6 | A5 → B5 | Pin 6 | Left button (TRIG1) | Output |
| GPIO 7 | A6 → B6 | Pin 7 | Right button (TRIG2) | Output |
| GPIO 8 | N/A (divider) | Pin 8 | Strobe / COM | Input |
| GPIO 25 | N/A | N/A | Status LED | Output |

## DB-9 connector pinout (male, from front)

```
  1 2 3 4 5
   6 7 8 9
```

| DB-9 pin | MSX signal | Connection |
| --- | --- | --- |
| 1 | Forward / Data 0 | 74HCT245 B1 |
| 2 | Back / Data 1 | 74HCT245 B2 |
| 3 | Left / Data 2 | 74HCT245 B3 |
| 4 | Right / Data 3 | 74HCT245 B4 |
| 5 | +5V | Power rail (via Schottky diode) |
| 6 | Trigger 1 (left btn) | 74HCT245 B5 |
| 7 | Trigger 2 (right btn) | 74HCT245 B6 |
| 8 | Strobe / COM | Voltage divider → GPIO 8 |
| 9 | GND | Ground |

## Voltage divider (strobe input)

```
DB-9 Pin 8 (5V strobe) ──── 2.2kΩ ──┬── GPIO 8 (3.3V tolerant input)
                                      │
                                    3.3kΩ
                                      │
                                     GND
```

Output voltage: `5V × 3.3kΩ / (2.2kΩ + 3.3kΩ) = ~3.0V`

## 74HCT245 connections

| Pin | Signal | Connection |
| --- | --- | --- |
| 1 | DIR | GND (A → B direction) |
| 2-7 | A1-A6 | GPIO 2-7 (3.3V inputs) |
| 8-9 | A7-A8 | N/A (unused, tie to GND) |
| 10 | GND | Ground |
| 11-12 | B8-B7 | N/A (unused) |
| 13-18 | B6-B1 | DB-9 pins 7,6,4,3,2,1 |
| 19 | OE (active low) | GND (always enabled) |
| 20 | VCC | +5V rail |

## USB-A connector

| Pin | Signal | Connection |
| --- | --- | --- |
| 1 | VBUS (+5V) | 5V rail via 500mA polyfuse |
| 2 | D- | 27Ω → RP2040 USB D- |
| 3 | D+ | 27Ω → RP2040 USB D+ |
| 4 | GND | Ground |

## Power rail

```
MSX DB-9 Pin 5 (+5V) ── Schottky diode ──┬── 5V rail
                                          │
USB-C pads (optional)  ── Schottky diode ──┘
                                          │
                                    XC6206 LDO → 3.3V rail → RP2040 + flash
                                          │
                                    Polyfuse → USB-A VBUS (to power mouse)
```
