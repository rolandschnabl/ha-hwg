#!/usr/bin/env python3
"""
HW Group Dashboard Generator
Automatically generates a Home Assistant dashboard YAML based on discovered devices.

Usage:
1. Run this script: python generate_dashboard.py
2. Copy the output to your Home Assistant dashboard
3. Or save to a file: python generate_dashboard.py > dashboard.yaml

Requirements:
- Home Assistant with HW Group integration installed
- Access to Home Assistant's states API or YAML configuration
"""

import json
import sys
from collections import defaultdict


def get_entities_from_stdin():
    """Read entities from stdin (JSON format)."""
    try:
        data = json.load(sys.stdin)
        return data
    except:
        return None


def get_entities_from_file(filename="entities.json"):
    """Read entities from a JSON file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except:
        return None


def categorize_entities(entities):
    """Categorize entities by device and type."""
    devices = defaultdict(lambda: {
        'name': 'Unknown Device',
        'sensors': [],
        'binary_sensors': [],
        'switches': []
    })
    
    for entity in entities:
        entity_id = entity.get('entity_id', '')
        state = entity.get('state', 'unavailable')
        attributes = entity.get('attributes', {})
        
        # Extract device info
        device_name = attributes.get('friendly_name', entity_id)
        device_id = attributes.get('device_id', 'default')
        
        # Get parent device name if available
        if 'device_info' in attributes:
            device_name = attributes['device_info'].get('name', device_name)
        
        # Categorize by domain
        domain = entity_id.split('.')[0]
        
        entity_info = {
            'entity_id': entity_id,
            'name': device_name,
            'state': state,
            'unit': attributes.get('unit_of_measurement', ''),
            'icon': attributes.get('icon', ''),
            'device_class': attributes.get('device_class', ''),
            'attributes': attributes
        }
        
        if domain == 'sensor':
            devices[device_id]['sensors'].append(entity_info)
        elif domain == 'binary_sensor':
            devices[device_id]['binary_sensors'].append(entity_info)
        elif domain == 'switch':
            devices[device_id]['switches'].append(entity_info)
        
        # Update device name
        if 'device_info' in attributes:
            devices[device_id]['name'] = attributes['device_info'].get('name', device_name)
    
    return devices


def generate_gauge_card(sensor):
    """Generate a gauge card for a sensor."""
    min_val = 0
    max_val = 100
    
    # Determine min/max based on device class
    if sensor['device_class'] == 'temperature':
        min_val = 0
        max_val = 50
    elif sensor['device_class'] == 'humidity':
        min_val = 0
        max_val = 100
    
    return f"""      - type: gauge
        entity: {sensor['entity_id']}
        name: {sensor['name']}
        min: {min_val}
        max: {max_val}
        severity:
          green: {min_val}
          yellow: {max_val * 0.7}
          red: {max_val * 0.85}
        needle: true"""


def generate_entities_card(items, title, show_state=True):
    """Generate an entities card."""
    yaml = f"""      - type: entities
        title: {title}
        show_header_toggle: false
        entities:
"""
    for item in items:
        yaml += f"""          - entity: {item['entity_id']}
            name: {item['name']}
"""
        if show_state:
            yaml += f"""            secondary_info: last-changed
"""
    return yaml


def generate_history_graph(sensors, title="History", hours=24):
    """Generate a history graph card."""
    yaml = f"""      - type: history-graph
        title: {title}
        hours_to_show: {hours}
        refresh_interval: 60
        entities:
"""
    for sensor in sensors:
        yaml += f"""          - entity: {sensor['entity_id']}
            name: {sensor['name']}
"""
    return yaml


def generate_glance_card(items, title, columns=3):
    """Generate a glance card."""
    yaml = f"""      - type: glance
        title: {title}
        show_name: true
        show_state: true
        columns: {columns}
        entities:
"""
    for item in items:
        yaml += f"""          - entity: {item['entity_id']}
            name: {item['name']}
"""
    return yaml


def generate_dashboard(devices):
    """Generate complete dashboard YAML."""
    yaml = """title: HW Group Monitoring (Auto-Generated)
views:
  - title: Übersicht
    path: overview
    icon: mdi:view-dashboard
    badges: []
    cards:
      # Header
      - type: markdown
        content: |
          # 🖥️ HW Group Monitoring
          Auto-generated dashboard for all discovered devices
          
          **Total Devices**: {device_count}
          **Last Updated**: {{{{ now().strftime('%d.%m.%Y %H:%M:%S') }}}}

""".format(device_count=len(devices))
    
    # Generate cards for each device
    for device_id, device_data in devices.items():
        device_name = device_data['name']
        sensors = device_data['sensors']
        binary_sensors = device_data['binary_sensors']
        switches = device_data['switches']
        
        if not sensors and not binary_sensors and not switches:
            continue
        
        # Device header
        yaml += f"""      # Device: {device_name}
      - type: vertical-stack
        cards:
          - type: markdown
            content: |
              ## 🔧 {device_name}

"""
        
        # Temperature sensors as gauges
        temp_sensors = [s for s in sensors if s['device_class'] == 'temperature']
        if temp_sensors:
            yaml += """          - type: horizontal-stack
            cards:
"""
            for sensor in temp_sensors[:3]:  # Max 3 gauges per row
                yaml += generate_gauge_card(sensor) + "\n"
        
        # Other sensors as entities
        other_sensors = [s for s in sensors if s['device_class'] != 'temperature']
        if other_sensors:
            yaml += generate_entities_card(other_sensors, f"{device_name} - Sensors")
        
        # Binary sensors
        if binary_sensors:
            yaml += generate_glance_card(binary_sensors, f"{device_name} - Status", columns=3)
        
        # Switches
        if switches:
            yaml += generate_entities_card(switches, f"{device_name} - Controls", show_state=True)
        
        # History graph for sensors
        if sensors:
            yaml += generate_history_graph(sensors, f"{device_name} - History (24h)", hours=24)
        
        yaml += "\n"
    
    # Add SMS Services tab if SMS Gateway found
    has_sms_gateway = any(
        'sms' in s['entity_id'].lower() or 'signal' in s['entity_id'].lower()
        for device in devices.values()
        for s in device['sensors']
    )
    
    if has_sms_gateway:
        yaml += """
  # SMS Services Tab
  - title: SMS
    path: sms
    icon: mdi:message-text
    badges: []
    cards:
      - type: markdown
        content: |
          # 📱 SMS Services
          Send SMS messages and make calls
          
          **Status**: {{{{ states('sensor.network_status') }}}}
          **Signal**: {{{{ states('sensor.signal_quality') }}}}%

      - type: entities
        title: SMS Gateway Status
        show_header_toggle: false
        entities:
          - sensor.signal_strength
          - sensor.signal_quality
          - sensor.network_operator
          - sensor.network_status
          - sensor.sms_sent
          - sensor.sms_errors

      - type: markdown
        content: |
          ## Quick Actions
          Use Developer Tools → Services to send SMS:
          
          ```yaml
          service: hwgroup.send_sms
          data:
            phone_number: "+43676XXXXXXX"
            message: "Your message"
          ```

"""
    
    return yaml


def main():
    """Main function."""
    print("# HW Group Dashboard Generator", file=sys.stderr)
    print("# Reading entities...", file=sys.stderr)
    
    # Try to read entities from stdin or file
    entities = get_entities_from_stdin()
    if not entities:
        entities = get_entities_from_file()
    
    if not entities:
        print("\n❌ No entities found!", file=sys.stderr)
        print("\nUsage:", file=sys.stderr)
        print("1. Export entities from Home Assistant:", file=sys.stderr)
        print("   Developer Tools → States → Copy all HW Group entities to JSON", file=sys.stderr)
        print("2. Save to entities.json", file=sys.stderr)
        print("3. Run: python generate_dashboard.py", file=sys.stderr)
        print("\nOr pipe entities JSON to stdin:", file=sys.stderr)
        print("   echo '[{...}]' | python generate_dashboard.py", file=sys.stderr)
        return 1
    
    print(f"# Found {len(entities)} entities", file=sys.stderr)
    
    # Categorize entities
    devices = categorize_entities(entities)
    print(f"# Categorized into {len(devices)} devices", file=sys.stderr)
    
    # Generate dashboard
    dashboard_yaml = generate_dashboard(devices)
    
    print("\n# Dashboard generated successfully!", file=sys.stderr)
    print("# Copy the output below to your Home Assistant dashboard\n", file=sys.stderr)
    
    # Output dashboard YAML
    print(dashboard_yaml)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
