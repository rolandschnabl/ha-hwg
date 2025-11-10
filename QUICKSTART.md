# Quick Start Guide

Get your HW Group device integrated with Home Assistant in 5 minutes!

## What You'll Need

- ✅ Home Assistant installed and running
- ✅ HW Group device (Poseidon 3268, 3266, or SMS Gateway)
- ✅ Device IP address
- ✅ (Optional) Device username and password

## Step 1: Install Integration (Choose One Method)

### Option A: HACS (Easiest)

1. Open HACS → Integrations
2. Click ⋮ → Custom repositories
3. Add repository URL, select "Integration"
4. Search "HW Group" and click Download
5. Restart Home Assistant

### Option B: Manual

1. Download release
2. Copy `custom_components/hwgroup` to your Home Assistant
3. Restart Home Assistant

## Step 2: Configure Device

1. Settings → Devices & Services → Add Integration
2. Search "HW Group"
3. Enter device details:
   - **IP address**: `192.168.1.100` (example)
   - **Username/Password**: (if needed)
   - **Device type**: Select your model
4. Click Submit

## Step 3: Verify

Check that entities appeared:
- Sensors (temperature, humidity, etc.)
- Binary sensors (contacts)
- Switches (relays)

## Step 4: Use It!

### Add to Dashboard

1. Edit your dashboard
2. Add card → choose entity
3. Select your HW Group sensors

### Create Automation Example

```yaml
# Alert when temperature is too high
automation:
  - alias: "Temperature Alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.hwgroup_temperature_sensor_1
      above: 30
    action:
      service: notify.mobile_app
      data:
        message: "Server room temperature high!"
```

## Troubleshooting

**Can't connect?**
- Verify IP address
- Check device is powered on
- Try: `http://[device-ip]/values.xml` in browser

**No entities?**
- Check logs: Settings → System → Logs
- Verify sensors configured on device

**Authentication failed?**
- Try without username/password first
- Check credentials in device web interface

## Next Steps

- 📊 Add sensor history graphs
- 🔔 Set up temperature alerts
- 🎛️ Control relays from dashboard
- 📱 Create mobile notifications

## Need Help?

- Read [INSTALLATION.md](INSTALLATION.md) for detailed guide
- Check [README.md](README.md) for full documentation
- See [EXAMPLES.md](EXAMPLES.md) for device XML samples
- Open GitHub issue for bugs

---

**That's it!** Your HW Group device is now integrated with Home Assistant. 🎉
