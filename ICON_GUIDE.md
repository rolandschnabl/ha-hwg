# HW Group Integration Icon

## Icon Requirements

Home Assistant integrations need an icon in the following format:

### File Location
```
custom_components/hwgroup/icon.png
```

### Specifications
- **Format**: PNG
- **Size**: 256x256 pixels
- **Background**: Transparent (recommended)
- **Style**: Simple, clear, recognizable

## Icon Design Suggestions

### Option 1: HW Group Logo
Use the official HW Group logo if available from their website.

### Option 2: Poseidon Theme
Design an icon representing the Poseidon devices:
- Network/monitoring symbol
- Server/rack icon
- Temperature/sensor symbol
- Combined with "HW" or "P" letter

### Option 3: Simple Text Icon
Create a simple icon with:
- "HWG" or "HW" text
- Clean, modern font
- Brand colors: Blue/Green theme
- Transparent or solid background

## How to Create the Icon

### Using GIMP (Free)
1. Create new image: 256x256 pixels
2. Add transparent background
3. Design your icon
4. Export as PNG: `icon.png`
5. Save to: `custom_components/hwgroup/icon.png`

### Using Inkscape (Free)
1. Create new document: 256x256 pixels
2. Design vector icon
3. Export as PNG at 256x256
4. Save to: `custom_components/hwgroup/icon.png`

### Using Online Tools
- **Canva**: Free online design tool
- **Figma**: Free design tool
- **LogoMaker**: Generate simple icons
- **Flaticon**: Download and customize icons

## Recommended Icon Styles

### Style 1: Monitoring Device
```
┌─────────────┐
│  [===]      │  
│  |   |      │  Server/Device
│  |___|      │  
│   📊 🌡️    │  Sensors
└─────────────┘
```

### Style 2: Network Monitoring
```
    🌐
   / | \
  📊 🌡️ 💡  Sensors/Outputs
```

### Style 3: Simple Text
```
┌─────────────┐
│             │
│     HWG     │  Clean Text
│             │
└─────────────┘
```

## Color Suggestions

- **Primary**: #0066CC (Blue)
- **Secondary**: #00AA66 (Green)
- **Accent**: #FF9900 (Orange)
- **Text**: #FFFFFF (White)

## After Creating the Icon

1. Save as `icon.png` (256x256 pixels)
2. Place in: `custom_components/hwgroup/icon.png`
3. Restart Home Assistant
4. Icon will appear in:
   - Integration list
   - Device pages
   - Configuration dialogs

## Icon Template (SVG)

You can use this basic SVG template and customize it:

```svg
<svg width="256" height="256" xmlns="http://www.w3.org/2000/svg">
  <!-- Background circle -->
  <circle cx="128" cy="128" r="120" fill="#0066CC"/>
  
  <!-- Text -->
  <text x="128" y="150" font-family="Arial, sans-serif" font-size="80" 
        font-weight="bold" fill="white" text-anchor="middle">HWG</text>
  
  <!-- Small sensor icon -->
  <rect x="100" y="180" width="56" height="30" rx="5" fill="white" opacity="0.8"/>
</svg>
```

Save this as SVG, then export as PNG at 256x256 pixels.

## Quick Option: Use Existing Icon

You can also use an icon from:
- **Material Design Icons**: https://materialdesignicons.com/
- **Font Awesome**: https://fontawesome.com/
- **Feather Icons**: https://feathericons.com/

Search for: "monitor", "server", "sensor", "device", "network"

## Installation

Once you have the icon:

```bash
# Copy icon to integration folder
cp icon.png custom_components/hwgroup/icon.png

# Or on Windows
copy icon.png custom_components\hwgroup\icon.png
```

Then restart Home Assistant to see the icon.

---

**Note**: If you don't have an icon, the integration will work fine but will use a default Home Assistant icon.
