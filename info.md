# HW Group Devices Integration

Monitor and control HW Group devices (Poseidon 3268, 3266, SMS Gateway) directly from Home Assistant.

## Features

- 🌡️ Temperature & Humidity monitoring
- ⚡ Voltage & Current sensors
- 🚪 Binary inputs (contacts, alarms)
- 🔌 Relay/output control
- 🔄 Automatic polling (30s interval)
- 🖥️ Easy UI configuration

## Quick Setup

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration** and search for "HW Group"
3. Enter your device IP address
4. (Optional) Add username/password if required
5. Select your device type
6. Done! All sensors and controls will be automatically discovered

## Supported Devices

- **Poseidon 3268** - Full-featured monitoring with multiple sensors and outputs
- **Poseidon 3266** - Compact monitoring device
- **SMS Gateway** - SMS notification capabilities

## Requirements

- HW Group device accessible on your network
- HTTP/XML API enabled on the device
- Home Assistant 2023.1.0 or newer
