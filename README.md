# HW Group Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

This custom integration provides support for HW Group devices in Home Assistant, including:

- **Poseidon 3268** - Multi-sensor monitoring device
- **Poseidon 3266** - Compact monitoring device  
- **SMS Gateway** - SMS notification device

## Features

- 🌡️ **Temperature Sensors** - Monitor temperature from connected probes
- 💧 **Humidity Sensors** - Track humidity levels
- ⚡ **Voltage/Current Sensors** - Monitor electrical parameters
- 🚪 **Binary Sensors** - Track door contacts, alarms, and other binary inputs
- 🔌 **Switch/Relay Control** - Control outputs on Poseidon devices
- � **SMS Services** - Send SMS and make calls via SMS Gateway (see [SMS Services Documentation](SMS_SERVICES.md))
- 📶 **Signal Monitoring** - Monitor cellular signal quality and network status
- �🔄 **Automatic Updates** - Regular polling of device status (configurable interval)
- 🖥️ **UI Configuration** - Easy setup through the Home Assistant UI
- 🎯 **Automatic Device Detection** - Automatically detects device type from model information

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner and select "Custom repositories"
4. Add this repository URL and select "Integration" as the category
5. Click "Install"
6. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/hwgroup` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

### Through the UI (Recommended)

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "HW Group Devices"
4. Enter your device details:
   - **Host**: IP address or hostname of your HW Group device (e.g., `192.168.1.100`)
   - **Username**: (Optional) Username for authentication
   - **Password**: (Optional) Password for authentication
   - **Device Type**: Select your device model (Poseidon 3268, 3266, or SMS Gateway)
5. Click **Submit**

The integration will automatically discover all sensors, binary sensors, and switches available on your device.

## Supported Devices

### Poseidon 3268
- Multiple temperature/humidity sensors
- Binary inputs for door/window contacts
- Relay outputs for controlling equipment
- Voltage and current monitoring

### Poseidon 3266
- Temperature and humidity monitoring
- Binary inputs
- Compact form factor

### SMS Gateway
- 📱 SMS sending and phone call capabilities
- 📶 Cellular signal strength monitoring (dBm)
- 📊 Signal quality monitoring (%)
- 📡 Network operator detection
- 📈 SMS statistics (sent/errors)
- 🔔 Network registration status

**See [SMS Services Documentation](SMS_SERVICES.md) for detailed SMS automation examples!**

## Device Communication

The integration communicates with HW Group devices using their HTTP/XML API. Devices are polled every 30 seconds by default to retrieve:
- Sensor values (temperature, humidity, voltage, current)
- Binary input states (contacts, alarms)
- Output/relay states

## Entities

The integration creates the following entity types:

### Sensors
- Temperature sensors (°C)
- Humidity sensors (%)
- Voltage sensors (V)
- Current sensors (A)
- Generic sensors (with custom units)

### Binary Sensors
- Contact sensors (door/window contacts)
- Alarm sensors

### Switches
- Relay/output controls

All entities include:
- Unique identifiers
- Device information
- State attributes with additional details

## Troubleshooting

### Cannot Connect to Device

1. Verify the device IP address is correct
2. Ensure the device is on the same network or accessible from Home Assistant
3. Check if authentication is required (username/password)
4. Verify the device's web interface is accessible in a browser

### No Sensors Appear

1. Check the device logs in Home Assistant (**Settings** → **System** → **Logs**)
2. Verify the device has sensors configured in its web interface
3. Try removing and re-adding the integration

### Authentication Errors

1. Verify username and password are correct
2. Check if the device requires authentication to access the XML API
3. Some devices may have read-only guest access - try without credentials first

## API Details

The integration uses the following API endpoints:
- `http://[device-ip]/values.xml` - Retrieve sensor values and states
- `http://[device-ip]/output.xml?id=[id]&state=[0|1]` - Control outputs

## Development

This integration uses:
- **aiohttp** for async HTTP communication
- **XML parsing** for device data
- **DataUpdateCoordinator** for efficient polling
- **Config Flow** for UI-based setup

## Support

For issues, feature requests, or questions:
- Open an issue on GitHub
- Check the Home Assistant community forums

## License

This project is licensed under the MIT License.

## Credits

Developed for HW Group device integration with Home Assistant.

HW Group official website: https://www.hw-group.com/

---

**Note**: This is a custom integration and is not officially affiliated with HW Group or Home Assistant.
