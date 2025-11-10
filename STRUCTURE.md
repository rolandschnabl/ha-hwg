# HW Group Integration - Project Structure

## Complete File Structure

```
hwg/
├── custom_components/
│   └── hwgroup/
│       ├── __init__.py              # Main integration setup
│       ├── manifest.json            # Integration metadata
│       ├── config_flow.py           # UI configuration flow
│       ├── const.py                 # Constants and configuration
│       ├── hwgroup.py               # API client for HW Group devices
│       ├── sensor.py                # Temperature, humidity, voltage sensors
│       ├── binary_sensor.py         # Contact/alarm sensors
│       ├── switch.py                # Relay/output controls
│       ├── strings.json             # UI strings
│       ├── icon.json                # Integration icon metadata
│       └── translations/
│           └── en.json              # English translations
│
├── README.md                        # Main documentation
├── INSTALLATION.md                  # Detailed installation guide
├── EXAMPLES.md                      # XML examples from devices
├── CHANGELOG.md                     # Version history
├── LICENSE                          # MIT License
├── .gitignore                       # Git ignore rules
├── hacs.json                        # HACS metadata
└── info.md                          # HACS info page

```

## File Descriptions

### Core Integration Files

#### `__init__.py`
- Main integration entry point
- Sets up coordinator for data polling
- Manages platform loading (sensor, binary_sensor, switch)
- Handles integration lifecycle (setup, unload)

#### `manifest.json`
- Integration metadata
- Domain: `hwgroup`
- Requirements: aiohttp>=3.8.0
- Integration type: device
- Config flow enabled

#### `config_flow.py`
- UI-based configuration
- Device connection validation
- Authentication handling
- Unique device identification via serial number

#### `const.py`
- Domain constant: `hwgroup`
- Device type definitions
- Default values (scan interval: 30s, port: 80)
- Sensor and binary sensor type definitions

#### `hwgroup.py`
- API client class `HWGroupAPI`
- HTTP/XML communication
- Data parsing from device XML
- Error handling (connection, authentication)
- Output/relay control methods

### Platform Files

#### `sensor.py`
- Temperature sensors (°C)
- Humidity sensors (%)
- Voltage sensors (V)
- Current sensors (A)
- Generic sensors with custom units
- Proper device classes and state classes

#### `binary_sensor.py`
- Contact sensors (door/window)
- Alarm sensors
- Device classes: opening, problem
- Binary state tracking

#### `switch.py`
- Relay/output control
- Turn on/off functionality
- State synchronization with device
- Uses API to send commands

### Configuration Files

#### `strings.json` & `translations/en.json`
- UI text for configuration flow
- Error messages
- Form labels and descriptions

#### `hacs.json`
- HACS compatibility metadata
- Minimum HACS version: 1.6.0
- Home Assistant minimum: 2023.1.0
- IoT class: Local Polling

### Documentation Files

#### `README.md`
- Overview and features
- Installation instructions
- Configuration guide
- Troubleshooting
- API details

#### `INSTALLATION.md`
- Detailed step-by-step installation
- HACS and manual methods
- Configuration walkthrough
- Troubleshooting section
- Advanced configuration

#### `EXAMPLES.md`
- XML response examples
- Poseidon 3268 sample
- Poseidon 3266 sample
- SMS Gateway sample
- XML structure explanation

#### `CHANGELOG.md`
- Version history
- Features added
- Changes documented

## Key Features Implemented

### 1. Device Communication
- HTTP/XML API support
- Basic authentication
- Async operations with aiohttp
- Error handling and validation

### 2. Entity Types
- **Sensors**: Temperature, humidity, voltage, current, generic
- **Binary Sensors**: Contacts, alarms
- **Switches**: Relay outputs

### 3. Home Assistant Integration
- Config flow for UI setup
- Data update coordinator (30s polling)
- Device registry integration
- Proper entity attributes
- Unique IDs for all entities

### 4. Supported Devices
- Poseidon 3268 (full-featured)
- Poseidon 3266 (compact)
- SMS Gateway

### 5. HACS Compatibility
- Proper metadata files
- Installation via HACS
- Update notifications
- Repository structure

## API Endpoints Used

### Read Data
```
GET http://[device-ip]/values.xml
```
Returns XML with all sensor, input, and output states.

### Control Output
```
GET http://[device-ip]/output.xml?id=[id]&state=[0|1]
```
Sets relay/output state (0=off, 1=on).

## Configuration Flow

1. User enters device IP address
2. Optional: username and password
3. Integration tests connection
4. Retrieves device information
5. Creates unique ID from serial number
6. Discovers all available entities
7. Creates entities in Home Assistant

## Data Update Flow

1. Coordinator triggers update (every 30s)
2. API client fetches `/values.xml`
3. XML parsed into structured data
4. Data distributed to all entities
5. Entity states updated in Home Assistant

## Error Handling

- **Connection errors**: Logged and reported to user
- **Authentication errors**: Specific error message
- **XML parsing errors**: Gracefully handled
- **Timeout handling**: 10-second timeout on requests

## Entity Naming

- **Sensors**: `sensor.hwgroup_[sensor_name]`
- **Binary Sensors**: `binary_sensor.hwgroup_[input_name]`
- **Switches**: `switch.hwgroup_[output_name]`

## Device Information

All entities include device info:
- Identifiers: Domain + entry ID
- Name: Device name from XML
- Manufacturer: "HW Group"
- Model: From device XML
- Software version: Firmware version

## State Attributes

### Sensors
- `state`: Sensor state (ok, warning, alarm)
- `sensor_id`: Unique sensor identifier

### Binary Sensors
- `binary_sensor_id`: Unique input identifier

### Switches
- `output_id`: Unique output identifier

## Installation Requirements

- Home Assistant 2023.1.0+
- Python 3.10+
- aiohttp library
- Network access to device

## Usage Example

### In Automations
```yaml
automation:
  - alias: "High Temperature Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.hwgroup_temperature_sensor_1
        above: 30
    action:
      - service: notify.mobile_app
        data:
          message: "Temperature is too high!"
```

### Controlling Relays
```yaml
automation:
  - alias: "Turn on cooling fan"
    trigger:
      - platform: numeric_state
        entity_id: sensor.hwgroup_temperature_sensor_1
        above: 25
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.hwgroup_relay_1
```

## Testing Checklist

- [ ] Install integration via HACS or manual
- [ ] Configure device through UI
- [ ] Verify all sensors appear
- [ ] Check sensor values update
- [ ] Test binary sensor states
- [ ] Test switch on/off commands
- [ ] Verify device information
- [ ] Check logs for errors
- [ ] Test reconnection after device restart
- [ ] Verify authentication (if enabled)

## Development Notes

### Adding New Sensor Types

1. Add constant to `const.py`
2. Add device class mapping in `sensor.py`
3. Update `_determine_sensor_type()` in `hwgroup.py`

### Supporting New Devices

1. Test with device's `/values.xml` output
2. Update XML parsing if structure differs
3. Add device type to `const.py`
4. Update documentation

### Debugging

Enable debug logging in `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.hwgroup: debug
```

## Future Enhancements

Possible improvements:
- [ ] Device discovery via SSDP/mDNS
- [ ] SMS sending capability (SMS Gateway)
- [ ] Historical data graphing
- [ ] Alarm threshold configuration
- [ ] Email notification support
- [ ] Multiple device support
- [ ] Backup/restore device config
- [ ] Firmware update notifications

## Contributing

To contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

- GitHub Issues: Report bugs and request features
- Home Assistant Community: Ask questions
- Device Documentation: Refer to HW Group manuals

## License

MIT License - See LICENSE file for details

---

**Integration Version**: 1.0.0  
**Last Updated**: November 10, 2025  
**Home Assistant Minimum**: 2023.1.0
