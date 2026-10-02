"""Test configuration for Fan BLE Home."""
import pytest
from unittest.mock import patch

@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    pass

@pytest.fixture(autouse=True)
def mock_bluetooth():
    """Mock bluetooth setup."""
    with patch("homeassistant.components.bluetooth.async_setup", return_value=True), \
         patch("homeassistant.components.bluetooth.async_setup_entry", return_value=True):
        yield
