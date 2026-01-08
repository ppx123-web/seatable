import unittest
from unittest.mock import MagicMock, patch, mock_open
import seatable_mcp.server as server
import json

class TestSeaTableMultiToken(unittest.TestCase):
    
    def setUp(self):
        # Reset cache
        server._check_base_cache = {}

    @patch('seatable_mcp.server.Base')
    @patch.dict('os.environ', {'SEATABLE_SERVER_URL': 'https://fake.url'})
    def test_get_base_from_config(self, MockBase):
        mock_config = [
            {"table_name": "TableA", "api_token": "token_a"},
            {"table_name": "TableB", "api_token": "token_b"}
        ]
        
        with patch('builtins.open', mock_open(read_data=json.dumps(mock_config))):
            with patch('os.path.exists', return_value=True):
                
                # Test TableA
                base_a = server.get_base("TableA")
                MockBase.assert_called_with('token_a', 'https://fake.url')
                
                # Test TableB
                base_b = server.get_base("TableB")
                MockBase.assert_called_with('token_b', 'https://fake.url')

    @patch('seatable_mcp.server.Base')
    @patch.dict('os.environ', {'SEATABLE_API_TOKEN': 'env_token', 'SEATABLE_SERVER_URL': 'https://fake.url'})
    def test_get_base_fallback(self, MockBase):
        # No config file
        with patch('os.path.exists', return_value=False):
            base = server.get_base("TableFallback")
            MockBase.assert_called_with('env_token', 'https://fake.url')

    @patch('seatable_mcp.server.Base')
    def test_get_base_no_token(self, MockBase):
        with patch('os.path.exists', return_value=False):
            with patch.dict('os.environ', {}, clear=True):
                with self.assertRaises(ValueError):
                    server.get_base("AnyTable")

if __name__ == '__main__':
    unittest.main()
