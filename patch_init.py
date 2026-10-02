with open("custom_components/fan_ble_home/__init__.py", "r") as f:
    content = f.read()

if "async_setup_entry" not in content:
    content += """
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    \"\"\"Set up Fan BLE Home from a config entry.\"\"\"
    await hass.config_entries.async_forward_entry_setups(entry, ["fan", "light"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    \"\"\"Unload a config entry.\"\"\"
    return await hass.config_entries.async_unload_platforms(entry, ["fan", "light"])
"""
    with open("custom_components/fan_ble_home/__init__.py", "w") as f:
        f.write(content)
