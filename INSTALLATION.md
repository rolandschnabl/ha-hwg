# HW Group Integration - Installation Guide

## Prerequisites

- Home Assistant 2023.1.0 or newer
- HW Group device (Poseidon 3268, 3266, or SMS Gateway)
- Network access to the device
- Device IP address

## Installation Methods

### Method 1: HACS (Recommended)

1. **Install HACS** (if not already installed)
   - Visit https://hacs.xyz for installation instructions

2. **Add Custom Repository**
   - Open HACS in Home Assistant
   - Click on "Integrations"
   - Click the three dots menu (⋮) in the top right
   - Select "Custom repositories"
   - Add this repository URL
   - Select "Integration" as category
   - Click "Add"

3. **Install Integration**
   - Search for "HW Group Devices"
   - Click "Download"
   - Restart Home Assistant

### Method 2: Manual Installation

1. **Download Integration**
   - Download the latest release
   - Extract the files

2. **Copy Files**
   ```
   custom_components/
   └── hwgroup/
       ├── __init__.py
       ├── manifest.json
       ├── config_flow.py
       ├── const.py
       ├── hwgroup.py
       ├── sensor.py
       ├── binary_sensor.py
       ├── switch.py
       ├── strings.json
       └── translations/
           └── en.json
   ```

3. **Copy to Home Assistant**
   - Copy the entire `hwgroup` folder to your `custom_components` directory
   - The path should be: `<config>/custom_components/hwgroup/`

4. **Restart Home Assistant**

## Configuration

### Step 1: Prepare Your Device

1. Ensure your HW Group device is connected to the network
2. Note the IP address (e.g., 192.168.1.100)
3. If authentication is enabled, have username/password ready
4. Verify you can access the device's web interface

### Step 2: Add Integration

1. Go to **Settings** → **Devices & Services**
2. Click the **+ Add Integration** button
3. Search for "HW Group"
4. Click on "HW Group Devices"

### Step 3: Configure Device

Enter the following information:

- **Host**: Your device IP address (e.g., `192.168.1.100`)
- **Username**: (Optional) Leave blank if no authentication
- **Password**: (Optional) Leave blank if no authentication
- **Device Type**: Select your device model
  - Poseidon 3268
  - Poseidon 3266
  - SMS Gateway

### Step 4: Complete Setup

1. Click **Submit**
2. The integration will test the connection
3. If successful, all sensors and controls will be discovered automatically
4. Entities will appear in Home Assistant

## Verify Installation

### Check Entities

1. Go to **Settings** → **Devices & Services**
2. Find "HW Group Devices" integration
3. Click on it to see the device
4. Click on the device to see all entities

### Expected Entities

Depending on your device configuration, you should see:

- **Sensors**: Temperature, humidity, voltage, current
- **Binary Sensors**: Contacts, alarms
- **Switches**: Relay outputs (Poseidon devices)

### Test Sensors

1. Go to **Developer Tools** → **States**
2. Search for `sensor.hwgroup_` or your device name
3. Verify sensor values are updating

### Test Switches (if applicable)

1. Find a switch entity in your dashboard
2. Try turning it on/off
3. Verify the physical output on the device responds

## Troubleshooting

### Connection Failed

**Error**: "Failed to connect to the device"

**Solutions**:
- Verify IP address is correct
- Check device is powered on and connected to network
- Ping the device: `ping 192.168.1.100`
- Verify firewall isn't blocking port 80
- Try accessing `http://[device-ip]/values.xml` in browser

### Authentication Failed

**Error**: "Invalid authentication credentials"

**Solutions**:
- Verify username and password are correct
- Try without credentials first (some devices allow guest access)
- Check device web interface for authentication settings
- Reset device credentials if necessary

### No Entities Appear

**Solutions**:
- Check Home Assistant logs: **Settings** → **System** → **Logs**
- Verify device has sensors configured in its web interface
- Try removing and re-adding the integration
- Access device's XML API in browser: `http://[device-ip]/values.xml`
- Verify XML contains sensor data

### Entities Not Updating

**Solutions**:
- Check if device is still reachable
- View integration in **Devices & Services** for error status
- Check Home Assistant logs for errors
- Restart Home Assistant
- Reload the integration

## Advanced Configuration

### Change Update Interval

The default polling interval is 30 seconds. To modify:

1. Edit `const.py` in the integration folder
2. Change `DEFAULT_SCAN_INTERVAL` value
3. Restart Home Assistant

### Custom Port

If your device uses a non-standard port:

1. The integration currently uses port 80
2. To modify, edit `hwgroup.py` and change `DEFAULT_PORT`
3. Or add port to host: `192.168.1.100:8080`

### Debug Logging

To enable debug logging:

1. Edit `configuration.yaml`:
   ```yaml
   logger:
     default: info
     logs:
       custom_components.hwgroup: debug
   ```
2. Restart Home Assistant
3. View detailed logs in **System** → **Logs**

## Uninstallation

1. Go to **Settings** → **Devices & Services**
2. Find "HW Group Devices" integration
3. Click the three dots menu (⋮)
4. Select "Delete"
5. Confirm deletion
6. (Optional) Remove custom_components/hwgroup folder
7. Restart Home Assistant

## Support

### Getting Help

- Check the [README.md](README.md) for general information
- Review [Home Assistant Community Forums](https://community.home-assistant.io)
- Open an issue on GitHub with:
  - Home Assistant version
  - Integration version
  - Device model
  - Error messages from logs
  - XML output from `/values.xml` endpoint

### Providing Logs

When reporting issues, include:

1. Home Assistant version
2. Integration version
3. Device model and firmware version
4. Relevant log entries
5. Example XML from device (anonymized if needed)

## Next Steps

After installation:

1. **Create Dashboard Cards** - Add sensor cards to your dashboard
2. **Set Up Automations** - Create automations based on sensor values
3. **Configure Alerts** - Set up notifications for threshold values
4. **Group Entities** - Organize entities into groups or areas
5. **Customize Names** - Rename entities for better identification

## Updates

### Checking for Updates

If using HACS:
- HACS will notify you of available updates
- Click "Update" to install

For manual installations:
- Check GitHub releases page
- Download and replace files
- Restart Home Assistant

## Device-Specific Notes

### Poseidon 3268

- Supports up to 12 sensors
- Has binary inputs and relay outputs
- May require authentication

### Poseidon 3266

- Compact version with fewer sensors
- Limited I/O compared to 3268

### SMS Gateway

- Primarily for SMS notifications
- Limited sensor capabilities
- Status monitoring available

---

**Need more help?** Check the full [README.md](README.md) or open an issue on GitHub.
