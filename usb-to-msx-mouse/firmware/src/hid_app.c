/*
 * hid_app.c — USB HID host application layer
 *
 * Implements TinyUSB host HID callbacks. When a USB mouse is plugged in,
 * TinyUSB calls tuh_hid_mount_cb(). We immediately request HID reports.
 * When reports arrive, we dispatch boot-protocol mouse reports to
 * process_mouse_report() in mouse.c.
 *
 * Based on unz-hid-pico by hsshss (MIT license).
 */

#include "tusb.h"
#include "config.h"
#include <hardware/gpio.h>

/* Defined in mouse.c */
void init_mouse(void);
void process_mouse_report(hid_mouse_report_t const *report);

/*
 * hid_app_init — called once from main() to set up mouse GPIO pins.
 */
void hid_app_init(void) {
#if MOUSE_ENABLED
    init_mouse();
#endif
}

/*
 * tuh_hid_mount_cb — called by TinyUSB when a HID device is connected.
 * We request the first report immediately to start the data flow.
 * Also turns on the status LED to indicate a device is connected.
 */
void tuh_hid_mount_cb(uint8_t dev_addr, uint8_t instance,
                       uint8_t const *desc_report, uint16_t desc_len) {
    (void)desc_report;
    (void)desc_len;

    /* LED on — device connected */
    gpio_put(LED_PIN, 1);

    /* Start receiving HID reports */
    tuh_hid_receive_report(dev_addr, instance);
}

/*
 * tuh_hid_umount_cb — called when a HID device is disconnected.
 * Turn off the LED.
 */
void tuh_hid_umount_cb(uint8_t dev_addr, uint8_t instance) {
    (void)dev_addr;
    (void)instance;

    /* LED off — device disconnected */
    gpio_put(LED_PIN, 0);
}

/*
 * tuh_hid_report_received_cb — called when a HID report arrives.
 * Dispatches boot-protocol mouse reports to the MSX protocol handler.
 * Immediately requests the next report to keep the data flowing.
 */
void tuh_hid_report_received_cb(uint8_t dev_addr, uint8_t instance,
                                 uint8_t const *report, uint16_t len) {
    (void)len;

    uint8_t const itf_protocol = tuh_hid_interface_protocol(dev_addr, instance);

    switch (itf_protocol) {
        case HID_ITF_PROTOCOL_MOUSE:
#if MOUSE_ENABLED
            process_mouse_report((hid_mouse_report_t const *)report);
#endif
            break;

        default:
            /* Ignore non-mouse devices (keyboards, gamepads, etc.) */
            break;
    }

    /* Request next report */
    tuh_hid_receive_report(dev_addr, instance);
}
