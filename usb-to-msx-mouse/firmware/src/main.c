/*
 * main.c — Entry point for USB-to-MSX mouse adapter
 *
 * Initializes the board, sets up the HID host application,
 * and runs the TinyUSB task loop forever. The actual mouse
 * protocol logic lives in mouse.c, driven by GPIO interrupts.
 */

#include "bsp/board.h"
#include "tusb.h"
#include "config.h"
#include <hardware/gpio.h>

/* Defined in hid_app.c */
void hid_app_init(void);

int main(void) {
    /* Standard Pico SDK board init (clocks, stdio, etc.) */
    board_init();

    /* Set up status LED */
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    gpio_put(LED_PIN, 0);

    /* Initialize mouse GPIO and USB HID host callbacks */
    hid_app_init();

    /* Start TinyUSB in host mode on the native USB port */
    tuh_init(BOARD_TUH_RHPORT);

    /* Main loop — TinyUSB processes USB events and dispatches HID reports */
    while (1) {
        tuh_task();
    }

    return 0;
}
