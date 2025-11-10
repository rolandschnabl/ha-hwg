# GitHub Repository Configuration

To complete the HACS validation, you need to configure your GitHub repository:

## 1. Add Repository Description

Go to: https://github.com/rolandschnabl/ha-hwg

1. Click "About" settings (gear icon) on the right side
2. Add description: **Home Assistant integration for HW Group devices (Poseidon 3268, 3266, SMS Gateway)**
3. Click "Save changes"

## 2. Add Topics

In the same "About" settings dialog, add these topics:
- `home-assistant`
- `hacs`
- `homeassistant`
- `custom-component`
- `hwgroup`
- `poseidon`
- `integration`

## 3. Verification

After adding the description and topics, the HACS validation should pass.

## Alternative: Use GitHub CLI

If you have GitHub CLI installed, you can run:

```powershell
gh repo edit rolandschnabl/ha-hwg --description "Home Assistant integration for HW Group devices (Poseidon 3268, 3266, SMS Gateway)"

gh repo edit rolandschnabl/ha-hwg --add-topic home-assistant --add-topic hacs --add-topic homeassistant --add-topic custom-component --add-topic hwgroup --add-topic poseidon --add-topic integration
```

## Note about Brands

The "brands" error can be ignored for custom integrations. It's only required for official Home Assistant integrations.
