# HW Group Integration Debug Commands
# Run these commands on your Home Assistant to diagnose the issue

# 1. Check if integration is loaded
echo "=== Checking integration status ==="
ha core logs | grep -i "hwgroup" | tail -50

# 2. Check for errors
echo -e "\n=== Checking for errors ==="
ha core logs | grep -E "hwgroup|ERROR|WARNING" | tail -30

# 3. List integration files
echo -e "\n=== Integration files ==="
ls -la /config/custom_components/hwgroup/

# 4. Check if devices are registered
echo -e "\n=== Checking config entries ==="
cat /config/.storage/core.config_entries | grep -A 20 "hwgroup"

# 5. Check coordinator data
echo -e "\n=== Check latest logs with debug ==="
grep "hwgroup" /config/home-assistant.log | tail -100

# 6. Restart integration
echo -e "\n=== To restart integration, run: ==="
echo "ha core restart"
