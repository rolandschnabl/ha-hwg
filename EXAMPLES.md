# Example XML Responses from HW Group Devices

This document shows example XML responses from HW Group devices to help with understanding and troubleshooting.

## Poseidon 3268 - values.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<response>
  <agent version="3.5.0" model="Poseidon2 3268" serialNumber="P2-3268-12345">
    <name>Poseidon Device</name>
  </agent>
  <senset>
    <entry id="1" name="Temperature Sensor 1">
      <value>22.5</value>
      <unit>°C</unit>
      <state>ok</state>
    </entry>
    <entry id="2" name="Humidity Sensor 1">
      <value>45.2</value>
      <unit>%</unit>
      <state>ok</state>
    </entry>
    <entry id="3" name="Voltage Monitor">
      <value>12.3</value>
      <unit>V</unit>
      <state>ok</state>
    </entry>
  </senset>
  <inputs>
    <input id="1" name="Door Contact">
      <state>0</state>
    </input>
    <input id="2" name="Window Contact">
      <state>1</state>
    </input>
  </inputs>
  <outputs>
    <output id="1" name="Relay 1">
      <state>0</state>
    </output>
    <output id="2" name="Relay 2">
      <state>1</state>
    </output>
  </outputs>
</response>
```

## Poseidon 3266 - values.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<response>
  <agent version="2.1.0" model="Poseidon2 3266" serialNumber="P2-3266-67890">
    <name>Server Room Monitor</name>
  </agent>
  <senset>
    <entry id="1" name="Room Temperature">
      <value>24.8</value>
      <unit>°C</unit>
      <state>ok</state>
    </entry>
    <entry id="2" name="Room Humidity">
      <value>52.0</value>
      <unit>%RH</unit>
      <state>ok</state>
    </entry>
  </senset>
  <inputs>
    <input id="1" name="Rack Door">
      <state>0</state>
    </input>
  </inputs>
</response>
```

## SMS Gateway - values.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<response>
  <agent version="1.5.2" model="SMS-GW" serialNumber="SMS-GW-11223">
    <name>SMS Gateway</name>
  </agent>
  <status>
    <signal>85</signal>
    <messages_sent>1234</messages_sent>
    <messages_failed>5</messages_failed>
  </status>
</response>
```

## Testing Your Device

To see your device's actual XML output:

1. Open a web browser
2. Navigate to: `http://[your-device-ip]/values.xml`
3. If authentication is required, enter username/password when prompted
4. Save or copy the XML for reference

## Common XML Elements

### Agent Information
- `version`: Firmware version
- `model`: Device model
- `serialNumber`: Unique device identifier
- `name`: User-configured device name

### Sensor Entry
- `id`: Unique sensor identifier
- `name`: Sensor name
- `value`: Current reading
- `unit`: Unit of measurement (°C, %, V, A, etc.)
- `state`: Sensor state (ok, warning, alarm)

### Binary Input
- `id`: Input identifier
- `name`: Input name
- `state`: 0=inactive/closed, 1=active/open

### Output/Relay
- `id`: Output identifier
- `name`: Output name
- `state`: 0=off, 1=on

## Variations by Device

Different HW Group devices may use slightly different XML structures. The integration is designed to handle common variations, including:

- Different tag names (entry vs sensor)
- Optional elements
- Various state representations
- Multiple sensor types

If your device uses a different XML format, please open an issue on GitHub with an example.
