/*
 * config.h — Pin assignments and configuration for USB-to-MSX mouse adapter
 *
 * This maps RP2040 GPIO pins to the MSX mouse protocol signals,
 * routed through a 74HCT245 level shifter to the DB-9 connector.
 *
 * Pin assignments match the custom PCB layout (not a Pico module).
 */

#ifndef CONFIG_H
#define CONFIG_H

/* Feature flags — mouse only, no gamepad needed */
#define MOUSE_ENABLED         1
#define GAMEPAD_ENABLED       0

/*
 * Trackman Marble is 300 DPI (400 DPI in some models).
 * MSX protocol expects ~200 DPI, so the firmware scales:
 *   msx_delta = -usb_delta * 200 / MOUSE_DPI
 * Set this to match your USB mouse. Common values: 300, 400, 800.
 */
#define MOUSE_DPI             300

/*
 * Bit reversal for data nibbles.
 * Set to 0 — our PCB routes data lines in standard order
 * (GPIO 2 = bit 0, GPIO 3 = bit 1, etc.) so no reversal needed.
 */
#define MOUSE_DATA_REVERSE    0

/*
 * GPIO pin assignments — matched to PCB schematic.
 * Data pins MUST be contiguous (uses gpio_put_masked with 4-bit window).
 *
 * RP2040 GPIO → 74HCT245 → DB-9 pin
 * ─────────────────────────────────────
 * GPIO 2  → 245 A1→B1 → Pin 1 (Data 0)
 * GPIO 3  → 245 A2→B2 → Pin 2 (Data 1)
 * GPIO 4  → 245 A3→B3 → Pin 3 (Data 2)
 * GPIO 5  → 245 A4→B4 → Pin 4 (Data 3)
 * GPIO 6  → 245 A5→B5 → Pin 6 (Left button)
 * GPIO 7  → 245 A6→B6 → Pin 7 (Right button)
 * GPIO 8  ← voltage divider ← Pin 8 (Strobe from S-760)
 */
#define MOUSE_DATA_PIN_BASE   2     /* GPIO 2-5 = 4 data lines */
#define MOUSE_TRIG1_PIN       6     /* Left button → DB-9 pin 6 */
#define MOUSE_TRIG2_PIN       7     /* Right button → DB-9 pin 7 */
#define MOUSE_COM_PIN         8     /* Strobe input from S-760 (via voltage divider) */

/* Status LED on GPIO 25 — active high */
#define LED_PIN               25

#endif /* CONFIG_H */
