/*
 * mouse.c — MSX mouse protocol implementation for the Roland S-760
 *
 * The S-760 uses the standard MSX mouse/trackball protocol on its DB-9
 * joystick port. This module converts accumulated USB HID mouse deltas
 * into the 4-nibble MSX format, driven by strobe interrupts from the S-760.
 *
 * MSX mouse protocol overview:
 *   The host (S-760) toggles the COM/strobe line (DB-9 pin 8) to request
 *   4 nibbles of data per read cycle:
 *     Nibble 0: X delta high nibble (bits 7-4)
 *     Nibble 1: X delta low nibble  (bits 3-0)
 *     Nibble 2: Y delta high nibble (bits 7-4)
 *     Nibble 3: Y delta low nibble  (bits 3-0)
 *   Data is presented on pins 1-4 as active-low signals.
 *   Button state is continuous on pins 6 (left) and 7 (right), active-low.
 *
 * If >300µs elapses between strobes, the state machine resets to nibble 0.
 * This handles incomplete read cycles gracefully.
 *
 * Based on unz-hid-pico by hsshss (MIT license), adapted for custom PCB
 * with 74HCT245 level shifter and RP2040 directly on board.
 */

#include <hardware/gpio.h>
#include "tusb.h"
#include "config.h"

/* Accumulated USB mouse deltas (updated from USB reports, read from IRQ) */
static int mouse_x = 0;
static int mouse_y = 0;

/* Strobe timing for timeout detection */
static uint64_t before_strobe = 0;

/* Latched 16-bit mouse data: [X_hi:X_lo:Y_hi:Y_lo] packed as nibbles */
static uint16_t mouse_data = 0;

/* Current nibble position in the 4-nibble read cycle (0-3) */
static int mouse_data_pos = 0;

/*
 * gpio_put_mouse_button — set button state on TRIG pins.
 * MSX protocol uses active-low: pressed = 0, released = 1.
 * The USB report gives active-high, and the 74HCT245 doesn't invert,
 * so we invert here in software.
 */
static void gpio_put_mouse_button(bool left, bool right) {
    gpio_put(MOUSE_TRIG1_PIN, !left);
    gpio_put(MOUSE_TRIG2_PIN, !right);
}

/*
 * gpio_put_mouse_data — output a 4-bit nibble on the data pins.
 * MSX data lines are active-low, so we invert (~) before output.
 * Uses gpio_put_masked for atomic 4-bit write on contiguous GPIOs.
 */
static void gpio_put_mouse_data(uint8_t data) {
    gpio_put_masked(
        0xf << MOUSE_DATA_PIN_BASE,
        ~((data & 0xf) << MOUSE_DATA_PIN_BASE));
}

/*
 * mouse_irq_callback — GPIO interrupt handler for the strobe line.
 *
 * Called on both rising and falling edges of COM (DB-9 pin 8).
 * Each edge requests the next nibble. If >300µs since last edge
 * (on falling edge), resets to nibble 0 — this is the start of
 * a new read cycle.
 *
 * On nibble 0, the accumulated USB deltas are latched, scaled from
 * the USB mouse's native DPI to the MSX's expected ~200 DPI, and
 * clamped to signed 8-bit range (-128..127).
 */
static void mouse_irq_callback(uint gpio, uint32_t event_mask) {
    uint64_t now = time_us_64();

    /* Timeout detection: if >300µs gap on falling edge, reset to nibble 0 */
    if (event_mask == GPIO_IRQ_EDGE_FALL && (now - before_strobe) >= 300) {
        mouse_data_pos = 0;
    }
    before_strobe = now;

    /* On nibble 0: latch and scale accumulated deltas */
    if (mouse_data_pos == 0) {
        /* Scale from USB DPI to MSX ~200 DPI, invert axes */
        int x = -mouse_x * 200 / MOUSE_DPI;
        int y = -mouse_y * 200 / MOUSE_DPI;

        /* Clamp to signed 8-bit range */
        if (x > 127)  x = 127;
        if (x < -128) x = -128;
        if (y > 127)  y = 127;
        if (y < -128) y = -128;

        /* Pack as 16 bits: [X_byte : Y_byte] */
        mouse_data = ((x & 0xff) << 8) | (y & 0xff);

        /* Reset accumulators */
        mouse_x = 0;
        mouse_y = 0;
    }

    /* Extract the requested nibble (MSB first: positions 3,2,1,0 map to nibbles 0,1,2,3) */
    uint16_t data = (mouse_data >> (3 - mouse_data_pos) * 4) & 0xf;

#if MOUSE_DATA_REVERSE
    /* Bit-reverse the nibble if data lines are wired in reverse order */
    data = ((data & 0x1) << 3) | ((data & 0x2) << 1) |
           ((data & 0x4) >> 1) | ((data & 0x8) >> 3);
#endif

    gpio_put_mouse_data(data);
    mouse_data_pos++;

    /* Wrap around after 4 nibbles */
    if (mouse_data_pos == 4) {
        mouse_data_pos = 0;
    }
}

/*
 * init_mouse — set up GPIO pins for MSX mouse protocol.
 *
 * Configures:
 *   - COM pin as input with pull-up and hysteresis (strobe from S-760)
 *   - 4 data pins as outputs (active-low, idle high via ~0 init)
 *   - 2 button pins as outputs (active-low, idle high = not pressed)
 *   - GPIO interrupt on COM for both edges
 */
void init_mouse(void) {
    /* COM / strobe input — from S-760 via voltage divider */
    gpio_init(MOUSE_COM_PIN);
    gpio_set_dir(MOUSE_COM_PIN, GPIO_IN);
    gpio_pull_up(MOUSE_COM_PIN);
    gpio_set_input_hysteresis_enabled(MOUSE_COM_PIN, true);

    /* 4 data output pins (contiguous from MOUSE_DATA_PIN_BASE) */
    for (int i = 0; i < 4; i++) {
        gpio_init(MOUSE_DATA_PIN_BASE + i);
        gpio_set_dir(MOUSE_DATA_PIN_BASE + i, GPIO_OUT);
    }
    /* Initialize data lines to idle (active-low → output all 1s = 0xF inverted) */
    gpio_put_mouse_data(0);

    /* Left button output — idle high (not pressed) */
    gpio_init(MOUSE_TRIG1_PIN);
    gpio_set_dir(MOUSE_TRIG1_PIN, GPIO_OUT);
    gpio_put(MOUSE_TRIG1_PIN, 1);

    /* Right button output — idle high (not pressed) */
    gpio_init(MOUSE_TRIG2_PIN);
    gpio_set_dir(MOUSE_TRIG2_PIN, GPIO_OUT);
    gpio_put(MOUSE_TRIG2_PIN, 1);

    /* Enable interrupt on both edges of the strobe line */
    gpio_set_irq_enabled_with_callback(
        MOUSE_COM_PIN,
        GPIO_IRQ_EDGE_RISE | GPIO_IRQ_EDGE_FALL,
        true,
        mouse_irq_callback);
}

/*
 * process_mouse_report — accumulate USB HID mouse report data.
 *
 * Called from the TinyUSB callback (hid_app.c) whenever a boot-protocol
 * mouse report arrives. Accumulates X/Y deltas with interrupt safety
 * (disables IRQs briefly to prevent the strobe ISR from reading partial data).
 * Button state is updated immediately (no accumulation needed).
 */
void process_mouse_report(hid_mouse_report_t const *report) {
    /* Update button state immediately — active-low output */
    gpio_put_mouse_button(
        report->buttons & MOUSE_BUTTON_LEFT,
        report->buttons & MOUSE_BUTTON_RIGHT);

    /* Accumulate deltas with interrupt safety */
    uint32_t int_status = save_and_disable_interrupts();
    mouse_x += report->x;
    mouse_y += report->y;
    restore_interrupts(int_status);
}
