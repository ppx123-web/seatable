# SeaTable MCP Server

A Model Context Protocol (MCP) server for SeaTable, allowing Claude Code (and other MCP clients) to interact with SeaTable bases.

## Installation

```bash
pip install .
```

## Configuration

The server supports two methods of authentication, allowing you to connect to one or multiple SeaTable bases.

### 1. Multi-Base Configuration (Recommended)

This method allows you to access different bases by mapping base names to specific API tokens.

1.  Create a configuration file (e.g., `seatable_config.json`). You can use `seatable_config.json.example` as a template.
2.  Format:
    ```json
    [
      {
        "base_name": "Finance",
        "api_token": "token_for_finance_base"
      },
      {
        "base_name": "HR",
        "api_token": "token_for_hr_base"
      }
    ]
    ```

### 2. Single-Base Configuration (Fallback)

If you strictly only need one base, you can technically set `SEATABLE_API_TOKEN` in the environment.

*   `SEATABLE_SERVER_URL`: Your SeaTable Server URL (e.g., `https://cloud.seatable.io`).
*   `SEATABLE_CONFIG_PATH`: Path to your JSON config file.

## Usage

### with Claude Code / CLI

You can add this MCP server to Claude Code using the `uv` command.

**Using Config File (Recommended):**

```bash
claude mcp add seatable \
  --env SEATABLE_CONFIG_PATH=/path/to/config.json \
  -- \
  /opt/homebrew/bin/uvx \
  --from git+https://github.com/ppx123-web/seatable.git \
  seatable-mcp
```

### Manual Run

```bash
# Set SEATABLE_CONFIG_PATH
SEATABLE_CONFIG_PATH=./seatable_config.json uv run seatable-mcp
```

## Workflow & Tools

The API is decoupled to separate **Configuration** from **Operation**.

### 1. Get Context
First, use these tools to understand what bases are available and get an access token.

*   `get_all_bases()`: List all configured bases and their tokens.
*   `get_api_token(base_name)`: Get the API token for a specific base.

### 2. Perform Operations
Pass the `api_token` retrieved above to these tools to perform actions.

*   `list_rows(table_name, ..., api_token=...)`
*   `add_row(table_name, row_data, api_token=...)`
*   `update_row(table_name, row_id, row_data, api_token=...)`
*   `delete_row(table_name, row_id, api_token=...)`
*   `get_base_info(api_token=...)`
*   `run_sql(query, api_token=...)`
*   `list_columns(...)`
*   `insert_column(...)`
*   `delete_column(...)`
*   `add_select_options(...)`
*   `list_views(...)`
*   `create_view(...)`
*   `delete_view(...)`
*   `create_table(...)`
*   `rename_table(...)`
*   `delete_table(...)`

