# Contributing to HW Group Integration

Thank you for your interest in contributing! Here's how you can help.

## Ways to Contribute

- 🐛 **Report bugs** - Open an issue with details
- 💡 **Suggest features** - Describe your idea
- 📝 **Improve documentation** - Fix typos, add examples
- 🔧 **Submit code** - Fix bugs or add features
- 🧪 **Test** - Try with your device and report results

## Reporting Issues

When reporting a bug, please include:

1. **Home Assistant version**
2. **Integration version**
3. **Device model and firmware**
4. **Steps to reproduce**
5. **Error logs** (from Settings → System → Logs)
6. **Expected vs actual behavior**

**Optional but helpful:**
- Sample XML from `http://[device-ip]/values.xml` (anonymized)
- Screenshots
- Configuration details

## Suggesting Features

Feature requests are welcome! Please describe:

1. **What** you want to achieve
2. **Why** it would be useful
3. **How** you envision it working
4. **Which devices** it applies to

## Pull Requests

### Before You Start

1. Check existing issues and PRs
2. Open an issue to discuss major changes
3. Fork the repository
4. Create a feature branch

### Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/homeassistant-hwgroup.git
cd homeassistant-hwgroup

# Create a branch
git checkout -b feature/your-feature-name
```

### Code Guidelines

- Follow existing code style
- Use type hints where possible
- Add docstrings to new functions/classes
- Keep functions focused and small
- Use async/await for I/O operations

### Testing Your Changes

1. **Local Testing**
   - Copy integration to Home Assistant
   - Test with real device
   - Verify all entity types work
   - Check logs for errors

2. **Code Quality**
   - Ensure JSON files are valid
   - Check for Python syntax errors
   - Test configuration flow
   - Verify entity states update

### Submitting PR

1. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: description of changes"
   ```

2. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request**
   - Go to GitHub
   - Click "New Pull Request"
   - Describe your changes
   - Reference related issues

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring

## Testing
- [ ] Tested with Poseidon 3268
- [ ] Tested with Poseidon 3266
- [ ] Tested with SMS Gateway
- [ ] Config flow works
- [ ] Entities update correctly
- [ ] No errors in logs

## Checklist
- [ ] Code follows existing style
- [ ] Documentation updated
- [ ] Tested locally
- [ ] No breaking changes (or documented)
```

## Code Style

### Python Style
- Follow PEP 8
- Use meaningful variable names
- Max line length: 88 characters (Black formatter)
- Use f-strings for formatting

### Example
```python
async def async_get_sensor_data(self, sensor_id: str) -> dict[str, Any] | None:
    """
    Get data for a specific sensor.
    
    Args:
        sensor_id: The unique identifier of the sensor
        
    Returns:
        Dictionary with sensor data or None if not found
    """
    data = await self.async_get_data()
    for sensor in data.get("sensors", []):
        if sensor["id"] == sensor_id:
            return sensor
    return None
```

## Adding New Features

### New Sensor Type

1. Add constant to `const.py`
2. Update `_determine_sensor_type()` in `hwgroup.py`
3. Add device class in `sensor.py`
4. Test with device
5. Update documentation

### New Device Model

1. Test XML output from device
2. Update XML parsing if needed
3. Add device type to `const.py`
4. Test all entity types
5. Update README and EXAMPLES.md

### New Platform (e.g., Climate)

1. Create new file: `climate.py`
2. Implement platform setup
3. Add to `PLATFORMS` in `__init__.py`
4. Test thoroughly
5. Update documentation

## Documentation

When adding features, update:

- README.md - Overview and features
- INSTALLATION.md - If setup changes
- EXAMPLES.md - If XML structure differs
- CHANGELOG.md - Version history

## Testing Checklist

Before submitting:

- [ ] Code runs without errors
- [ ] Config flow works
- [ ] Entities appear correctly
- [ ] States update properly
- [ ] Switches control outputs (if applicable)
- [ ] Authentication works (if used)
- [ ] Device info displays correctly
- [ ] Unique IDs are stable
- [ ] No log warnings/errors
- [ ] Documentation updated

## Device Support

Have a HW Group device not yet supported?

1. **Capture XML Output**
   - Access `http://[device-ip]/values.xml`
   - Save the XML (anonymize if needed)
   - Note device model and firmware

2. **Test Integration**
   - Try existing integration
   - Note what works and what doesn't

3. **Open Issue**
   - Include device details
   - Attach XML sample
   - Describe expected behavior

## Questions?

- Open a discussion on GitHub
- Check existing issues
- Read documentation files

## Code of Conduct

- Be respectful and constructive
- Welcome newcomers
- Focus on the issue, not the person
- Assume good intentions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing!** Every contribution, no matter how small, helps improve the integration. 🙏
