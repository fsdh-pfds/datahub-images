import unittest
from unittest.mock import patch
from function_app import get_config

class TestConfig(unittest.TestCase):

    @patch.dict(os.environ, {
        'DatahubServiceBus': 'test_connection_string',
        'AzureServiceBusQueueName4Bugs': 'test_bug_queue',
        'AzureServiceBusQueueName4Results': 'test_results_queue'
    })
    def test_get_config(self):
        asb_connection_str, queue_name, check_results_queue_name = get_config()
        self.assertEqual(asb_connection_str, 'test_connection_string')
        self.assertEqual(queue_name, 'test_bug_queue')
        self.assertEqual(check_results_queue_name, 'test_results_queue')

if __name__ == '__main__':
    unittest.main()