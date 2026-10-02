"""Test configuration for Fan BLE Home."""
import pytest
from unittest.mock import patch, PropertyMock

@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    pass

@pytest.fixture(autouse=True)
def mock_dependencies():
    """Mock dependencies to prevent trying to load real HA components."""
    with patch(
        "homeassistant.loader.Integration.dependencies",
        new_callable=PropertyMock,
        return_value=[]
    ):
        yield
