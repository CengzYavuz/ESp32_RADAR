# Sonar‑Controlled DC Motor System

A two-part embedded project that uses an ESP32, an ultrasonic proximity sensor, and an L293D motor driver to control a DC motor and visualize distance readings.

---

## Table of Contents

- [Overview](#overview)  
- [Features](#features)  
- [Hardware Requirements](#hardware-requirements)  
- [Software Requirements](#software-requirements)  
- [Connection Diagram](#connection-diagram)  
- [Getting Started](#getting-started)  
  - [Part 1: ESP32 Firmware](#part-1-esp32-firmware)  
  - [Part 2: Data Evaluation (Python)](#part-2-data-evaluation-python)  
- [Usage](#usage)  
- [Code Structure](#code-structure)  
- [Troubleshooting](#troubleshooting)  
- [Future Improvements](#future-improvements)  
- [License](#license)  

---

## Overview

This project measures proximity using an ultrasonic sensor and drives a DC motor accordingly. The ESP32 microcontroller handles:

1. **Visualization** – displays real‑time distance on an attached screen.  
2. **Motor control** – drives a DC motor via an L293D H‑bridge based on sensor readings.

A separate Python script ingests logged distance data for offline analysis and decision making (e.g., threshold detection, filtering, plotting).

---

## Features

- Real‑time distance measurements (sonar)  
- Visual feedback on-screen (OLED/TFT)  
- Bidirectional DC motor control via L293D  
- Data logging over serial/Wi-Fi  
- Offline data analysis and visualization in Python

---

## Hardware Requirements

- **ESP32 Development Board**  
- **Ultrasonic Proximity Sensor** (e.g., HC‑SR04)  
- **L293D Motor Driver**  
- **DC Motor**  
- Display module (OLED/TFT)  
- Breadboard, jumper wires, power supply  

---

## Software Requirements

- **Arduino IDE** (with ESP32 board support)  
- **Python 3.8+**  
- Python packages:  
  - `pyserial` (for data ingestion, if using serial)  
  - `numpy`, `matplotlib`, `pandas` (for analysis/plots)

---

## Connection Diagram

