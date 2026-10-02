with open("custom_components/fan_ble_home/__init__.py", "r") as f:
    content = f.read()

content = content.replace(
    'data["entries"].add(entry.entry_id)\n    return True',
    'data["entries"].add(entry.entry_id)\n    await hass.config_entries.async_forward_entry_setups(entry, ["fan", "light"])\n    return True'
)

content = content.replace(
    'return True\n',
    'return await hass.config_entries.async_unload_platforms(entry, ["fan", "light"])\n'
)

with open("custom_components/fan_ble_home/__init__.py", "w") as f:
    f.write(content)
