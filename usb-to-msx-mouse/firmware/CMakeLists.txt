# CMakeLists.txt — Build configuration for USB-to-MSX mouse adapter
#
# Requires the Pico SDK. Set PICO_SDK_PATH before running cmake:
#   export PICO_SDK_PATH=/path/to/pico-sdk
#   mkdir build && cd build && cmake .. && make

cmake_minimum_required(VERSION 3.13)

include(pico_sdk_import.cmake)

project(usb-to-msx-mouse C CXX ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

add_executable(usb-to-msx-mouse)

target_sources(usb-to-msx-mouse PUBLIC
    ${CMAKE_CURRENT_LIST_DIR}/src/main.c
    ${CMAKE_CURRENT_LIST_DIR}/src/hid_app.c
    ${CMAKE_CURRENT_LIST_DIR}/src/mouse.c
)

# Include directories: src/ for config.h, include/ for tusb_config.h
target_include_directories(usb-to-msx-mouse PUBLIC
    ${CMAKE_CURRENT_LIST_DIR}/src
    ${CMAKE_CURRENT_LIST_DIR}/include
)

# Link TinyUSB host mode + Pico standard library
target_link_libraries(usb-to-msx-mouse PUBLIC
    pico_stdlib
    tinyusb_host
    tinyusb_board
)

# Generate .uf2 output for drag-and-drop flashing via BOOTSEL
pico_add_extra_outputs(usb-to-msx-mouse)
