# Auto-Discovery Dashboard Template

Diese Lösung erstellt automatisch Dashboard-Karten für alle gefundenen HW Group Geräte.

## Option 1: Auto-Entities Card (Empfohlen)

Installieren Sie zuerst die **auto-entities** Card via HACS:

1. **HACS** → **Frontend** → **Explore & Download Repositories**
2. Suchen Sie nach "**auto-entities**"
3. Installieren und Home Assistant neu starten

### Dashboard YAML mit Auto-Discovery

```yaml
title: HW Group Auto-Discovery
views:
  - title: Alle Geräte
    path: auto
    icon: mdi:auto-fix
    cards:
      # Auto-detect all HW Group temperature sensors
      - type: custom:auto-entities
        card:
          type: horizontal-stack
        filter:
          include:
            - domain: sensor
              attributes:
                device_class: temperature
              integration: hwgroup
          exclude:
            []
        card_param: cards
        card:
          type: gauge
          min: 0
          max: 50
          severity:
            green: 0
            yellow: 28
            red: 35
      
      # Auto-detect all HW Group binary sensors
      - type: custom:auto-entities
        card:
          type: entities
          title: 🚪 Binary Sensors (Auto-detected)
        filter:
          include:
            - domain: binary_sensor
              integration: hwgroup
          exclude:
            []
        show_empty: false
      
      # Auto-detect all HW Group sensors
      - type: custom:auto-entities
        card:
          type: entities
          title: 📊 All Sensors (Auto-detected)
        filter:
          include:
            - domain: sensor
              integration: hwgroup
          exclude:
            []
        show_empty: false
      
      # Auto-detect SMS Gateway sensors
      - type: custom:auto-entities
        card:
          type: glance
          title: 📱 SMS Gateway
          columns: 3
        filter:
          include:
            - entity_id: "*signal*"
              integration: hwgroup
            - entity_id: "*network*"
              integration: hwgroup
            - entity_id: "*sms*"
              integration: hwgroup
          exclude:
            []
        show_empty: false
      
      # History for all temperature sensors
      - type: custom:auto-entities
        card:
          type: history-graph
          title: 🌡️ Temperature History (Auto-detected)
          hours_to_show: 24
        filter:
          include:
            - domain: sensor
              attributes:
                device_class: temperature
              integration: hwgroup
          exclude:
            []
        show_empty: false
```

## Option 2: Template Sensor für Device Liste

Erstellen Sie einen Template Sensor der alle Geräte auflistet:

### In `configuration.yaml`:

```yaml
template:
  - sensor:
      - name: "HW Group Devices List"
        unique_id: hwgroup_devices_list
        state: >
          {{ states.sensor | selectattr('entity_id', 'in', integration_entities('hwgroup'))
             | map(attribute='entity_id') | list | count }}
        attributes:
          devices: >
            {% set ns = namespace(devices=[]) %}
            {% for entity in integration_entities('hwgroup') %}
              {% set device = device_attr(entity, 'name') %}
              {% if device and device not in ns.devices %}
                {% set ns.devices = ns.devices + [device] %}
              {% endif %}
            {% endfor %}
            {{ ns.devices }}
          
          temperature_sensors: >
            {{ states.sensor 
               | selectattr('entity_id', 'in', integration_entities('hwgroup'))
               | selectattr('attributes.device_class', 'eq', 'temperature')
               | map(attribute='entity_id') | list }}
          
          binary_sensors: >
            {{ states.binary_sensor 
               | selectattr('entity_id', 'in', integration_entities('hwgroup'))
               | map(attribute='entity_id') | list }}
          
          sms_sensors: >
            {{ states.sensor 
               | selectattr('entity_id', 'in', integration_entities('hwgroup'))
               | selectattr('entity_id', 'search', 'signal|sms|network')
               | map(attribute='entity_id') | list }}
```

### Dashboard verwendet den Template Sensor:

```yaml
title: HW Group Dynamic
views:
  - title: Overview
    cards:
      # Show device count
      - type: markdown
        content: >
          # 🖥️ HW Group Devices
          
          **Total Devices**: {{ state_attr('sensor.hwgroup_devices_list', 'devices') | count }}
          
          **Devices**:
          {% for device in state_attr('sensor.hwgroup_devices_list', 'devices') %}
          - {{ device }}
          {% endfor %}
      
      # Dynamic temperature gauges
      - type: horizontal-stack
        cards:
          {% for sensor in state_attr('sensor.hwgroup_devices_list', 'temperature_sensors') %}
          - type: gauge
            entity: {{ sensor }}
            min: 0
            max: 50
          {% endfor %}
      
      # Dynamic binary sensors
      - type: entities
        title: Binary Sensors
        entities:
          {% for sensor in state_attr('sensor.hwgroup_devices_list', 'binary_sensors') %}
          - {{ sensor }}
          {% endfor %}
```

## Option 3: Python Automation

Erstellen Sie eine Automation die bei Integration Neustart das Dashboard aktualisiert:

### `automations.yaml`:

```yaml
- alias: "Update HW Group Dashboard on Change"
  description: "Automatically rebuild dashboard when HW Group devices change"
  trigger:
    - platform: homeassistant
      event: start
    - platform: event
      event_type: call_service
      event_data:
        domain: homeassistant
        service: reload_config_entry
  condition:
    - condition: template
      value_template: >
        {{ trigger.event.data.entry_id in 
           integration_entities('hwgroup') | map('device_id') | list }}
  action:
    - service: notify.persistent_notification
      data:
        title: "HW Group Dashboard"
        message: >
          Dashboard should be updated. Found {{ integration_entities('hwgroup') | count }} entities.
```

## Option 4: Markdown Template Card

Einfachste Lösung - zeigt alle Entitäten in Markdown:

```yaml
title: HW Group Simple
views:
  - title: All Devices
    cards:
      - type: markdown
        content: >
          # 🖥️ HW Group Devices
          
          ## 🌡️ Temperature Sensors
          {% for entity in integration_entities('hwgroup') %}
            {% if state_attr(entity, 'device_class') == 'temperature' %}
          - **{{ state_attr(entity, 'friendly_name') }}**: {{ states(entity) }}°C
            {% endif %}
          {% endfor %}
          
          ## 🚪 Binary Sensors
          {% for entity in integration_entities('hwgroup') %}
            {% if entity.startswith('binary_sensor.') %}
          - **{{ state_attr(entity, 'friendly_name') }}**: {{ states(entity) }}
            {% endif %}
          {% endfor %}
          
          ## 📱 SMS Gateway
          {% for entity in integration_entities('hwgroup') %}
            {% if 'signal' in entity or 'sms' in entity or 'network' in entity %}
          - **{{ state_attr(entity, 'friendly_name') }}**: {{ states(entity) }} {{ state_attr(entity, 'unit_of_measurement') }}
            {% endif %}
          {% endfor %}
```

## Empfehlung

**Beste Lösung**: Option 1 mit **auto-entities** Card

Vorteile:
- ✅ Vollautomatisch
- ✅ Keine manuelle Konfiguration nötig
- ✅ Aktualisiert sich bei neuen Geräten
- ✅ Schöne Darstellung mit Gauges, Entities, Glance
- ✅ Filtert automatisch nach Integration

Nach der Installation von auto-entities via HACS einfach den YAML-Code kopieren und als neues Dashboard hinzufügen!

## Test

Um zu testen welche Entitäten gefunden werden:

**Developer Tools** → **Template**:

```jinja
{{ integration_entities('hwgroup') }}
```

Zeigt alle HW Group Entitäten an!
