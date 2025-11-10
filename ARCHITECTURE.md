# HW Group Integration Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      Home Assistant                              │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              HW Group Integration                          │  │
│  │                                                             │  │
│  │  ┌─────────────┐      ┌──────────────┐                   │  │
│  │  │ Config Flow │──────▶│ Coordinator  │                   │  │
│  │  └─────────────┘      └──────┬───────┘                   │  │
│  │                               │                            │  │
│  │                               │ Polls every 30s            │  │
│  │                               ▼                            │  │
│  │                       ┌───────────────┐                   │  │
│  │                       │  API Client   │                   │  │
│  │                       │  (hwgroup.py) │                   │  │
│  │                       └───────┬───────┘                   │  │
│  │                               │                            │  │
│  │         ┌─────────────────────┼─────────────────────┐    │  │
│  │         │                     │                     │     │  │
│  │         ▼                     ▼                     ▼     │  │
│  │  ┌────────────┐       ┌──────────────┐      ┌──────────┐│  │
│  │  │  Sensors   │       │Binary Sensors│      │ Switches ││  │
│  │  │ (sensor.py)│       │(binary_     │      │(switch.py)││  │
│  │  │            │       │ sensor.py)  │      │          ││  │
│  │  └────────────┘       └──────────────┘      └──────────┘│  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/XML API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    HW Group Device                               │
│              (Poseidon 3268/3266/SMS Gateway)                   │
│                                                                   │
│  Endpoints:                                                      │
│  • GET /values.xml        - Read all data                       │
│  • GET /output.xml?id=X   - Control relay                       │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Setup Phase

```
User Action                     Integration                    Device
    │                                │                           │
    ├──[Add Integration]────────────▶│                           │
    │                                │                           │
    ├──[Enter IP/Credentials]───────▶│                           │
    │                                │                           │
    │                                ├──[Test Connection]───────▶│
    │                                │                           │
    │                                │◀──[Return device info]────┤
    │                                │                           │
    │◀──[Show discovered entities]───┤                           │
    │                                │                           │
    └──[Complete Setup]──────────────┤                           │
                                     │                           │
                         [Create entities & start polling]       │
```

### Polling Phase (Every 30 seconds)

```
Coordinator                  API Client                  Device
    │                           │                          │
    ├──[Trigger Update]────────▶│                          │
    │                           │                          │
    │                           ├──GET /values.xml────────▶│
    │                           │                          │
    │                           │◀─[XML Response]──────────┤
    │                           │                          │
    │                           ├──[Parse XML]             │
    │                           │                          │
    │◀──[Return parsed data]────┤                          │
    │                           │                          │
    ├──[Distribute to entities]                            │
    │                                                       │
    ├──▶ Sensors                                           │
    ├──▶ Binary Sensors                                    │
    └──▶ Switches                                          │
```

### Control Phase (Switch)

```
User                      Switch Entity           API Client          Device
 │                            │                       │                 │
 ├──[Turn On]────────────────▶│                       │                 │
 │                            │                       │                 │
 │                            ├──[Call API]──────────▶│                 │
 │                            │                       │                 │
 │                            │                       ├──GET output.xml▶│
 │                            │                       │  ?id=1&state=1  │
 │                            │                       │                 │
 │                            │                       │◀─[OK]───────────┤
 │                            │                       │                 │
 │                            │◀──[Success]───────────┤                 │
 │                            │                       │                 │
 │                            ├──[Request Refresh]────────────────────────┐
 │                            │                                           │
 │◀──[State Updated]──────────┤                                           │
 └────────────────────────────────────────────────────────────────────────┘
```

## Component Relationships

```
┌──────────────────────────────────────────────────────────────┐
│                        manifest.json                          │
│  Defines: domain, name, version, requirements                │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                        __init__.py                            │
│  • async_setup_entry() - Create coordinator                  │
│  • async_unload_entry() - Cleanup                           │
│  • Forward setup to platforms                               │
└──────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  sensor.py  │    │binary_      │    │  switch.py  │
│             │    │sensor.py    │    │             │
│ Creates:    │    │             │    │ Creates:    │
│ - Temp      │    │ Creates:    │    │ - Relays    │
│ - Humidity  │    │ - Contacts  │    │ - Outputs   │
│ - Voltage   │    │ - Alarms    │    │             │
│ - Current   │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  hwgroup.py   │
                    │               │
                    │ - API calls   │
                    │ - XML parsing │
                    │ - Auth        │
                    └───────────────┘
```

## File Dependencies

```
config_flow.py
    └─── hwgroup.py (for connection testing)
    └─── const.py (for constants)

__init__.py
    ├─── hwgroup.py (create API client)
    ├─── const.py (domain, platforms)
    └─── coordinator (Home Assistant)

sensor.py
    ├─── coordinator (data source)
    └─── const.py (domain)

binary_sensor.py
    ├─── coordinator (data source)
    └─── const.py (domain)

switch.py
    ├─── coordinator (data source)
    ├─── hwgroup.py (control outputs)
    └─── const.py (domain)

hwgroup.py
    └─── aiohttp (HTTP client)
    └─── xml.etree.ElementTree (XML parsing)
```

## Entity Hierarchy

```
HW Group Device (Device)
├─── Device Info
│    ├─── Name: "Poseidon Device"
│    ├─── Manufacturer: "HW Group"
│    ├─── Model: "Poseidon2 3268"
│    └─── Serial: "P2-3268-12345"
│
├─── Sensors (Platform)
│    ├─── sensor.hwgroup_temperature_sensor_1
│    │    ├─── Value: 22.5
│    │    ├─── Unit: °C
│    │    ├─── Device Class: temperature
│    │    └─── State Class: measurement
│    │
│    ├─── sensor.hwgroup_humidity_sensor_1
│    │    ├─── Value: 45.2
│    │    ├─── Unit: %
│    │    ├─── Device Class: humidity
│    │    └─── State Class: measurement
│    │
│    └─── sensor.hwgroup_voltage_monitor
│         ├─── Value: 12.3
│         ├─── Unit: V
│         ├─── Device Class: voltage
│         └─── State Class: measurement
│
├─── Binary Sensors (Platform)
│    ├─── binary_sensor.hwgroup_door_contact
│    │    ├─── State: off
│    │    └─── Device Class: opening
│    │
│    └─── binary_sensor.hwgroup_window_contact
│         ├─── State: on
│         └─── Device Class: opening
│
└─── Switches (Platform)
     ├─── switch.hwgroup_relay_1
     │    └─── State: off
     │
     └─── switch.hwgroup_relay_2
          └─── State: on
```

## Configuration Flow States

```
                    ┌─────────┐
                    │  START  │
                    └────┬────┘
                         │
                         ▼
              ┌──────────────────┐
              │   User Input     │
              │  (IP, Auth, etc) │
              └────┬────┬────────┘
                   │    │
        ┌──────────┘    └──────────┐
        │                           │
        ▼                           ▼
   ┌─────────┐               ┌──────────┐
   │  ERROR  │               │ VALIDATE │
   │         │               │          │
   │ • Cannot│               └────┬─────┘
   │   Connect                    │
   │ • Auth   │                   │
   │   Failed │          ┌────────┴────────┐
   └────┬────┘           │                 │
        │                ▼                 ▼
        │          ┌──────────┐      ┌──────────┐
        │          │  SUCCESS │      │ ALREADY  │
        │          │          │      │CONFIGURED│
        │          │  Create  │      └──────────┘
        │          │  Entry   │
        │          └──────────┘
        │                │
        └────────────────┘
```

## XML Parsing Flow

```
XML Response from Device
        │
        ▼
┌─────────────────┐
│ Parse XML Root  │
└────────┬────────┘
         │
    ┌────┴────┬─────────────┬──────────────┐
    │         │             │              │
    ▼         ▼             ▼              ▼
┌────────┐ ┌──────┐  ┌────────────┐  ┌─────────┐
│ Agent  │ │Sensors│  │Binary Input│  │ Outputs │
│  Info  │ │(entry)│  │  (input)   │  │(output) │
└───┬────┘ └───┬──┘  └──────┬─────┘  └────┬────┘
    │          │             │              │
    ▼          ▼             ▼              ▼
┌────────┐ ┌──────┐  ┌────────────┐  ┌─────────┐
│Name    │ │Value │  │State: 0/1  │  │State:0/1│
│Model   │ │Unit  │  │            │  │         │
│Serial  │ │State │  │            │  │         │
│Version │ │Type  │  │            │  │         │
└────────┘ └──────┘  └────────────┘  └─────────┘
    │          │             │              │
    └──────────┴─────────────┴──────────────┘
                     │
                     ▼
            ┌────────────────┐
            │ Structured Data│
            │    Dictionary  │
            └────────────────┘
```

## Error Handling Flow

```
API Call
   │
   ├─▶ Try
   │     │
   │     ├─▶ HTTP Request
   │     │      │
   │     │      ├─▶ 200 OK ──────────▶ Parse XML ──▶ Return Data
   │     │      │
   │     │      ├─▶ 401 Unauthorized ─▶ Raise AuthError
   │     │      │
   │     │      └─▶ Other Error ──────▶ Raise ConnectionError
   │     │
   │     └─▶ Exceptions
   │           │
   │           ├─▶ ClientError ──────▶ Raise ConnectionError
   │           │
   │           ├─▶ TimeoutError ─────▶ Raise ConnectionError
   │           │
   │           └─▶ ParseError ────────▶ Raise HWGroupError
   │
   └─▶ Except
         │
         └─▶ Log Error & Return to Coordinator
               │
               └─▶ UpdateFailed ──▶ Shown in HA UI
```

---

This architecture provides:
- Clear separation of concerns
- Robust error handling
- Efficient data polling
- Easy maintenance and extensibility
- Standard Home Assistant patterns
