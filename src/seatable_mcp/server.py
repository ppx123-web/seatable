import os
import sys
import json
from mcp.server.fastmcp import FastMCP
from seatable_api import Base, context

# Initialize FastMCP
mcp = FastMCP("seatable")
server_url = "https://table.nju.edu.cn"

# Global variable to hold the SeaTable base connections
# Map: api_token -> Base instance
_check_base_cache = {}

def load_config():
    """
    Load configuration from JSON file path specified in SEATABLE_CONFIG_PATH
    or default to 'seatable_config.json' in current directory.
    """
    config_path = os.environ.get("SEATABLE_CONFIG_PATH", "seatable_config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config file {config_path}: {e}", file=sys.stderr)
            return []
    return []

def get_token_for_base(base_name: str) -> str:
    """
    Find the API token for a given base name from config.
    Fallback to SEATABLE_API_TOKEN env var if not found in config.
    Note: In config, 'table_name' key is used currently to represent the base name.
    """
    # 1. Try to find in JSON config
    config = load_config()
    if config:
        for entry in config:
            # We treat 'table_name' in config as the base identifier
            if entry.get('table_name') == base_name:
                return entry.get('api_token')
    
    # 2. Fallback to single environment variable
    return os.environ.get("SEATABLE_API_TOKEN")

def get_base(base_name: str = None):
    """
    Get a Base instance. 
    If base_name is provided, tries to find the specific token for that base.
    """
    api_token = None
    if base_name:
        api_token = get_token_for_base(base_name)
    
    # If no base name provided (e.g. get_server_info) or no specific token found...
    if not api_token:
        api_token = os.environ.get("SEATABLE_API_TOKEN")

    if not api_token:
        # If we still don't have a token, and we have a config, pick the first one
        # to allow general operations like get_base_info() to work on the default base.
        config = load_config()
        if config and len(config) > 0:
             api_token = config[0].get('api_token')

    if not api_token:
        # If we still don't have a token, error out.
        raise ValueError(f"No API token found for base '{base_name}' and SEATABLE_API_TOKEN is not set.")

    target_server_url = os.environ.get("SEATABLE_SERVER_URL", server_url)
    
    if api_token in _check_base_cache:
        return _check_base_cache[api_token]

    base = Base(api_token, target_server_url)
    base.auth()
    _check_base_cache[api_token] = base
    return base

@mcp.tool()
def list_rows(table_name: str, view_name: str = None, limit: int = 100, base_name: str = None) -> str:
    """
    List rows from a SeaTable table.
    
    Args:
        table_name: The name of the table to list rows from.
        view_name: Optional name of the view to filter rows.
        limit: Maximum number of rows to return (default 100).
        base_name: Optional name of the base (from config) to look up the API token.
    """
    try:
        b = get_base(base_name)
        # SeaTable API list_rows returns a list of dictionaries
        rows = b.list_rows(table_name, view_name=view_name, limit=limit)
        return str(rows)
    except Exception as e:
        return f"Error listing rows: {str(e)}"

@mcp.tool()
def add_row(table_name: str, row_data: dict, base_name: str = None) -> str:
    """
    Add a new row to a SeaTable table.
    
    Args:
        table_name: The name of the table.
        row_data: A dictionary containing the row data.
        base_name: Optional name of the base (from config) to look up the API token.
    """
    try:
        b = get_base(base_name)
        row = b.append_row(table_name, row_data)
        return f"Row added successfully: {row}"
    except Exception as e:
        return f"Error adding row: {str(e)}"

@mcp.tool()
def update_row(table_name: str, row_id: str, row_data: dict, base_name: str = None) -> str:
    """
    Update an existing row in a SeaTable table.
    
    Args:
        table_name: The name of the table.
        row_id: The ID of the row to update.
        row_data: A dictionary containing the updated data.
        base_name: Optional name of the base (from config) to look up the API token.
    """
    try:
        b = get_base(base_name)
        b.update_row(table_name, row_id, row_data)
        return f"Row {row_id} updated successfully."
    except Exception as e:
        return f"Error updating row: {str(e)}"

@mcp.tool()
def delete_row(table_name: str, row_id: str, base_name: str = None) -> str:
    """
    Delete a row from a SeaTable table.
    
    Args:
        table_name: The name of the table.
        row_id: The ID of the row to delete.
        base_name: Optional name of the base (from config) to look up the API token.
    """
    try:
        b = get_base(base_name)
        b.delete_row(table_name, row_id)
        return f"Row {row_id} deleted successfully."
    except Exception as e:
        return f"Error deleting row: {str(e)}"

@mcp.tool()
def get_base_info(base_name: str = None) -> str:
    """
    Get metadata about the current base (tables, columns, etc).
    
    Args:
        base_name: Optional name of the base (from config) to connect to.
    """
    try:
        b = get_base(base_name)
        metadata = b.get_metadata()
        return str(metadata)
    except Exception as e:
        return f"Error getting base info: {str(e)}"

@mcp.tool()
def run_sql(query: str, base_name: str = None) -> str:
    """
    Execute a SQL query against the SeaTable base.
    
    Args:
        query: The SQL query string.
        base_name: Optional name of the base (from config) to connect to.
    """
    try:
        b = get_base(base_name)
        results = b.query(query)
        return str(results)
    except Exception as e:
        return f"Error executing SQL: {str(e)}"

@mcp.tool()
def list_columns(table_name: str, view_name: str = None, base_name: str = None) -> str:
    """
    List all columns in a table.
    
    Args:
        table_name: The name of the table.
        view_name: Optional view name.
        base_name: Optional name of the base (from config) to look up the API token.
    """
    try:
        b = get_base(base_name)
        columns = b.list_columns(table_name, view_name=view_name)
        return str(columns)
    except Exception as e:
        return f"Error listing columns: {str(e)}"

from seatable_api.constants import ColumnTypes

@mcp.tool()
def insert_column(table_name: str, column_name: str, column_type: str, data: dict = None, base_name: str = None) -> str:
    """
    Insert a new column into a table.
    
    Args:
        table_name: The name of the table.
        column_name: The name of the new column.
        column_type: The type of the column (e.g., 'text', 'number', 'date', 'single-select').
        data: Optional dictionary with additional column options.
        base_name: Optional name of the base (from config) to look up the API token.
    """
    try:
        b = get_base(base_name)
        
        # Map string type to ColumnTypes enum
        type_map = {
            'text': ColumnTypes.TEXT,
            'number': ColumnTypes.NUMBER,
            'date': ColumnTypes.DATE,
            'single-select': ColumnTypes.SINGLE_SELECT,
            'multiple-select': ColumnTypes.MULTIPLE_SELECT,
            'long-text': ColumnTypes.LONG_TEXT,
            'checkbox': ColumnTypes.CHECKBOX,
            'url': ColumnTypes.URL,
            'email': ColumnTypes.EMAIL,
            'duration': ColumnTypes.DURATION,
            'file': ColumnTypes.FILE,
            'image': ColumnTypes.IMAGE,
            'collaborator': ColumnTypes.COLLABORATOR,
        }
        
        # Default to text if not found, or try to use the string if it matches enum name
        c_type = type_map.get(column_type.lower())
        if not c_type:
             # Try to find by name (case insensitive)
             try:
                 c_type = ColumnTypes[column_type.upper().replace("-", "_")]
             except KeyError:
                 return f"Error: Unsupported column type '{column_type}'"

        # The seatable-api insert_column does not accept a 'data' argument in this version
        b.insert_column(table_name, column_name, c_type)
        return f"Column '{column_name}' inserted successfully."
    except Exception as e:
        return f"Error inserting column: {str(e)}"

@mcp.tool()
def delete_column(table_name: str, column_name: str, base_name: str = None) -> str:
    """
    Delete a column from a table.
    
    Args:
        table_name: The name of the table.
        column_name: The name of the column to delete.
        base_name: Optional name of the base (from config) to look up the API token.
    """
    try:
        b = get_base(base_name)
        b.delete_column(table_name, column_name)
        return f"Column '{column_name}' deleted successfully."
    except Exception as e:
        return f"Error deleting column: {str(e)}"

@mcp.tool()
def add_select_options(table_name: str, column_name: str, options: list, base_name: str = None) -> str:
    """
    Add options to a single or multiple select column.
    
    Args:
        table_name: The name of the table.
        column_name: The name of the column.
        options: A list of options to add (strings).
        base_name: Optional name of the base (from config) to look up the API token.
    """
    try:
        b = get_base(base_name)
        
        # Convert simple string options to the dict format required by SeaTable API
        formatted_options = []
        for opt in options:
            if isinstance(opt, str):
                formatted_options.append({
                    "name": opt,
                    "color": "#666666", # Default gray color
                    "textColor": "#FFFFFF"
                })
            else:
                formatted_options.append(opt)
                
        b.add_column_options(table_name, column_name, formatted_options)
        return f"Options added to column '{column_name}'."
    except Exception as e:
        return f"Error adding options: {str(e)}"

@mcp.tool()
def list_views(table_name: str, base_name: str = None) -> str:
    """
    List all views in a table.
    
    Args:
        table_name: The name of the table.
        base_name: Optional name of the base (from config) to look up the API token.
    """
    try:
        b = get_base(base_name)
        views = b.list_views(table_name)
        return str(views)
    except Exception as e:
        return f"Error listing views: {str(e)}"

@mcp.tool()
def create_view(table_name: str, view_name: str, view_type: str = 'table', base_name: str = None) -> str:
    """
    Create a new view in a table.
    
    Args:
        table_name: The name of the table.
        view_name: The name of the new view.
        view_type: The type of view (default 'table').
        base_name: Optional name of the base (from config) to look up the API token.
    """
    try:
        b = get_base(base_name)
        # seatable-api v2.x add_view does not support view_type, defaults to 'table'
        b.add_view(table_name, view_name)
        return f"View '{view_name}' created successfully."
    except Exception as e:
        return f"Error creating view: {str(e)}"

@mcp.tool()
def delete_view(table_name: str, view_name: str, base_name: str = None) -> str:
    """
    Delete a view from a table.
    
    Args:
        table_name: The name of the table.
        view_name: The name of the view to delete.
        base_name: Optional name of the base (from config) to look up the API token.
    """
    try:
        b = get_base(base_name)
        b.delete_view(table_name, view_name)
        return f"View '{view_name}' deleted successfully."
    except Exception as e:
        return f"Error deleting view: {str(e)}"

@mcp.tool()
def create_table(table_name: str, base_name: str = None) -> str:
    """
    Create a new table.
    
    Args:
        table_name: The name of the new table.
        base_name: Optional name of the base (from config) to look up the API token.
    """
    try:
        b = get_base(base_name)
        b.add_table(table_name)
        return f"Table '{table_name}' created successfully."
    except Exception as e:
        return f"Error creating table: {str(e)}"

@mcp.tool()
def rename_table(table_name: str, new_table_name: str, base_name: str = None) -> str:
    """
    Rename a table.
    
    Args:
        table_name: The current name of the table.
        new_table_name: The new name for the table.
        base_name: Optional name of the base (from config) to look up the API token.
    """
    try:
        b = get_base(base_name)
        b.rename_table(table_name, new_table_name)
        return f"Table '{table_name}' renamed to '{new_table_name}'."
    except Exception as e:
        return f"Error renaming table: {str(e)}"

@mcp.tool()
def delete_table(table_name: str, base_name: str = None) -> str:
    """
    Delete a table.
    
    Args:
        table_name: The name of the table to delete.
        base_name: Optional name of the base (from config) to look up the API token.
    """
    try:
        b = get_base(base_name)
        b.delete_table(table_name)
        return f"Table '{table_name}' deleted successfully."
    except Exception as e:
        return f"Error deleting table: {str(e)}"

@mcp.tool()
def get_server_info() -> str:
    """
    Get information about the SeaTable server.
    """
    try:
        b = get_base()
        # There isn't a direct 'get_server_info' in standard base operations usually, 
        # but get_metadata returns base info. We can alias or wrap it.
        # Or we can check if there's a specific call. for now using get_metadata basics.
        return str(b.get_metadata())
    except Exception as e:
        return f"Error getting server info: {str(e)}"

def main():
    mcp.run()

if __name__ == "__main__":
    main()
