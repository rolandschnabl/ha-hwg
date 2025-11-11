# Dashboard Vorlage für HW Group Integration

Diese Dashboard-Vorlage zeigt alle Sensoren und SMS-Funktionalität übersichtlich an.

## Installation

### Methode 1: YAML Dashboard (Empfohlen)

1. Gehen Sie zu **Einstellungen** → **Dashboards**
2. Klicken Sie auf **+ DASHBOARD HINZUFÜGEN**
3. Wählen Sie **Neue Dashboard hinzufügen**
4. Name: `HW Group Monitoring`
5. Icon: `mdi:server-network`
6. Klicken Sie auf die **3 Punkte** → **RAW-KONFIGURATIONSEDITOR**
7. Kopieren Sie den YAML-Code unten
8. Klicken Sie auf **SPEICHERN**

### Methode 2: UI-basiert

Folgen Sie der Schritt-für-Schritt Anleitung am Ende dieses Dokuments.

---

## YAML Dashboard Code

```yaml
title: HW Group Monitoring
views:
  - title: Übersicht
    path: overview
    icon: mdi:view-dashboard
    badges: []
    cards:
      # Header Card
      - type: markdown
        content: |
          # 🖥️ HW Group Monitoring Dashboard
          Überwachung aller Poseidon Geräte und SMS Gateway
          
          **Status**: {{'\u2705' if states('binary_sensor.srv_izw_door') == 'off' else '\u274c'}} Serverraum sicher
      
      # Poseidon Geräte - Temperaturen
      - type: vertical-stack
        cards:
          - type: markdown
            content: |
              ## 🌡️ Temperatur Überwachung
          
          - type: horizontal-stack
            cards:
              - type: gauge
                entity: sensor.izw_srv_rack_server
                name: Rack Server
                min: 0
                max: 40
                severity:
                  green: 0
                  yellow: 25
                  red: 30
                needle: true
              
              - type: gauge
                entity: sensor.izw_srv_rack_storage
                name: Rack Storage
                min: 0
                max: 40
                severity:
                  green: 0
                  yellow: 25
                  red: 30
                needle: true
          
          - type: history-graph
            title: Temperatur Verlauf (24h)
            entities:
              - entity: sensor.izw_srv_rack_server
                name: Server
              - entity: sensor.izw_srv_rack_storage
                name: Storage
            hours_to_show: 24
            refresh_interval: 60
      
      # Binary Sensors - Sicherheit
      - type: vertical-stack
        cards:
          - type: markdown
            content: |
              ## 🚪 Sicherheit & Status
          
          - type: entities
            title: Eingänge & Sensoren
            show_header_toggle: false
            entities:
              - entity: binary_sensor.srv_izw_door
                name: Serverraum Tür
                icon: mdi:door
                secondary_info: last-changed
              
              - entity: binary_sensor.srv_izw_hum_back
                name: Feuchtigkeit Hinten
                icon: mdi:water-percent
                secondary_info: last-changed
              
              - entity: binary_sensor.srv_izw_hum_front
                name: Feuchtigkeit Vorne
                icon: mdi:water-percent
                secondary_info: last-changed
              
              - entity: binary_sensor.binary_4
                name: Binary Eingang 4
                icon: mdi:electric-switch
                secondary_info: last-changed
              
              - entity: binary_sensor.comm_monitor_1
                name: Kommunikation Monitor
                icon: mdi:network
                secondary_info: last-changed
          
          - type: conditional
            conditions:
              - entity: binary_sensor.srv_izw_door
                state: "on"
            card:
              type: markdown
              content: |
                ### ⚠️ WARNUNG
                **Serverraum Tür ist offen!**
                Bitte überprüfen und schließen.
              card_mod:
                style: |
                  ha-card {
                    background-color: rgba(255, 152, 0, 0.2);
                    border: 2px solid orange;
                  }
      
      # SMS Gateway Status
      - type: vertical-stack
        cards:
          - type: markdown
            content: |
              ## 📱 SMS Gateway Status
          
          - type: glance
            title: Mobilfunk Signal
            show_name: true
            show_state: true
            entities:
              - entity: sensor.signal_strength
                name: Signalstärke
                icon: mdi:signal-cellular-3
              
              - entity: sensor.signal_quality
                name: Qualität
                icon: mdi:signal
              
              - entity: sensor.network_operator
                name: Provider
                icon: mdi:cellphone
              
              - entity: sensor.network_status
                name: Status
                icon: mdi:network
          
          - type: entities
            title: SMS Statistiken
            show_header_toggle: false
            entities:
              - entity: sensor.sms_sent
                name: SMS Gesendet
                icon: mdi:message-check
                secondary_info: last-changed
              
              - entity: sensor.sms_errors
                name: SMS Fehler
                icon: mdi:message-alert
                secondary_info: last-changed
          
          - type: horizontal-stack
            cards:
              - type: gauge
                entity: sensor.signal_quality
                name: Signal Qualität
                min: 0
                max: 100
                severity:
                  green: 50
                  yellow: 30
                  red: 0
                unit: "%"
                needle: true
              
              - type: gauge
                entity: sensor.signal_strength
                name: Signal Stärke
                min: -110
                max: -50
                severity:
                  red: -110
                  yellow: -85
                  green: -70
                unit: dBm
                needle: true

  # SMS Senden Tab
  - title: SMS Senden
    path: sms
    icon: mdi:message-text
    badges: []
    cards:
      - type: markdown
        content: |
          # 📱 SMS & Anrufe
          Versenden Sie SMS-Nachrichten oder rufen Sie Nummern an.
          
          **Signal Status**: {{ states('sensor.network_status') }}
          **Provider**: {{ states('sensor.network_operator') }}
          **Qualität**: {{ states('sensor.signal_quality') }}%
      
      # Quick Actions
      - type: vertical-stack
        cards:
          - type: markdown
            content: |
              ## ⚡ Schnellaktionen
          
          - type: horizontal-stack
            cards:
              - type: button
                name: Test SMS
                icon: mdi:message-text-outline
                tap_action:
                  action: call-service
                  service: script.send_test_sms
                  service_data: {}
                hold_action:
                  action: none
              
              - type: button
                name: Status Report
                icon: mdi:file-document
                tap_action:
                  action: call-service
                  service: script.send_status_report
                  service_data: {}
                hold_action:
                  action: none
              
              - type: button
                name: Test Anruf
                icon: mdi:phone
                tap_action:
                  action: call-service
                  service: script.test_call
                  service_data: {}
                hold_action:
                  action: none
      
      # Manual SMS Form
      - type: entities
        title: 📝 Manuelle SMS senden
        show_header_toggle: false
        entities:
          - type: attribute
            entity: sensor.network_operator
            attribute: friendly_name
            name: SMS Gateway
            icon: mdi:cellphone-check
          
          - type: conditional
            conditions:
              - entity: sensor.signal_quality
                state_not: "unavailable"
            row:
              type: section
              label: "Signal: {{states('sensor.signal_quality')}}%"
      
      - type: markdown
        content: |
          ### 📝 SMS manuell senden
          
          Verwenden Sie **Entwicklerwerkzeuge** → **Dienste** um eine SMS zu senden:
          
          ```yaml
          service: hwgroup.send_sms
          data:
            phone_number: "+43676XXXXXXX"
            message: "Ihre Nachricht hier"
          ```
          
          Oder erstellen Sie ein Script (siehe unten).
      
      # SMS History
      - type: vertical-stack
        cards:
          - type: markdown
            content: |
              ## 📊 SMS Statistik
          
          - type: history-graph
            title: SMS Verlauf
            entities:
              - entity: sensor.sms_sent
                name: Gesendet
              - entity: sensor.sms_errors
                name: Fehler
            hours_to_show: 168
            refresh_interval: 300

  # Alarme & Automationen
  - title: Alarme
    path: alarms
    icon: mdi:bell-alert
    badges: []
    cards:
      - type: markdown
        content: |
          # 🚨 Alarm Konfiguration
          Übersicht der aktiven Automationen und Alarme
      
      - type: vertical-stack
        cards:
          - type: markdown
            content: |
              ## 🌡️ Temperatur Alarme
          
          - type: entities
            title: Temperatur Schwellwerte
            show_header_toggle: false
            entities:
              - type: custom:slider-entity-row
                entity: input_number.temp_warning_threshold
                name: Warnung
                icon: mdi:thermometer-alert
              
              - type: custom:slider-entity-row
                entity: input_number.temp_critical_threshold
                name: Kritisch
                icon: mdi:thermometer-high
      
      - type: vertical-stack
        cards:
          - type: markdown
            content: |
              ## 📱 SMS Empfänger
          
          - type: entities
            title: Benachrichtigungs-Nummern
            show_header_toggle: false
            entities:
              - entity: input_text.sms_primary_number
                name: Primäre Nummer
                icon: mdi:phone
              
              - entity: input_text.sms_secondary_number
                name: Sekundäre Nummer
                icon: mdi:phone-plus
              
              - entity: input_boolean.enable_sms_alarms
                name: SMS Alarme aktiviert
                icon: mdi:bell
      
      - type: vertical-stack
        cards:
          - type: markdown
            content: |
              ## 🔔 Aktive Automationen
          
          - type: entities
            title: Automation Status
            show_header_toggle: false
            entities:
              - entity: automation.temperatur_alarm_sms
                name: Temperatur Alarm
                secondary_info: last-triggered
              
              - entity: automation.serverraum_tur_alarm
                name: Tür Alarm
                secondary_info: last-triggered
              
              - entity: automation.taglicher_server_status
                name: Täglicher Report
                secondary_info: last-triggered
              
              - entity: automation.kritischer_server_alarm
                name: Kritischer Alarm
                secondary_info: last-triggered
              
              - entity: automation.ha_neustart_benachrichtigung
                name: HA Neustart
                secondary_info: last-triggered

  # System Info
  - title: System
    path: system
    icon: mdi:information
    badges: []
    cards:
      - type: markdown
        content: |
          # ℹ️ System Information
          Details zu allen HW Group Geräten
      
      # Device Cards
      - type: vertical-stack
        cards:
          - type: markdown
            content: |
              ## 🖥️ Poseidon Geräte
          
          - type: entities
            title: IZW03-MON-SRV (192.168.150.21)
            show_header_toggle: false
            entities:
              - type: attribute
                entity: sensor.izw_srv_rack_server
                attribute: device_class
                name: Gerät Typ
              
              - type: section
                label: "Temperatur Sensoren"
              
              - entity: sensor.izw_srv_rack_server
                name: Rack Server
                secondary_info: last-updated
              
              - entity: sensor.izw_srv_rack_storage
                name: Rack Storage
                secondary_info: last-updated
              
              - type: section
                label: "Binär Eingänge"
              
              - entity: binary_sensor.srv_izw_door
                name: Tür
              
              - entity: binary_sensor.srv_izw_hum_back
                name: Feuchtigkeit Hinten
              
              - entity: binary_sensor.srv_izw_hum_front
                name: Feuchtigkeit Vorne
      
      - type: vertical-stack
        cards:
          - type: markdown
            content: |
              ## 📱 SMS Gateway
          
          - type: entities
            title: HWg-SMS-GW3 (192.168.150.9)
            show_header_toggle: false
            entities:
              - type: attribute
                entity: sensor.signal_strength
                attribute: friendly_name
                name: Gerät
              
              - type: section
                label: "Mobilfunk"
              
              - entity: sensor.signal_strength
                name: Signalstärke
                secondary_info: last-updated
              
              - entity: sensor.signal_quality
                name: Signalqualität
                secondary_info: last-updated
              
              - entity: sensor.network_operator
                name: Provider
                secondary_info: last-updated
              
              - entity: sensor.network_status
                name: Netzwerk Status
                secondary_info: last-updated
              
              - type: section
                label: "Statistiken"
              
              - entity: sensor.sms_sent
                name: SMS Gesendet
                secondary_info: last-updated
              
              - entity: sensor.sms_errors
                name: SMS Fehler
                secondary_info: last-updated
      
      - type: markdown
        content: |
          ## 📖 Dokumentation
          
          - [SMS Services Dokumentation](https://github.com/rolandschnabl/ha-hwg/blob/main/SMS_SERVICES.md)
          - [SMS Schnellstart](https://github.com/rolandschnabl/ha-hwg/blob/main/SMS_QUICKSTART.md)
          - [Changelog](https://github.com/rolandschnabl/ha-hwg/blob/main/CHANGELOG.md)
          
          **Version**: 1.1.0
```

---

## Benötigte Helper & Scripts

### Helper (Einstellungen → Geräte & Dienste → Helper)

Erstellen Sie folgende Helper:

#### 1. Input Numbers (Zahlen)

**Temperatur Warnung:**
- Name: `Temperatur Warnung Schwellwert`
- Entity ID: `input_number.temp_warning_threshold`
- Minimum: 20
- Maximum: 40
- Schritt: 0.5
- Einheit: °C
- Initial: 28

**Temperatur Kritisch:**
- Name: `Temperatur Kritisch Schwellwert`
- Entity ID: `input_number.temp_critical_threshold`
- Minimum: 25
- Maximum: 50
- Schritt: 0.5
- Einheit: °C
- Initial: 35

#### 2. Input Text (Texteingabe)

**Primäre SMS Nummer:**
- Name: `SMS Primäre Nummer`
- Entity ID: `input_text.sms_primary_number`
- Modus: Text
- Initial: `+43676XXXXXXX`

**Sekundäre SMS Nummer:**
- Name: `SMS Sekundäre Nummer`
- Entity ID: `input_text.sms_secondary_number`
- Modus: Text
- Initial: `+43676YYYYYYY`

#### 3. Input Boolean (Schalter)

**SMS Alarme aktivieren:**
- Name: `SMS Alarme aktiviert`
- Entity ID: `input_boolean.enable_sms_alarms`
- Initial: Ein

---

## Scripts für Quick Actions

Fügen Sie diese Scripts in Ihre `configuration.yaml` oder `scripts.yaml` ein:

```yaml
script:
  send_test_sms:
    alias: "Test SMS senden"
    sequence:
      - service: hwgroup.send_sms
        data:
          phone_number: "{{ states('input_text.sms_primary_number') }}"
          message: >-
            🧪 Test SMS von Home Assistant
            Zeit: {{ now().strftime('%H:%M:%S') }}
            Datum: {{ now().strftime('%d.%m.%Y') }}
    mode: single
    icon: mdi:message-text-outline

  send_status_report:
    alias: "Status Report per SMS"
    sequence:
      - service: hwgroup.send_sms
        data:
          phone_number: "{{ states('input_text.sms_primary_number') }}"
          message: >-
            📊 Server Status {{ now().strftime('%d.%m %H:%M') }}
            
            🌡️ Temperaturen:
            Server: {{ states('sensor.izw_srv_rack_server') }}°C
            Storage: {{ states('sensor.izw_srv_rack_storage') }}°C
            
            🚪 Tür: {{ 'Offen' if is_state('binary_sensor.srv_izw_door', 'on') else 'Geschlossen' }}
            
            📱 Signal: {{ states('sensor.signal_quality') }}%
    mode: single
    icon: mdi:file-document

  test_call:
    alias: "Test Anruf"
    sequence:
      - service: hwgroup.call_number
        data:
          phone_number: "{{ states('input_text.sms_primary_number') }}"
    mode: single
    icon: mdi:phone

  send_alarm_sms:
    alias: "Alarm SMS senden"
    fields:
      message:
        description: Alarm Nachricht
        example: "Server Temperatur kritisch!"
    sequence:
      - condition: state
        entity_id: input_boolean.enable_sms_alarms
        state: "on"
      
      - service: hwgroup.send_sms
        data:
          phone_number: "{{ states('input_text.sms_primary_number') }}"
          message: "🚨 ALARM: {{ message }}"
      
      - delay:
          seconds: 5
      
      - condition: template
        value_template: "{{ states('input_text.sms_secondary_number') != 'unavailable' }}"
      
      - service: hwgroup.send_sms
        data:
          phone_number: "{{ states('input_text.sms_secondary_number') }}"
          message: "🚨 ALARM: {{ message }}"
    mode: queued
    icon: mdi:bell-alert
```

---

## Automationen (optional)

Beispiel-Automationen die mit dem Dashboard funktionieren:

```yaml
automation:
  - alias: "Temperatur Alarm SMS"
    description: "SMS bei Überschreitung des Schwellwerts"
    trigger:
      - platform: template
        value_template: >-
          {{ states('sensor.izw_srv_rack_server') | float(0) > 
             states('input_number.temp_warning_threshold') | float(30) }}
    condition:
      - condition: state
        entity_id: input_boolean.enable_sms_alarms
        state: "on"
    action:
      - service: script.send_alarm_sms
        data:
          message: >-
            Serverraum Temperatur zu hoch!
            Server: {{ states('sensor.izw_srv_rack_server') }}°C
            Schwellwert: {{ states('input_number.temp_warning_threshold') }}°C
    mode: single

  - alias: "Kritischer Server Alarm"
    description: "Mehrfache Benachrichtigung bei kritischer Temperatur"
    trigger:
      - platform: template
        value_template: >-
          {{ states('sensor.izw_srv_rack_server') | float(0) > 
             states('input_number.temp_critical_threshold') | float(35) }}
    condition:
      - condition: state
        entity_id: input_boolean.enable_sms_alarms
        state: "on"
    action:
      # SMS senden
      - service: script.send_alarm_sms
        data:
          message: >-
            KRITISCH! Server {{ states('sensor.izw_srv_rack_server') }}°C
      
      # Anruf
      - service: hwgroup.call_number
        data:
          phone_number: "{{ states('input_text.sms_primary_number') }}"
      
      # Nochmal nach 1 Minute
      - delay:
          minutes: 1
      
      - service: script.send_alarm_sms
        data:
          message: >-
            KRITISCH! Server immer noch {{ states('sensor.izw_srv_rack_server') }}°C
    mode: single
```

---

## UI-basierte Installation (Schritt-für-Schritt)

Wenn Sie lieber die UI verwenden statt YAML:

### 1. Neues Dashboard erstellen
1. **Einstellungen** → **Dashboards** → **+ DASHBOARD HINZUFÜGEN**
2. Name: `HW Group Monitoring`
3. Icon: `mdi:server-network`

### 2. Übersichts-Tab erstellen
1. Neuen Tab hinzufügen: "Übersicht"
2. Icon: `mdi:view-dashboard`

### 3. Karten hinzufügen

**Markdown Header:**
- Karte hinzufügen → Markdown
- Inhalt: `# 🖥️ HW Group Monitoring Dashboard`

**Temperatur Gauges:**
- Karte hinzufügen → Gauge
- Entity: `sensor.izw_srv_rack_server`
- Minimum: 0, Maximum: 40
- Schwellwerte: Grün 0, Gelb 25, Rot 30

**History Graph:**
- Karte hinzufügen → History Graph
- Entities: Beide Temperatur-Sensoren
- Stunden: 24

**Binary Sensors:**
- Karte hinzufügen → Entities
- Alle Binary Sensoren hinzufügen
- `secondary_info: last-changed` setzen

**SMS Gateway Status:**
- Karte hinzufügen → Glance
- Alle SMS Gateway Sensoren hinzufügen

### 4. SMS Tab erstellen
1. Neuen Tab: "SMS Senden"
2. Icon: `mdi:message-text`
3. Button Karten für Quick Actions erstellen
4. Markdown mit Anleitung hinzufügen

### 5. Helper erstellen
1. **Einstellungen** → **Geräte & Dienste** → **Helper**
2. Alle oben genannten Helper erstellen

### 6. Scripts erstellen
1. **Einstellungen** → **Automationen & Szenen** → **Scripts**
2. Die 4 Scripts von oben erstellen

---

## Screenshots Beispiele

So sollte Ihr Dashboard aussehen:

### Übersicht Tab
```
┌─────────────────────────────────────────┐
│  🖥️ HW Group Monitoring Dashboard      │
│  Status: ✅ Serverraum sicher            │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  🌡️ Temperatur Überwachung              │
│  ┌──────────┐  ┌──────────┐            │
│  │  23.8°C  │  │  20.9°C  │            │
│  │  Server  │  │ Storage  │            │
│  └──────────┘  └──────────┘            │
│  [Verlauf Grafik über 24h]             │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  🚪 Sicherheit & Status                 │
│  ✅ Serverraum Tür: Geschlossen         │
│  ✅ Feuchtigkeit Hinten: Normal         │
│  ✅ Feuchtigkeit Vorne: Normal          │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  📱 SMS Gateway Status                  │
│  📶 -75 dBm  📊 61%  📱 T-Mobile       │
│  ✉️ 6354 gesendet  ❌ 0 Fehler         │
└─────────────────────────────────────────┘
```

### SMS Tab
```
┌─────────────────────────────────────────┐
│  📱 SMS & Anrufe                        │
│  Signal: Registered | Provider: T-Mobile│
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  ⚡ Schnellaktionen                      │
│  [Test SMS] [Status Report] [Anruf]    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  📝 Manuelle SMS senden                 │
│  Verwenden Sie Entwicklerwerkzeuge...   │
└─────────────────────────────────────────┘
```

---

## Anpassungen

### Farben ändern
Fügen Sie Card-Mod hinzu (HACS Integration erforderlich):
```yaml
card_mod:
  style: |
    ha-card {
      background-color: rgba(0, 150, 255, 0.1);
      border: 1px solid #0096ff;
    }
```

### Mehr Geräte hinzufügen
Kopieren Sie einfach die Entity-Karten und passen Sie die Sensor-Namen an.

### Mobile-Optimierung
Das Dashboard ist bereits für Mobilgeräte optimiert. Für noch bessere Mobile-Ansicht verwenden Sie:
- `type: vertical-stack` für übereinander
- `type: horizontal-stack` für nebeneinander (max 2-3 Karten)

---

## Fehlerbehebung

**Karten werden nicht angezeigt:**
- Überprüfen Sie Entity-Namen in Entwicklerwerkzeuge → Zustände
- Passen Sie Entity-IDs im YAML an Ihre Sensoren an

**Quick Action Buttons funktionieren nicht:**
- Erstellen Sie zuerst die Scripts
- Starten Sie Home Assistant neu

**Helper nicht verfügbar:**
- Erstellen Sie die Input Helper in den Einstellungen
- Starten Sie Home Assistant neu

---

## Erweiterte Features

### Conditional Cards
Zeigen Sie Karten nur unter bestimmten Bedingungen:
```yaml
type: conditional
conditions:
  - entity: binary_sensor.srv_izw_door
    state: "on"
card:
  type: markdown
  content: "⚠️ TÜR OFFEN!"
```

### Badges oben
Fügen Sie wichtige Infos als Badges hinzu:
```yaml
badges:
  - entity: sensor.izw_srv_rack_server
  - entity: binary_sensor.srv_izw_door
  - entity: sensor.signal_quality
```

### Auto-Entities
Mit HACS Auto-Entities alle HW Group Sensoren automatisch anzeigen:
```yaml
type: custom:auto-entities
card:
  type: entities
  title: Alle HW Group Sensoren
filter:
  include:
    - domain: sensor
      attributes:
        device_class: temperature
    - domain: binary_sensor
```

---

**Viel Erfolg mit Ihrem Dashboard! 📊**
