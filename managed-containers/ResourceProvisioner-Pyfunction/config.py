#config.py
import os

# Constants from environment variables
DATAHUB_ENVNAME = os.getenv("DataHub_ENVNAME")
AZURE_SUBSCRIPTION_ID = os.getenv("AzureSubscriptionId")
AZURE_TENANT_ID = os.getenv("AzureTenantId")
asb_connection_str = os.getenv("DatahubServiceBus")

queue_name = os.getenv("AzureServiceBusQueueName4Bugs") or "bug-report"
check_results_queue_name = os.getenv("AzureServiceBusQueueName4Results") or "infrastructure-health-check-results"
