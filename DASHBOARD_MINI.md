# Mini Dashboard - Schnellstart

Für einen schnellen Start - ein vereinfachtes Dashboard mit den wichtigsten Funktionen.

## Installation in 2 Minuten

1. **Neues Dashboard erstellen:**
   - Einstellungen → Dashboards → "+ Dashboard hinzufügen"
   - Name: `HW Group Mini`
   - Icon: `mdi:server`

2. **YAML kopieren:**
   - Klicken Sie auf die 3 Punkte → "RAW-Konfigurationseditor"
   - Kopieren Sie den Code unten
   - Speichern

---

## Mini Dashboard YAML

```yaml
title: HW Group Mini
views:
  - title: Home
    cards:
      # Quick Status
      - type: glance
        title: 🖥️ Server Status
        show_name: true
        show_state: true
        columns: 3
        entities:
          - entity: sensor.izw_srv_rack_server
            name: Server
          - entity: sensor.izw_srv_rack_storage
            name: Storage
          - entity: binary_sensor.srv_izw_door
            name: Tür
      
      # SMS Gateway
      - type: glance
        title: 📱 SMS Gateway
        columns: 4
        entities:
          - entity: sensor.signal_quality
            name: Signal
          - entity: sensor.network_operator
            name: Provider
          - entity: sensor.sms_sent
            name: Gesendet
          - entity: sensor.sms_errors
            name: Fehler
      
      # Quick Actions
      - type: horizontal-stack
        cards:
          - type: button
            name: Test SMS
            icon: mdi:message
            tap_action:
              action: call-service
              service: hwgroup.send_sms
              service_data:
                phone_number: "+43676XXXXXXX"  # IHRE NUMMER!
                message: "Test von Home Assistant"
          
          - type: button
            name: Status SMS
            icon: mdi:file-document
            tap_action:
              action: call-service
              service: hwgroup.send_sms
              service_data:
                phone_number: "+43676XXXXXXX"  # IHRE NUMMER!
                message: >-
                  Server: {{ states('sensor.izw_srv_rack_server') }}°C
                  Storage: {{ states('sensor.izw_srv_rack_storage') }}°C
                  Signal: {{ states('sensor.signal_quality') }}%
          
          - type: button
            name: Anrufen
            icon: mdi:phone
            tap_action:
              action: call-service
              service: hwgroup.call_number
              service_data:
                phone_number: "+43676XXXXXXX"  # IHRE NUMMER!
      
      # Temperature Graph
      - type: history-graph
        title: 📊 Temperatur (24h)
        hours_to_show: 24
        refresh_interval: 60
        entities:
          - entity: sensor.izw_srv_rack_server
            name: Server
          - entity: sensor.izw_srv_rack_storage
            name: Storage
      
      # All Sensors
      - type: entities
        title: 📋 Alle Sensoren
        show_header_toggle: false
        entities:
          - sensor.izw_srv_rack_server
          - sensor.izw_srv_rack_storage
          - binary_sensor.srv_izw_door
          - binary_sensor.srv_izw_hum_back
          - binary_sensor.srv_izw_hum_front
          - sensor.signal_strength
          - sensor.signal_quality
          - sensor.network_operator
          - sensor.sms_sent
```

**⚠️ WICHTIG:** Ersetzen Sie `+43676XXXXXXX` mit Ihrer echten Telefonnummer!

---

## Was macht dieses Dashboard?

### Glance Cards
Zeigt die wichtigsten Werte auf einen Blick:
- **Server Temperaturen** - Beide Rack-Sensoren
- **Tür Status** - Ob offen oder geschlossen
- **SMS Gateway** - Signal, Provider, Statistiken

### Quick Action Buttons
**3 Buttons zum direkten Ausführen:**

1. **Test SMS** 📱
   - Sendet sofort eine Test-SMS an Ihre Nummer
   - Klicken = SMS wird versendet!

2. **Status SMS** 📊
   - Sendet aktuellen Server-Status per SMS
   - Enthält: Temperaturen + Signal-Qualität

3. **Anrufen** 📞
   - Ruft Ihre Nummer an (Ring + Auflegen)
   - Perfekt für stille Alarme

### History Graph
Zeigt Temperaturverlauf der letzten 24 Stunden

### Sensor Liste
Alle Sensoren übersichtlich aufgelistet

---

## Screenshots

```
┌────────────────────────────────┐
│ 🖥️ Server Status                │
│ ┌─────┐ ┌─────┐ ┌─────┐       │
│ │23.8°│ │20.9°│ │ ✅  │       │
│ │Serve│ │Stora│ │ Tür │       │
│ └─────┘ └─────┘ └─────┘       │
└────────────────────────────────┘

┌────────────────────────────────┐
│ 📱 SMS Gateway                  │
│ 61%   T-Mobile  6354    0      │
│ Signal Provider Gesend. Fehler │
└────────────────────────────────┘

┌────────────────────────────────┐
│ [Test SMS] [Status] [Anrufen] │
└────────────────────────────────┘

┌────────────────────────────────┐
│ 📊 Temperatur (24h)            │
│     [Linien-Grafik]            │
└────────────────────────────────┘
```

---

## Erweiterte Button-Optionen

### Button mit Bestätigung
```yaml
- type: button
  name: Alarm!
  icon: mdi:alert
  tap_action:
    action: call-service
    service: hwgroup.send_sms
    service_data:
      phone_number: "+43676XXXXXXX"
      message: "🚨 ALARM!"
    confirmation:
      text: "Wirklich Alarm-SMS senden?"
```

### Button mit Hold-Action
```yaml
- type: button
  name: SMS
  icon: mdi:message
  tap_action:
    action: more-info
  hold_action:
    action: call-service
    service: hwgroup.send_sms
    service_data:
      phone_number: "+43676XXXXXXX"
      message: "Test"
```
**Nutzung:** Kurz klicken = Details, Lang halten = SMS senden

### Button mit Conditional
```yaml
- type: conditional
  conditions:
    - entity: binary_sensor.srv_izw_door
      state: "on"
  card:
    type: button
    name: TÜR OFFEN!
    icon: mdi:door-open
    entity: binary_sensor.srv_izw_door
    tap_action:
      action: call-service
      service: hwgroup.send_sms
      service_data:
        phone_number: "+43676XXXXXXX"
        message: "Serverraum Tür ist offen!"
```
**Wird nur angezeigt wenn Tür offen ist!**

---

## Anpassungen

### Eigene Telefonnummer verwenden

**Option 1: Direkt im Button (wie oben)**
```yaml
phone_number: "+43676XXXXXXX"
```

**Option 2: Mit Input Helper**
1. Helper erstellen: `input_text.my_phone_number`
2. Im Button verwenden:
```yaml
phone_number: "{{ states('input_text.my_phone_number') }}"
```

### Mehrere Buttons für verschiedene Empfänger
```yaml
- type: horizontal-stack
  cards:
    - type: button
      name: An Admin
      icon: mdi:account
      tap_action:
        action: call-service
        service: hwgroup.send_sms
        service_data:
          phone_number: "+43676111111"
          message: "Admin Alert"
    
    - type: button
      name: An Chef
      icon: mdi:account-tie
      tap_action:
        action: call-service
        service: hwgroup.send_sms
        service_data:
          phone_number: "+43676222222"
          message: "Chef Alert"
```

### Button Farben ändern (mit card_mod)
```yaml
- type: button
  name: ALARM
  icon: mdi:alert
  card_mod:
    style: |
      ha-card {
        background-color: red;
        color: white;
      }
```

### Bedingte Nachricht
```yaml
- type: button
  name: Smart SMS
  icon: mdi:message-star
  tap_action:
    action: call-service
    service: hwgroup.send_sms
    service_data:
      phone_number: "+43676XXXXXXX"
      message: >-
        Status: {% if states('sensor.izw_srv_rack_server')|float > 30 %}
        🔥 KRITISCH
        {% elif states('sensor.izw_srv_rack_server')|float > 25 %}
        ⚠️ WARNUNG
        {% else %}
        ✅ OK
        {% endif %}
        Temp: {{ states('sensor.izw_srv_rack_server') }}°C
```

---

## Mobile App Optimierung

### Kompakte Ansicht für Handy
```yaml
# Für Smartphones besser lesbar
- type: vertical-stack
  cards:
    - type: glance
      columns: 2  # Nur 2 Spalten auf Mobile
      entities:
        - sensor.izw_srv_rack_server
        - sensor.izw_srv_rack_storage
    
    - type: vertical-stack  # Buttons untereinander statt nebeneinander
      cards:
        - type: button
          name: Test SMS
        - type: button
          name: Status SMS
        - type: button
          name: Anrufen
```

### Große Buttons für Touch
```yaml
- type: custom:button-card  # Benötigt HACS Button Card
  name: GROSS
  entity: sensor.signal_quality
  show_state: true
  styles:
    card:
      - height: 120px
      - font-size: 24px
    name:
      - font-size: 20px
```

---

## Tipps & Tricks

### 1. Dashboard als Standard setzen
- Einstellungen → Dashboards
- Bei "HW Group Mini" auf Stern klicken

### 2. Dashboard-Link teilen
- Dashboard öffnen
- URL kopieren: `http://homeassistant.local:8123/dashboard-hwgroup-mini`
- Als Lesezeichen speichern

### 3. Schnellzugriff auf Mobile
- Dashboard auf Smartphone öffnen
- "Zum Startbildschirm hinzufügen"
- Icon erscheint wie eine App

### 4. Kiosk-Modus (Vollbild)
URL mit Parameter:
```
http://homeassistant.local:8123/dashboard-hwgroup-mini?kiosk
```

### 5. Auto-Refresh
Dashboard aktualisiert sich automatisch alle 30 Sekunden.

---

## Häufige Fehler

**Button funktioniert nicht:**
- ✅ Überprüfen Sie die Telefonnummer
- ✅ HTTP GET im SMS Gateway aktiviert?
- ✅ Logs prüfen: Entwicklerwerkzeuge → Logs

**Sensoren nicht gefunden:**
- ✅ Entity-Namen überprüfen in: Entwicklerwerkzeuge → Zustände
- ✅ Sensoren existieren? Integration neu laden
- ✅ Groß-/Kleinschreibung beachten

**SMS kommt nicht an:**
- ✅ Signal Quality > 30%?
- ✅ Network Status = "Registered"?
- ✅ Test im Browser: `http://[IP]/values.xml?Cmd=SMS&Nmr=NUMMER&Text=Test`

**Zu viele SMS werden gesendet:**
- Button-Spam vermeiden: Confirmation hinzufügen
- Automation mit Bedingungen verwenden
- Rate Limiting einbauen

---

## Nächste Schritte

Nach dem Mini-Dashboard:

1. **Fügen Sie Automationen hinzu** aus [SMS_SERVICES.md](SMS_SERVICES.md)

2. **Erweitern Sie auf Vollversion** mit [DASHBOARD.md](DASHBOARD.md)

3. **Erstellen Sie Alarme** mit Input Helpers

4. **Optimieren Sie für Ihre Bedürfnisse**

---

## Support

Bei Fragen:
- Siehe [SMS_QUICKSTART.md](SMS_QUICKSTART.md) für Setup
- Siehe [SMS_SERVICES.md](SMS_SERVICES.md) für Beispiele
- Siehe [TROUBLESHOOTING.md](TROUBLESHOOTING.md) für Probleme

**Viel Erfolg! 🚀**
