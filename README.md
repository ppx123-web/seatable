# SeaTable MCP Server

A Model Context Protocol (MCP) server for SeaTable, allowing Claude Code (and other MCP clients) to interact with SeaTable bases.

## Installation

```bash
pip install .
```

## Configuration

The server supports two methods of authentication, allowing you to connect to one or multiple SeaTable bases.

### 1. Multi-Base Configuration (Recommended)

This method allows you to access tables across different bases by mapping table names to specific API tokens.

1.  Create a configuration file (e.g., `seatable_config.json`). You can use `seatable_config.json.example` as a template.
2.  Format:
    ```json
    [
      {
        "table_name": "Expenses",
        "api_token": "token_for_finance_base"
      },
      {
        "table_name": "Employees",
        "api_token": "token_for_hr_base"
      }
    ]
    ```

### 2. Single-Base Configuration (Fallback)

If you strictly only need one base, you can technically set `SEATABLE_API_TOKEN` in the environment, but using the config file is preferred to avoid ambiguity when scaling to multiple tables.

*   `SEATABLE_SERVER_URL`: Your SeaTable Server URL (e.g., `https://cloud.seatable.io`).
*   `SEATABLE_CONFIG_PATH`: Path to your JSON config file.

## Usage

### with Claude Code / CLI

You can add this MCP server to Claude Code using the `uv` command.

**Using Config File:**

```bash
claude mcp add seatable -- uv run --directory /path/to/seatable-mcp seatable-mcp --config-path /path/to/seatable_config.json
```

### Manual Run

```bash
# Set SEATABLE_CONFIG_PATH
uv run seatable-mcp --config-path ./seatable_config.json
```

## Tools

*   `list_rows`: List rows from a table.
*   `add_row`: Add a new row.
*   `update_row`: Update a row.
*   `delete_row`: Delete a row.
*   `get_base_info`: Get base metadata.
*   `run_sql`: Run SQL queries.
