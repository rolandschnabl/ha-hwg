# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2025-11-10

### Added - SMS Gateway Support 📱

#### New Services
- **`hwgroup.send_sms`** - Send SMS messages via HWg-SMS-GW3
  - Support for international phone number formats
  - UTF-8 message encoding
  - Up to 160 characters per SMS
- **`hwgroup.call_number`** - Ring phone numbers via HWg-SMS-GW3
  - Silent alarm capability (ring and hang up)
  - Cheaper alternative to SMS for simple alerts

#### New SMS Gateway Sensors
- **Signal Strength** - Cellular signal strength in dBm (-50 to -110 dBm)
- **Signal Quality** - Signal quality percentage (0-100%)
- **Network Operator** - Current mobile network operator name
- **Network Status** - Network registration status (e.g., "Registered, home network")
- **SMS Sent** - Counter of successfully sent SMS messages
- **SMS Errors** - Counter of failed SMS attempts

#### New Documentation
- **SMS_SERVICES.md** - Comprehensive guide with 8 detailed automation examples:
  - Temperature alarms
  - Door monitoring
  - Daily status reports
  - Critical multi-notification alerts
  - Multiple recipients
  - And more!
- **SMS_QUICKSTART.md** - 5-minute quick setup guide for SMS functionality
- Updated **README.md** with SMS features and capabilities

#### Technical Improvements
- Automatic fetching of `status.xml` for SMS Gateway devices
- Enhanced XML parsing supporting multiple formats:
  - Poseidon devices with namespace (`<val:Root>`)
  - SMS Gateway without namespace (`<Root>`)
- Improved device type detection for HWg-SMS-GW3
- Added extensive debug logging for troubleshooting
- Service definitions in `services.yaml` for UI integration

### Fixed
- Network Operator sensor correctly handles empty text values
- XML parsing supports both `<SenSet>` (Poseidon) and agent-only formats (SMS Gateway)
- Device type detection now recognizes "HWg-SMS-GW3" model string
- Improved error handling for missing XML elements

### Changed
- Moved "Parsed data" log message after SMS Gateway status parsing (accurate sensor counts)
- Enhanced device info parsing to support both `<Title>` and `<ProductName>` elements

---

## [1.0.0] - 2025-11-10

### Added - Initial Release 🎉
- Initial release with core monitoring functionality
- Support for HW Group Poseidon 3268 devices
- Support for HW Group Poseidon 3266 devices  
- Support for HW Group SMS Gateway devices (basic recognition)
- Temperature sensor monitoring (°C)
- Humidity sensor monitoring (%)
- Voltage and current sensor monitoring (V, A)
- Binary sensor support (contacts, alarms)
- Switch/relay control for Poseidon outputs
- UI-based configuration flow with automatic device discovery
- Options flow for live configuration updates without restart
- Data update coordinator for efficient polling (30s interval)
- HACS compatibility with proper metadata
- Integration icon (256x256 PNG)

### Features
- HTTP/XML API communication via aiohttp
- Basic authentication support (username/password)
- Configurable polling interval (default 30 seconds)
- Device information and attributes (model, serial, version)
- Multiple sensor types with proper Home Assistant device classes
- Unique device IDs based on host + serial number (multi-device support)
- Automatic device type detection from model information
- Error handling and connection validation
- Debug logging for troubleshooting

### Documentation
- README.md with installation and usage instructions
- EXAMPLES.md with XML format examples
- QUICKSTART.md for rapid setup
- INSTALLATION.md with detailed setup steps
- ARCHITECTURE.md for developers
- TROUBLESHOOTING.md for common issues

---

## Release Notes

### Upgrading to v1.1.0

**What's New:**
- Complete SMS Gateway functionality for sending SMS and making calls from automations
- 6 new sensors for monitoring SMS Gateway health and cellular connectivity
- Comprehensive documentation with ready-to-use automation examples

**Upgrade Steps:**
1. Update the integration files via HACS or manually copy new files
2. Restart Home Assistant
3. **Important**: If you have an SMS Gateway configured:
   - Remove the device from the integration
   - Re-add it to enable new sensors
4. **Required**: Enable HTTP GET in SMS Gateway settings:
   - Open gateway web interface: `http://[IP-ADDRESS]`
   - Go to **GSM Modem** tab
   - Check ☑️ **"Enable HTTP GET for sending SMS"**
   - Save settings
5. Test SMS functionality using Developer Tools → Services
6. Follow [SMS_QUICKSTART.md](SMS_QUICKSTART.md) for complete setup

**Breaking Changes:** None - fully backward compatible with v1.0.0

**Known Issues:** None

---

## Roadmap

### v1.2.0 (Planned)
- [ ] Additional Poseidon sensors (pressure, air quality)
- [ ] Advanced SMS queuing and rate limiting  
- [ ] SMS templates with variable substitution
- [ ] Home Assistant notify platform integration
- [ ] SMS character encoding optimization

### v1.3.0 (Planned)
- [ ] Support for Poseidon 2250
- [ ] Relay scheduling and automation
- [ ] Historical data and statistics
- [ ] Custom update intervals per device
- [ ] Web UI for SMS Gateway statistics

### Future Considerations
- SNMP support as alternative to HTTP API
- Local push notifications instead of polling only
- SMS response handling (incoming SMS processing)
- Multi-language SMS support with translations
- Integration with external notification services

---

## Contributing

Contributions are welcome! To contribute:

1. **Fork** the repository
2. Create a **feature branch** (`git checkout -b feature/amazing-feature`)
3. Make your changes with **clear commit messages**
4. **Test thoroughly** on a real Home Assistant installation
5. Update **documentation** if needed
6. Submit a **pull request**

### Development Guidelines
- Follow Home Assistant integration best practices
- Add tests for new features
- Update CHANGELOG.md with your changes
- Maintain backward compatibility when possible

---

## Support & Community

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/rolandschnabl/ha-hwg/issues)
- 💡 **Feature Requests**: [GitHub Issues](https://github.com/rolandschnabl/ha-hwg/issues)
- 📖 **Documentation**: Check the repository docs folder
- 💬 **Community**: Home Assistant Community Forums
- 📧 **Contact**: Open an issue for questions

---

## Acknowledgments

- Thanks to HW Group for their well-documented API
- Home Assistant community for integration development resources
- All users who provide feedback and bug reports

---

**Note**: This integration is actively maintained. Feature requests and bug reports are welcome and appreciated!
