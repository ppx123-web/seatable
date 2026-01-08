import unittest
from unittest.mock import MagicMock, patch
import seatable_mcp.server as server

class TestSeaTableMCP(unittest.TestCase):
    
    def setUp(self):
        # Reset the global base variable before each test
        server.base = None

    @patch('seatable_mcp.server.Base')
    @patch.dict('os.environ', {'SEATABLE_API_TOKEN': 'fake_token', 'SEATABLE_SERVER_URL': 'https://fake.url'})
    def test_list_rows(self, MockBase):
        # Setup mock
        mock_instance = MockBase.return_value
        mock_instance.list_rows.return_value = [{'id': '1', 'name': 'Test Row'}]
        
        # Call the tool
        result = server.list_rows(table_name="Table1")
        
        # Assertions
        MockBase.assert_called_with('fake_token', 'https://fake.url')
        mock_instance.auth.assert_called_once()
        mock_instance.list_rows.assert_called_with("Table1", view_name=None, limit=100)
        self.assertIn("Test Row", result)

    @patch('seatable_mcp.server.Base')
    @patch.dict('os.environ', {'SEATABLE_API_TOKEN': 'fake_token', 'SEATABLE_SERVER_URL': 'https://fake.url'})
    def test_add_row(self, MockBase):
        mock_instance = MockBase.return_value
        mock_instance.append_row.return_value = {'_id': '123', 'Name': 'New Row'}
        
        result = server.add_row(table_name="Table1", row_data={'Name': 'New Row'})
        
        mock_instance.append_row.assert_called_with("Table1", {'Name': 'New Row'})
        self.assertIn("Row added successfully", result)

    @patch('seatable_mcp.server.Base')
    @patch.dict('os.environ', {'SEATABLE_API_TOKEN': 'fake_token', 'SEATABLE_SERVER_URL': 'https://fake.url'})
    def test_get_base_info(self, MockBase):
        mock_instance = MockBase.return_value
        mock_instance.get_metadata.return_value = {'tables': []}
        
        result = server.get_base_info()
        
        mock_instance.get_metadata.assert_called_once()
        self.assertIn("'tables': []", result)

    @patch('seatable_mcp.server.Base')
    def test_missing_env_vars(self, MockBase):
        # Ensure env vars are missing
        with patch.dict('os.environ', {}, clear=True):
            # The tool should catch the exception and return an error string
            result = server.list_rows(table_name="Table1")
            self.assertIn("Error listing rows", result)
            self.assertIn("environment variables must be set", result)

    @patch('seatable_mcp.server.Base')
    @patch.dict('os.environ', {'SEATABLE_API_TOKEN': 'fake_token', 'SEATABLE_SERVER_URL': 'https://fake.url'})
    def test_column_operations(self, MockBase):
        mock_instance = MockBase.return_value
        
        # list_columns
        mock_instance.list_columns.return_value = [{'key': '0000', 'name': 'Name', 'type': 'text'}]
        self.assertIn("Name", server.list_columns("Table1"))
        
        # insert_column
        server.insert_column("Table1", "NewCol", "text")
        mock_instance.insert_column.assert_called_with("Table1", "NewCol", "text", data=None)
        
        # delete_column
        server.delete_column("Table1", "NewCol")
        mock_instance.delete_column.assert_called_with("Table1", "NewCol")

    @patch('seatable_mcp.server.Base')
    @patch.dict('os.environ', {'SEATABLE_API_TOKEN': 'fake_token', 'SEATABLE_SERVER_URL': 'https://fake.url'})
    def test_view_operations(self, MockBase):
        mock_instance = MockBase.return_value
        
        # list_views
        mock_instance.list_views.return_value = [{'key': '0000', 'name': 'Default View'}]
        self.assertIn("Default View", server.list_views("Table1"))
        
        # create_view
        server.create_view("Table1", "NewView")
        mock_instance.add_view.assert_called_with("Table1", "NewView", view_type='table')
        
        # delete_view
        server.delete_view("Table1", "NewView")
        mock_instance.delete_view.assert_called_with("Table1", "NewView")

    @patch('seatable_mcp.server.Base')
    @patch.dict('os.environ', {'SEATABLE_API_TOKEN': 'fake_token', 'SEATABLE_SERVER_URL': 'https://fake.url'})
    def test_table_operations(self, MockBase):
        mock_instance = MockBase.return_value
        
        # create_table
        server.create_table("NewTable")
        mock_instance.add_table.assert_called_with("NewTable")
        
        # rename_table
        server.rename_table("NewTable", "RenamedTable")
        mock_instance.rename_table.assert_called_with("NewTable", "RenamedTable")
        
        # delete_table
        server.delete_table("RenamedTable")
        mock_instance.delete_table.assert_called_with("RenamedTable")

if __name__ == '__main__':
    unittest.main()
