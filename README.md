# Sonar‑Controlled DC Motor System

A two-part embedded project that uses an ESP32, an ultrasonic proximity sensor (HC‑SR04), and an L293D motor driver to control a DC motor and visualize distance readings on an I2C LCD. A Python script runs on a PC to ingest and visualize the distance data in real time.

---

## Table of Contents

* [Overview](#overview)
* [Features](#features)
* [Hardware Requirements](#hardware-requirements)
* [Software Requirements](#software-requirements)
* [Connection Diagram](#connection-diagram)
* [Getting Started](#getting-started)

  * [Part 1: ESP32 Firmware (CODE.C)](#part-1-esp32-firmware)
  * [Part 2: Data Visualization (Python)](#part-2-data-visualization-python)
* [Usage](#usage)
* [Code Structure](#code-structure)
* [Troubleshooting](#troubleshooting)
* [Future Improvements](#future-improvements)

---

## Overview

The ESP32 continuously rotates a DC motor via an L293D H‑bridge, pausing at fixed angular steps to measure distance with an HC‑SR04 ultrasonic sensor. Measurements are displayed on a 16×2 I2C LCD (LiquidCrystal\_I2cTUR) and streamed over serial to a PC. A Python script reads the serial stream, plots a radar‑style visualization, and logs raw data for offline analysis.

---

## Features

* Angular sweep distance measurements (sonar) in 4° steps up to 360°
* Real‑time display of distance on a 16×2 I2C LCD
* Bidirectional DC motor control (forward/reverse) via L293D
* Serial handshake protocol (`RDY`, `FWR`, `Distance:<value>`, `CDR`)
* PC‑side radar visualization with live plotting of measurements
* Data logging for offline analysis

---

## Hardware Requirements

* **ESP32 Development Board**
* **HC‑SR04 Ultrasonic Sensor**
* **L293D Motor Driver**
* **DC Motor** (9 V supply)
* **16×2 I2C LCD** (LiquidCrystal\_I2cTUR compatible)
* **Piezo Buzzer** (optional)
* Breadboard, jumper wires, 9 V battery (or equivalent motor supply)

---

## Software Requirements

* **Arduino IDE** (with ESP32 board support)
* **Python 3.8+**
* Python packages (install via `pip install -r requirements.txt`):

  * `pyserial`
  * `numpy`
  * `matplotlib`

---

## Connection Diagram

```text
ESP32              HC‑SR04           L293D             16×2 I2C LCD         DC Motor           Buzzer
-----              -------           -----             -------------       --------           ------
3V3 ────────────── VCC              VCC                VCC                 + (9 V battery +)
GND ────────────── GND              GND                GND                 - (9 V battery -)
GPIO 13 ── Trig    ─                ─                  ─                   ─                  ─
GPIO 32 ── Echo    ─                ─                  ─                   ─                  ─
GPIO 25 ── Enable  ─  Enable1,2      ─                  ─                   ─                  ─
GPIO 26 ── IN1     ─  Input1         ─                  ─                   ─                  ─
GPIO 27 ── IN2     ─  Input2         ─                  ─                   ─                  ─
GPIO 21 ── SDA     ─                SDA                ─
GPIO 22 ── SCL     ─                SCL                ─
GPIO 14 ── Buzzer  ─                ─                  ─                   ─
```

*(Replace motor leads and power lines according to your battery connector.)*

---

## Getting Started

### Part 1: ESP32 Firmware (CODE.C)

1. Open `CODE.C` in the Arduino IDE.
2. Ensure the following libraries are installed:

   * `Wire.h` (I2C support)
   * `LiquidCrystal_I2cTUR.h` (I2C LCD)
3. Verify pin definitions at the top of the sketch:

   ```cpp
   #define enablePin       25
   #define directionPin1   26
   #define directionPin2   27
   #define buzzer          14
   #define proximityTrig   13
   #define proximityEcho   32
   #define SDA_PIN         21
   #define SCL_PIN         22
   ```
4. Upload to your ESP32.
5. Open the Serial Monitor at **115200 bps** to observe the handshake and distance readings.

### Part 2: Data Visualization (Python)

1. Navigate to the `python/` directory.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
3. Configure the serial port in `GROUP_03_2022510158_2018510126_2021510002_PYTHON_CODE.py`:

   ```python
   PORT = '/dev/ttyUSB0'
   BAUD_RATE = 115200
   ```
4. Run the script:

   ```bash
   python GROUP_03_2022510158_2018510126_2021510002_PYTHON_CODE.py
   ```
5. A radar‑style plot window will open and update in real time.

---

## Usage

1. Power up your ESP32 and motor supply.
2. The ESP32 prints `ESP32: Ready signal received.` when it gets `RDY` from the Python script.
3. The motor sweeps in 4° increments; each step:

   * Stops, triggers the HC‑SR04, displays `Distance:` on LCD.
   * Sends `FWR` then `Distance:<value>` over serial.
4. After 90 measurements, the ESP32 sends `CDR` and reverses sweep direction.
5. The Python script interprets those messages to animate the radar.

---

## Code Structure

```text
├── CODE.C                         Arduino firmware for ESP32
├── LICENSE                        Project license (MIT)
├── python/
│   ├── requirements.txt           Python dependencies
│   └── GROUP_03_2022510158_2018510126_2021510002_PYTHON_CODE.py  PC‑side visualization
└── docs/
    └── wiring_diagram.png         (Optional) high‑res diagram
```

---

## Troubleshooting

* **No serial output**: Verify USB connection, correct COM/TTY port, and baud rate.
* **LCD blank**: Check I2C address (default `0x27`) and `LiquidCrystal_I2cTUR` library.
* **No distance readings**: Confirm HC‑SR04 Vcc/GND, `proximityTrig` (GPIO 13) and `proximityEcho` (GPIO 32).
* **Motor not spinning**: Ensure motor supply connected to L293D Vcc2, `enablePin` (25) set by `analogWrite(enablePin, 255)`.

---

## Future Improvements

* Implement filtering (moving average, Kalman) on distances.
* Add web‑based dashboard via ESP32 Wi‑Fi.
* Switch to hardware interrupts for echo timing for higher precision.
