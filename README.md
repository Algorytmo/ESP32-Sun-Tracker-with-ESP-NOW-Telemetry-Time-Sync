# ESP32-Sun-Tracker-with-ESP-NOW-Telemetry-Time-Sync
_A low‑power autonomous solar node with astronomical tracking, battery monitoring, and wireless synchronization_.


__Overview__

This project aims to create a fully autonomous and energy‑efficient ‘smart slot’ that tries to powers or hosts any type of environmental sensor in the most sustainable way possible.
The goal is to build a platform that can operate off‑grid, using only solar energy, while maximizing battery life through ultra‑low‑power design, intelligent power management, and precise astronomical sun tracking.
The system is designed to be durable, modular, and adaptable, enabling long‑term deployments for air‑quality monitoring, environmental sensing, IoT nodes, or any low‑power device that benefits from a self‑sustaining energy source.

This project implements a fully autonomous solar‑powered ESP32 node capable of:

- Astronomical sun tracking (azimuth + elevation)
- Servo‑controlled dual‑axis movement (pan/tilt)
- Battery, panel voltage, current, and power monitoring
- Ultra‑low‑power operation using deep sleep
- ESP‑NOW communication with a base station
- Blocking handshake protocol for reliable time & location sync
- Manual override mode using a joystick
- OLED display for real‑time diagnostics
- The system is designed for outdoor, long‑term, low‑maintenance operation, powered entirely by a small solar panel and a Li‑ion battery.



__Architecture__

The project consists of two ESP32-32U boards:

1. Solar Node (ESP32‑Solar)
- Runs on battery + solar panel
- Wakes up periodically
- Sends telemetry to the base
- Waits (blocking) for time + GPS coordinates
- Updates RTC
- Computes sun position
- Moves servos
- Goes back to deep sleep

2. Base Station (ESP32‑Base)
- Connected to Wi‑Fi, retrieves:
  Geolocation (via IP‑API)
  Time (via NTP)
- Waits for telemetry
- Sends time + lat/lon to the solar node

This ensures perfect synchronization and zero drift, even after long deep‑sleep cycles.



__Communication Protocol (Blocking Handshake)__

The system uses a deterministic two‑phase ESP‑NOW handshake:
SOLAR → BASE: Telemetry packet
BASE  → SOLAR: Time + Latitude + Longitude

The solar node does not proceed until the base responds.
This guarantees:
- Correct RTC time
- Accurate astronomical tracking
- No lost packets
- No race conditions



__Electronic Components__

Power System Components
```
-Samsung 18650 Li‑ion Battery
Nominal voltage: 3.7V
Max voltage: 4.2V

- Solar Panel (6W, 6V)
Provides energy for battery charging and system operation

- CN3791 Solar Charger Module
MPPT‑like behavior optimized for 6V panels
Handles variable solar input without locking up
Safely charges the 18650 battery

- MCP1700 LDO Regulator (3.3V)
Ultra‑low quiescent current (~1.6 µA)
Powers the ESP32 and sensors
Requires 1 µF input + 1 µF output capacitors

- 5V Step‑Up Converter (Boost Converter)
Boosts battery voltage (3.0–4.2V) to stable 5V
Powers:
  Servos
  5V rail monitoring
  Decoupled with a 470 µF capacitor to handle servo current peaks
```

Control & Communication Components
```
- ESP32‑WROOM‑32U (with IPEX antenna)
Main microcontroller
External antenna for improved ESP‑NOW range
Handles:
  Sun tracking logic
  Telemetry
  Deep sleep
  Joystick manual mode
  OLED display

- INA219 Current/Voltage Sensor
Measures:
  Solar panel voltage
  Solar panel current
  Power (mW)
  Includes 0.1 Ω shunt resistor
  Requires 1 µF supply capacitor for stable readings
```

User Interface Components
```
- Analog Joystick
VRX, VRY, SW buttons
Used for manual override mode

- SSD1306 OLED Display (I2C)
128×64 pixels
Shows:
  Mode (AUTO/MANUAL)
  Voltage, current, power
  Pan/tilt angles
```

Passive Components
```
Resistors
- Battery voltage divider	10 kΩ + 10 kΩ	Scales battery voltage (max ~4.2V) to safe ADC range
- 5V rail voltage divider	10 kΩ + 10 kΩ	Same divider ratio for consistent calibration
- 3.3V rail voltage divider	10 kΩ + 10 kΩ	Used for monitoring ESP32 internal supply
- INA219 shunt resistor	0.1 Ω	Provided by the INA219 module

Capacitors
- MCP1700 input capacitor	1 µF	Required by MCP1700 datasheet
- MCP1700 output capacitor	1 µF	Required for regulator stability
- Battery input smoothing	47 µF	Stabilizes battery line during load changes
- 5V rail servo smoothing	470 µF	Prevents voltage dips when servos move
- INA219 supply filtering	1 µF	Recommended for stable current/voltage readings
```


__Software Structure__

The firmware is fully modular:
```
/solar/
main.py
config.py
espnow_handler.py
hardware.py
ina219.py
joystick.py
logging.py
logging_utils.py
power.py
ssd1306.py
telemetry.py
tracking.py
```


Key Modules

- main.py
Main entry point containing the full solar node logic.

- config.py  
All constants and tunable parameters.

- hardware.py  
ADC, INA219, display, servos, voltage reading.

- tracking.py  
Astronomical sun‑position calculations.

- telemetry.py  
Telemetry packet creation + ESP‑NOW send.

- espnow_handler.py  
Peer initialization + blocking receive.

- joystick.py  
Manual override mode.

- power.py  
Deep sleep helpers.

- logging_utils.py  
Logging option



__Astronomical Tracking__

The solar node computes:
- Julian day
- Solar mean anomaly
- Ecliptic longitude
- Right ascension
- Declination
- Local sidereal time
- Hour angle
- Azimuth
- Elevation

Then maps:
azimuth → pan servo
elevation → tilt servo

Elevation is clamped to 0–90° to avoid pointing below the horizon.



__Power Management__

The solar node is optimized for ultra‑low power:
- INA219 power measurement
- ADC battery monitoring
- OLED auto‑off before sleep
- Servo PWM deinit before sleep
- Deep sleep between cycles (default: 10 minutes)
- Wake‑on‑joystick interrupt



__Telemetry Format__

Example telemetry packet:
```
{
  "ts": 1718467200,
  "bat_v": 3.50,
  "panel_v": 5.08,
  "panel_i": 0.128,
  "panel_p": 0.652,
  "pan": 90,
  "tilt": 45
}
```

__To Do__

- configure better manual mode
- configure better auto mode
- add photo and data graphics
