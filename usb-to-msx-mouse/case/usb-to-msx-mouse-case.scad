/*
 * usb-to-msx-mouse-case.scad — Parametric snap-fit case for USB-to-MSX mouse adapter
 *
 * Two-piece design: bottom (tray) + top (lid) with snap-fit clips.
 * USB-A connector on one short edge, DB-9 on the other.
 *
 * To render:
 *   openscad -o case-bottom.stl -D 'part="bottom"' usb-to-msx-mouse-case.scad
 *   openscad -o case-top.stl -D 'part="top"' usb-to-msx-mouse-case.scad
 *
 * Print settings: PLA, 0.2mm layer height, no supports needed.
 */

/* ── Configuration ────────────────────────────────────────────────── */

// Which part to render: "bottom", "top", or "both" (exploded view)
part = "both";

// PCB dimensions (mm)
pcb_length = 52;      // X axis (USB-A to DB-9)
pcb_width  = 22;      // Y axis
pcb_thick  = 1.6;     // Board thickness

// Case wall parameters
wall = 1.5;           // Wall thickness
gap = 0.3;            // Clearance between PCB and case walls
bottom_thick = 1.5;   // Bottom floor thickness
top_thick = 1.2;      // Top ceiling thickness

// Total interior dimensions
int_length = pcb_length + 2 * gap;
int_width  = pcb_width + 2 * gap;
int_height = 12;      // Interior height (accommodates components + connectors)

// PCB sits on ledges inside the case
pcb_ledge = 0.8;      // Width of support ledge
pcb_z = 3;            // Height of PCB bottom above case floor (clearance for bottom components)

// Connector cutout dimensions
// USB-A female: ~13mm wide x 6mm tall (generous cutout)
usb_width  = 14;
usb_height = 7.5;
usb_z_off  = pcb_z + pcb_thick - 1;  // Bottom of USB cutout

// DB-9 male: ~31mm wide x 12mm tall (includes mounting hardware)
db9_width  = 33;
db9_height = 11;
db9_z_off  = pcb_z - 2;  // DB-9 extends below PCB

// Snap-fit clip dimensions
clip_width = 3;
clip_depth = 0.8;     // How far clip protrudes
clip_height = 2;

// Split height: where bottom ends and top begins
split_z = pcb_z + pcb_thick + 3;  // Just above tallest SMD component

// Outer dimensions (derived)
ext_length = int_length + 2 * wall;
ext_width  = int_width + 2 * wall;
ext_height = int_height + bottom_thick + top_thick;

// Corner rounding
corner_r = 2;

/* ── Modules ──────────────────────────────────────────────────────── */

// Rounded box (hollow)
module rounded_box(l, w, h, r, wall_t) {
    difference() {
        // Outer shell
        hull() {
            for (x = [r, l - r])
                for (y = [r, w - r])
                    translate([x, y, 0])
                        cylinder(h = h, r = r, $fn = 32);
        }
        // Inner cavity
        translate([wall_t, wall_t, wall_t])
            hull() {
                for (x = [r, l - 2 * wall_t - r])
                    for (y = [r, w - 2 * wall_t - r])
                        translate([x, y, 0])
                            cylinder(h = h, r = max(r - wall_t, 0.5), $fn = 32);
            }
    }
}

// PCB support ledges (run along long edges)
module pcb_ledges() {
    // Left ledge
    translate([wall + gap, wall, bottom_thick + pcb_z - pcb_ledge])
        cube([int_length, pcb_ledge, pcb_ledge]);
    // Right ledge
    translate([wall + gap, wall + int_width - pcb_ledge, bottom_thick + pcb_z - pcb_ledge])
        cube([int_length, pcb_ledge, pcb_ledge]);
}

// USB-A cutout (on -X face)
module usb_cutout() {
    translate([-1, (ext_width - usb_width) / 2, bottom_thick + usb_z_off])
        cube([wall + 2, usb_width, usb_height]);
}

// DB-9 cutout (on +X face)
module db9_cutout() {
    translate([ext_length - wall - 1, (ext_width - db9_width) / 2, bottom_thick + db9_z_off])
        cube([wall + 2, db9_width, db9_height]);
}

// Snap-fit clips on bottom half (protrude outward from inner wall)
module snap_clips_bottom() {
    // Two clips per long side
    for (x_pos = [ext_length * 0.3, ext_length * 0.7]) {
        // Left side
        translate([x_pos - clip_width / 2, wall - 0.1, bottom_thick + split_z - clip_height])
            difference() {
                cube([clip_width, clip_depth + 0.1, clip_height]);
                translate([0, clip_depth, clip_height])
                    rotate([0, 90, 0])
                        cylinder(h = clip_width, r = clip_depth, $fn = 16);
            }
        // Right side
        translate([x_pos - clip_width / 2, ext_width - wall - clip_depth, bottom_thick + split_z - clip_height])
            difference() {
                cube([clip_width, clip_depth + 0.1, clip_height]);
                translate([0, 0, clip_height])
                    rotate([0, 90, 0])
                        cylinder(h = clip_width, r = clip_depth, $fn = 16);
            }
    }
}

// Snap-fit slots in top half (recesses to receive clips)
module snap_slots_top() {
    slot_extra = 0.2;  // Extra clearance for snap fit
    for (x_pos = [ext_length * 0.3, ext_length * 0.7]) {
        // Left side
        translate([x_pos - clip_width / 2 - slot_extra, wall - clip_depth - slot_extra - 0.1, -0.1])
            cube([clip_width + 2 * slot_extra, clip_depth + slot_extra + 0.2, clip_height + 0.2]);
        // Right side
        translate([x_pos - clip_width / 2 - slot_extra, ext_width - wall - 0.1, -0.1])
            cube([clip_width + 2 * slot_extra, clip_depth + slot_extra + 0.2, clip_height + 0.2]);
    }
}

// BOOTSEL button access hole (small hole in top, aligned with switch location)
// Switch is approximately at PCB center-left
module bootsel_hole() {
    translate([wall + gap + 12, ext_width / 2, -0.1])
        cylinder(d = 3, h = top_thick + 0.2, $fn = 24);
}

// LED light pipe (small hole in top, aligned with LED)
module led_hole() {
    translate([wall + gap + 24, ext_width / 2 - 3, -0.1])
        cylinder(d = 2, h = top_thick + 0.2, $fn = 24);
}

/* ── Parts ────────────────────────────────────────────────────────── */

module bottom_half() {
    bottom_h = bottom_thick + split_z;

    difference() {
        union() {
            // Main shell (cut at split height)
            intersection() {
                rounded_box(ext_length, ext_width, ext_height, corner_r, wall);
                cube([ext_length + 1, ext_width + 1, bottom_h]);
            }
            // PCB ledges
            pcb_ledges();
            // Snap clips
            snap_clips_bottom();
        }
        // Connector cutouts
        usb_cutout();
        db9_cutout();
    }
}

module top_half() {
    top_h = ext_height - bottom_thick - split_z;

    difference() {
        // Main shell (upper portion)
        translate([0, 0, 0])
            intersection() {
                // Shift the full shell down so we get the top portion
                translate([0, 0, -(bottom_thick + split_z)])
                    rounded_box(ext_length, ext_width, ext_height, corner_r, wall);
                cube([ext_length + 1, ext_width + 1, top_h + top_thick]);
            }
        // Connector cutouts (shifted to match)
        translate([0, 0, -(bottom_thick + split_z)]) {
            usb_cutout();
            db9_cutout();
        }
        // Snap slots
        snap_slots_top();
        // BOOTSEL access hole
        translate([0, 0, top_h + top_thick - top_thick])
            bootsel_hole();
        // LED hole
        translate([0, 0, top_h + top_thick - top_thick])
            led_hole();
    }
}

/* ── Render ───────────────────────────────────────────────────────── */

if (part == "bottom") {
    bottom_half();
} else if (part == "top") {
    // Flip top half upside down for printing
    translate([0, ext_width, ext_height - bottom_thick - split_z])
        rotate([180, 0, 0])
            top_half();
} else if (part == "both") {
    // Exploded view: bottom in place, top offset above
    color("DodgerBlue", 0.8)
        bottom_half();
    color("LightSteelBlue", 0.6)
        translate([0, 0, bottom_thick + split_z + 10])  // 10mm gap for visibility
            top_half();
} else {
    echo("Set part to \"bottom\", \"top\", or \"both\"");
}
