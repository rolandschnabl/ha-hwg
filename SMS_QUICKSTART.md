# SMS Schnellstart-Anleitung

## Erste SMS in 5 Minuten versenden! 📱

### Schritt 1: SMS Gateway Konfiguration überprüfen

1. Gehen Sie zu **Einstellungen** → **Geräte & Dienste**
2. Suchen Sie nach "HW Group" Integration
3. Klicken Sie auf das SMS Gateway Gerät
4. Überprüfen Sie die Sensoren:
   - ✅ **Signal Quality** sollte > 30% sein
   - ✅ **Network Status** sollte "Registered" zeigen
   - ✅ **Network Operator** sollte Ihren Provider anzeigen

### Schritt 2: HTTP GET im Gateway aktivieren

⚠️ **Wichtig**: HTTP GET muss im SMS Gateway aktiviert sein!

1. Öffnen Sie die Web-Oberfläche des SMS Gateways: `http://[IP-ADRESSE]`
2. Gehen Sie zum Tab **GSM Modem**
3. Aktivieren Sie: ☑️ **"Enable HTTP GET for sending SMS"**
4. Speichern Sie die Einstellungen

### Schritt 3: Test-SMS über Entwicklerwerkzeuge senden

1. Gehen Sie zu **Entwicklerwerkzeuge** → **Dienste**
2. Wählen Sie den Dienst: `hwgroup.send_sms`
3. Geben Sie folgende Daten ein:

```yaml
service: hwgroup.send_sms
data:
  phone_number: "+43676XXXXXXX"  # Ihre Nummer!
  message: "Test SMS von Home Assistant!"
```

4. Klicken Sie auf **DIENST AUFRUFEN**
5. Überprüfen Sie Ihr Telefon - die SMS sollte in 10-30 Sekunden ankommen! 📲

### Schritt 4: Erste Automation erstellen

Jetzt erstellen wir eine einfache Automation, die eine SMS bei Problemen sendet.

#### Beispiel: Temperatur-Alarm

1. Gehen Sie zu **Einstellungen** → **Automationen & Szenen**
2. Klicken Sie auf **+ AUTOMATION ERSTELLEN**
3. Wählen Sie **Leere Automation erstellen**
4. Fügen Sie folgenden YAML-Code ein (oder verwenden Sie die UI):

```yaml
alias: Temperatur Alarm SMS
description: SMS bei zu hoher Serverraum-Temperatur
trigger:
  - platform: numeric_state
    entity_id: sensor.izw_srv_rack_server
    above: 28
action:
  - service: hwgroup.send_sms
    data:
      phone_number: "+43676XXXXXXX"
      message: >-
        🚨 ALARM: Serverraum zu heiß!
        Temperatur: {{ states('sensor.izw_srv_rack_server') }}°C
        Zeit: {{ now().strftime('%H:%M Uhr') }}
```

5. Speichern Sie die Automation
6. Testen Sie sie durch Ändern des Schwellwerts oder manuelles Auslösen

### Fertig! 🎉

Sie haben erfolgreich:
- ✅ Das SMS Gateway konfiguriert
- ✅ Eine Test-SMS versendet
- ✅ Ihre erste SMS-Automation erstellt

---

## Nächste Schritte

### Mehr Beispiele ansehen
Schauen Sie sich [SMS_SERVICES.md](SMS_SERVICES.md) für weitere Beispiele an:
- Mehrere Empfänger
- Anrufe statt SMS
- Tägliche Status-Reports
- Kritische Alarme mit mehrfacher Benachrichtigung

### SMS-Kosten optimieren
1. Verwenden Sie `hwgroup.call_number` für einfache Alarme (günstiger als SMS)
2. Gruppieren Sie Benachrichtigungen mit Verzögerungen
3. Nutzen Sie Bedingungen, um doppelte SMS zu vermeiden

### Problembehandlung

**SMS kommt nicht an?**
1. Überprüfen Sie die Telefonnummer (internationales Format: `+43...`)
2. Prüfen Sie Signal Quality Sensor (sollte >30% sein)
3. Schauen Sie in die Home Assistant Logs: `ha core logs | grep hwgroup`
4. Testen Sie die URL direkt im Browser: `http://[IP]/values.xml?Cmd=SMS&Nmr=IHRE_NUMMER&Text=Test`

**Service nicht verfügbar?**
1. Starten Sie Home Assistant neu
2. Überprüfen Sie, ob `services.yaml` im Integration-Ordner existiert
3. Prüfen Sie die Logs auf Fehler

**HTTP GET funktioniert nicht?**
- Öffnen Sie das SMS Gateway Web-Interface
- Gehen Sie zu: GSM Modem → "Enable HTTP GET for sending SMS"
- Aktivieren und speichern!

---

## Praktische Tipps

### Telefonnummern-Format
```
✅ Richtig:  +43676123456
✅ Richtig:  00436761234567
❌ Falsch:   0676123456
❌ Falsch:   43676123456
```

### SMS-Text Tipps
- Maximal **160 Zeichen** pro SMS
- Verwenden Sie Emojis für bessere Übersicht: 🚨⚠️✅❌📊🔥
- Fügen Sie Zeitstempel hinzu für bessere Nachvollziehbarkeit
- Halten Sie kritische Infos am Anfang der Nachricht

### Automation Best Practices
```yaml
# ✅ GUT: Mit Bedingung gegen Spam
trigger:
  - platform: numeric_state
    entity_id: sensor.temperature
    above: 30
condition:
  - condition: template
    value_template: >
      {{ (now() - state_attr('automation.temperatur_alarm_sms', 'last_triggered') | default(now() - timedelta(hours=1))).total_seconds() > 3600 }}
action:
  - service: hwgroup.send_sms
    data:
      phone_number: "+43676..."
      message: "Temperatur zu hoch!"

# ❌ SCHLECHT: Keine Spam-Kontrolle, kann viele SMS senden!
trigger:
  - platform: numeric_state
    entity_id: sensor.temperature
    above: 30
action:
  - service: hwgroup.send_sms
    data:
      phone_number: "+43676..."
      message: "Temperatur zu hoch!"
```

---

## Erweiterte Funktionen

### Anruf statt SMS (günstiger!)
```yaml
action:
  - service: hwgroup.call_number
    data:
      phone_number: "+43676123456"
```
Das Telefon klingelt einmal und legt auf - perfekt für stille Alarme!

### SMS mit Sensor-Werten
```yaml
action:
  - service: hwgroup.send_sms
    data:
      phone_number: "+43676123456"
      message: >-
        Server Status:
        CPU: {{ states('sensor.cpu_temp') }}°C
        Rack: {{ states('sensor.izw_srv_rack_server') }}°C
        Tür: {{ states('binary_sensor.srv_izw_door') }}
```

### Mehrere Empfänger
```yaml
action:
  - repeat:
      for_each:
        - "+43676111111"
        - "+43676222222"
      sequence:
        - service: hwgroup.send_sms
          data:
            phone_number: "{{ repeat.item }}"
            message: "ALARM: Server down!"
        - delay:
            seconds: 2
```

---

## Hilfe & Support

Bei Problemen:
1. Überprüfen Sie die Logs: **Einstellungen** → **System** → **Protokolle**
2. Suchen Sie nach "hwgroup" Einträgen
3. Öffnen Sie ein Issue auf GitHub mit den Log-Details

**Viel Erfolg mit Ihren SMS-Automationen! 📱🚀**
