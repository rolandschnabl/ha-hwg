# SMS Gateway Services

Die HW Group Integration bietet zwei Services zum Versenden von SMS und Anrufen über das HWg-SMS-GW3 Gateway.

## Verfügbare Services

### 1. `hwgroup.send_sms` - SMS versenden

Sendet eine SMS über das SMS Gateway.

**Parameter:**
- `phone_number` (erforderlich): Empfänger-Telefonnummer im internationalen Format (empfohlen: `+43676123456` oder `00436761234567`)
- `message` (erforderlich): SMS-Text (max. 160 Zeichen)
- `device_id` (optional): Device ID wenn Sie mehrere SMS Gateways haben

**Beispiel Service-Aufruf:**
```yaml
service: hwgroup.send_sms
data:
  phone_number: "+43676123456"
  message: "Test SMS von Home Assistant"
```

---

### 2. `hwgroup.call_number` - Telefonnummer anrufen

Ruft eine Telefonnummer an (das Telefon klingelt einmal und legt dann auf). Nützlich für stille Alarme.

**Parameter:**
- `phone_number` (erforderlich): Telefonnummer im internationalen Format
- `device_id` (optional): Device ID wenn Sie mehrere SMS Gateways haben

**Beispiel Service-Aufruf:**
```yaml
service: hwgroup.call_number
data:
  phone_number: "+43676123456"
```

---

## Beispiel-Automationen

### 1. Temperatur-Alarm per SMS

Sendet eine SMS wenn die Serverraum-Temperatur zu hoch ist:

```yaml
automation:
  - alias: "Serverraum Temperatur Alarm"
    description: "SMS bei zu hoher Temperatur"
    trigger:
      - platform: numeric_state
        entity_id: sensor.izw_srv_rack_server
        above: 28
    action:
      - service: hwgroup.send_sms
        data:
          phone_number: "+43676123456"
          message: >-
            ALARM: Serverraum Temperatur zu hoch!
            Aktuell: {{ states('sensor.izw_srv_rack_server') }}°C
            Zeit: {{ now().strftime('%H:%M:%S') }}
```

### 2. Tür-Alarm per Anruf

Ruft an wenn die Tür geöffnet wird:

```yaml
automation:
  - alias: "Serverraum Tür Alarm"
    description: "Anruf bei geöffneter Tür"
    trigger:
      - platform: state
        entity_id: binary_sensor.srv_izw_door
        to: "on"
    action:
      - service: hwgroup.call_number
        data:
          phone_number: "+43676123456"
      - delay:
          seconds: 5
      - service: hwgroup.send_sms
        data:
          phone_number: "+43676123456"
          message: "ALARM: Serverraum Tür wurde geöffnet!"
```

### 3. Täglicher Status-Report per SMS

Sendet täglich um 8:00 Uhr einen Status-Report:

```yaml
automation:
  - alias: "Täglicher Server Status"
    description: "SMS mit allen Sensor-Werten"
    trigger:
      - platform: time
        at: "08:00:00"
    action:
      - service: hwgroup.send_sms
        data:
          phone_number: "+43676123456"
          message: >-
            Server Status {{ now().strftime('%d.%m.%Y') }}:
            Rack-Server: {{ states('sensor.izw_srv_rack_server') }}°C
            Rack-Storage: {{ states('sensor.izw_srv_rack_storage') }}°C
            Tür: {{ states('binary_sensor.srv_izw_door') }}
```

### 4. Kritischer Alarm mit mehrfacher Benachrichtigung

Sendet SMS und ruft an bei kritischen Problemen:

```yaml
automation:
  - alias: "Kritischer Server Alarm"
    description: "Mehrfache Benachrichtigung bei kritischen Werten"
    trigger:
      - platform: numeric_state
        entity_id: sensor.izw_srv_rack_server
        above: 35
    action:
      # Erste SMS
      - service: hwgroup.send_sms
        data:
          phone_number: "+43676123456"
          message: "KRITISCH! Server {{ states('sensor.izw_srv_rack_server') }}°C"
      # Anruf
      - service: hwgroup.call_number
        data:
          phone_number: "+43676123456"
      - delay:
          seconds: 10
      # Zweite SMS mit mehr Details
      - service: hwgroup.send_sms
        data:
          phone_number: "+43676123456"
          message: >-
            KRITISCHER ALARM!
            Server: {{ states('sensor.izw_srv_rack_server') }}°C
            Storage: {{ states('sensor.izw_srv_rack_storage') }}°C
            Sofortige Aktion erforderlich!
```

### 5. Home Assistant Neustart-Benachrichtigung

Sendet SMS wenn Home Assistant gestartet wird:

```yaml
automation:
  - alias: "HA Neustart Benachrichtigung"
    description: "SMS bei Home Assistant Start"
    trigger:
      - platform: homeassistant
        event: start
    action:
      - delay:
          seconds: 30
      - service: hwgroup.send_sms
        data:
          phone_number: "+43676123456"
          message: "Home Assistant wurde neu gestartet um {{ now().strftime('%H:%M:%S') }}"
```

### 6. Netzwerk-Status Überwachung

Benachrichtigt bei schlechtem Mobilfunk-Signal:

```yaml
automation:
  - alias: "SMS Gateway Signal Warnung"
    description: "Warnung bei schwachem Signal"
    trigger:
      - platform: numeric_state
        entity_id: sensor.signal_quality
        below: 30
    action:
      - service: persistent_notification.create
        data:
          title: "SMS Gateway Signal schwach"
          message: >-
            Signal Qualität: {{ states('sensor.signal_quality') }}%
            Signal Stärke: {{ states('sensor.signal_strength') }} dBm
            Operator: {{ states('sensor.network_operator') }}
```

### 7. SMS an mehrere Empfänger

Sendet die gleiche SMS an mehrere Personen:

```yaml
automation:
  - alias: "Alarm an mehrere Empfänger"
    description: "SMS an mehrere Nummern"
    trigger:
      - platform: state
        entity_id: binary_sensor.srv_izw_door
        to: "on"
    action:
      - repeat:
          for_each:
            - "+43676111111"
            - "+43676222222"
            - "+43676333333"
          sequence:
            - service: hwgroup.send_sms
              data:
                phone_number: "{{ repeat.item }}"
                message: "ALARM: Serverraum Tür geöffnet!"
            - delay:
                seconds: 2
```

### 8. SMS mit Sensor-Historie

Sendet SMS mit Durchschnittswert der letzten Stunde:

```yaml
automation:
  - alias: "Stündlicher Temperatur-Report"
    description: "SMS mit Durchschnittswerten"
    trigger:
      - platform: time_pattern
        hours: "/1"
    action:
      - service: hwgroup.send_sms
        data:
          phone_number: "+43676123456"
          message: >-
            Temp Report {{ now().strftime('%H:%M') }}
            Server: {{ state_attr('sensor.izw_srv_rack_server', 'mean') | default(states('sensor.izw_srv_rack_server')) }}°C
            Max: {{ state_attr('sensor.izw_srv_rack_server', 'max_value') | default('N/A') }}°C
```

---

## Tipps & Best Practices

### Telefonnummern-Format
- **Empfohlen**: `+43676123456` (internationales Format mit +)
- **Alternative**: `00436761234567` (internationales Format mit 00)
- **Nicht empfohlen**: `0676123456` (nationales Format, funktioniert nur lokal)

### SMS-Länge
- Maximale Länge: **160 Zeichen**
- Längere Nachrichten werden als mehrere SMS versendet
- Sonderzeichen (ä, ö, ü) können die Länge reduzieren

### Rate Limiting
- Vermeiden Sie zu viele SMS in kurzer Zeit
- Fügen Sie `delay` zwischen mehreren SMS ein
- Verwenden Sie `condition` um Spam zu vermeiden

### Fehlerbehandlung
```yaml
action:
  - service: hwgroup.send_sms
    data:
      phone_number: "+43676123456"
      message: "Test"
    continue_on_error: true
  - service: persistent_notification.create
    data:
      message: "SMS wurde versendet (oder fehlgeschlagen)"
```

### Kosten sparen
- Verwenden Sie `hwgroup.call_number` statt SMS wenn möglich (günstiger)
- Gruppieren Sie Benachrichtigungen
- Nutzen Sie Zeitfenster und Bedingungen

### Mehrere SMS Gateways
Wenn Sie mehrere SMS Gateways haben, können Sie die `device_id` angeben:

```yaml
action:
  - service: hwgroup.send_sms
    data:
      device_id: "01K9PC2VMZ7G6G4CZM15FFTF0G"
      phone_number: "+43676123456"
      message: "Test"
```

---

## Verfügbare SMS Gateway Sensoren

Das SMS Gateway stellt folgende Sensoren zur Verfügung:

1. **Signal Strength** (`sensor.signal_strength`)
   - Signalstärke in dBm
   - Typische Werte: -50 bis -110 dBm
   - Je höher (näher an 0), desto besser

2. **Signal Quality** (`sensor.signal_quality`)
   - Signalqualität in Prozent
   - 0-100%

3. **Network Operator** (`sensor.network_operator`)
   - Name des Mobilfunkanbieters
   - z.B. "T-Mobile Austria"

4. **Network Status** (`sensor.network_status`)
   - Registrierungsstatus im Netz
   - z.B. "Registered, home network"

5. **SMS Sent** (`sensor.sms_sent`)
   - Anzahl erfolgreich gesendeter SMS
   - Zähler seit letztem Reset

6. **SMS Errors** (`sensor.sms_errors`)
   - Anzahl fehlgeschlagener SMS
   - Sollte idealerweise 0 sein

---

## Fehlerbehebung

### SMS kommt nicht an
1. Überprüfen Sie das Telefonnummern-Format
2. Prüfen Sie den Network Status Sensor
3. Kontrollieren Sie die Signal Quality (sollte >30% sein)
4. Überprüfen Sie Home Assistant Logs: `ha core logs | grep hwgroup`

### Service nicht verfügbar
1. Stellen Sie sicher, dass das SMS Gateway in Home Assistant konfiguriert ist
2. Überprüfen Sie, ob `services.yaml` vorhanden ist
3. Starten Sie Home Assistant neu

### Authentifizierungsfehler
1. Überprüfen Sie Username/Password in der Integration
2. Stellen Sie sicher, dass HTTP GET im SMS Gateway aktiviert ist
3. Gateway-Konfiguration: GSM Modem → "Enable HTTP GET for sending SMS"

---

## Weiterführende Links

- [HW Group SMS Gateway Dokumentation](https://www.hw-group.com/support/how-to-send-sms-via-hwg-sms-gw3)
- [HWg-SMS-GW3 Produkt](https://www.hw-group.com/accessory/sms-gw3)
- [Home Assistant Automation Dokumentation](https://www.home-assistant.io/docs/automation/)
