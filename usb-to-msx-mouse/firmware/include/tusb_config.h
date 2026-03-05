/*
 * tusb_config.h — TinyUSB configuration for USB Host mode
 *
 * Configures TinyUSB as a USB Host to receive HID reports from a
 * standard USB mouse (boot protocol). Uses the RP2040's native
 * USB hardware (not PIO-based USB).
 */

#ifndef TUSB_CONFIG_H
#define TUSB_CONFIG_H

/* Use native USB hardware in host mode */
#define CFG_TUH_ENABLED               1
#define CFG_TUH_RPI_PIO_USB           0       /* 0 = hardware USB, not PIO */
#define BOARD_TUH_RHPORT              CFG_TUH_RPI_PIO_USB
#define BOARD_TUH_MAX_SPEED           OPT_MODE_DEFAULT_SPEED

/* HID host — support up to 4 interfaces (for hub scenarios) */
#define CFG_TUH_HUB                   1       /* Allow USB hubs */
#define CFG_TUH_CDC                   0
#define CFG_TUH_HID                   4
#define CFG_TUH_MSC                   0
#define CFG_TUH_VENDOR                0

/* Max devices — with hub support, allow a few */
#define CFG_TUH_DEVICE_MAX            4

/* Buffer sizes for HID endpoint data */
#define CFG_TUH_HID_EPIN_BUFSIZE      64
#define CFG_TUH_HID_EPOUT_BUFSIZE     64

/* Enumeration buffer for parsing descriptors */
#define CFG_TUH_ENUMERATION_BUFSIZE   256

#endif /* TUSB_CONFIG_H */
