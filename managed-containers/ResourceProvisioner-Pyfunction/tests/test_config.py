# tests/test_config.py
import os
import sys
import importlib

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config

def test_config_with_env(monkeypatch):
    # Set environment variables to custom values
    monkeypatch.setenv("DataHub_ENVNAME", "test_env")
    monkeypatch.setenv("AzureSubscriptionId", "sub123")
    monkeypatch.setenv("AzureTenantId", "tenant123")
    monkeypatch.setenv("DatahubServiceBus", "servicebus_connection")
    monkeypatch.setenv("AzureServiceBusQueueName4Bugs", "custom_bug_queue")
    monkeypatch.setenv("AzureServiceBusQueueName4Results", "custom_results_queue")

    # Reload the config module so it picks up the new environment variables
    importlib.reload(config)

    assert config.DATAHUB_ENVNAME == "test_env"
    assert config.AZURE_SUBSCRIPTION_ID == "sub123"
    assert config.AZURE_TENANT_ID == "tenant123"
    assert config.asb_connection_str == "servicebus_connection"
    assert config.queue_name == "custom_bug_queue"
    assert config.check_results_queue_name == "custom_results_queue"


def test_config_defaults(monkeypatch):
    # Remove environment variables if they exist
    monkeypatch.delenv("DataHub_ENVNAME", raising=False)
    monkeypatch.delenv("AzureSubscriptionId", raising=False)
    monkeypatch.delenv("AzureTenantId", raising=False)
    monkeypatch.delenv("DatahubServiceBus", raising=False)
    monkeypatch.delenv("AzureServiceBusQueueName4Bugs", raising=False)
    monkeypatch.delenv("AzureServiceBusQueueName4Results", raising=False)

    # Reload the config module to use the updated (cleared) environment
    importlib.reload(config)

    # For these variables, there are no defaults so they should be None
    assert config.DATAHUB_ENVNAME is None
    assert config.AZURE_SUBSCRIPTION_ID is None
    assert config.AZURE_TENANT_ID is None
    assert config.asb_connection_str is None

    # For these, the default values should kick in
    assert config.queue_name == "bug-report"
    assert config.check_results_queue_name == "infrastructure-health-check-results"
