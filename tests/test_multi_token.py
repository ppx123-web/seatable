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
    def test_get_api_token_from_config(self, MockBase):
        mock_config = [
            {"base_name": "BaseA", "api_token": "token_a"},
            {"base_name": "BaseB", "api_token": "token_b"}
        ]
        
        with patch('builtins.open', mock_open(read_data=json.dumps(mock_config))):
            with patch('os.path.exists', return_value=True):
                
                # Test get_api_token
                token_a = server.get_api_token("BaseA")
                self.assertEqual(token_a, "token_a")
                
                token_b = server.get_api_token("BaseB")
                self.assertEqual(token_b, "token_b")

                # Verify get_base usages
                server.get_base(api_token=token_a)
                MockBase.assert_called_with('token_a', 'https://fake.url')

    @patch('seatable_mcp.server.Base')
    @patch.dict('os.environ', {'SEATABLE_API_TOKEN': 'env_token', 'SEATABLE_SERVER_URL': 'https://fake.url'})
    def test_get_base_fallback(self, MockBase):
        # No api_token passed
        base = server.get_base()
        MockBase.assert_called_with('env_token', 'https://fake.url')

    @patch('seatable_mcp.server.Base')
    def test_get_base_no_token(self, MockBase):
        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(ValueError):
                server.get_base()

if __name__ == '__main__':
    unittest.main()
