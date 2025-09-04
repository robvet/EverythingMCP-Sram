#!/bin/bash

# MCP Testing Helper Script
# Usage: ./mcp_test.sh <method> [tool_name] [arguments]

set -e

MCP_URL="http://localhost:8000/mcp"
CONTENT_TYPE="Content-Type: application/json"

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_colored() {
    echo -e "${1}${2}${NC}"
}

# Function to check if jq is available
check_jq() {
    if ! command -v jq &> /dev/null; then
        print_colored $YELLOW "Warning: jq not found. Install with: brew install jq"
        return 1
    fi
    return 0
}

# Function to make MCP request
make_mcp_request() {
    local request_data="$1"
    local use_jq="$2"
    
    print_colored $BLUE "=== MCP Request ==="
    echo "$request_data" | (check_jq && jq '.' || cat)
    print_colored $BLUE "=== MCP Response ==="
    
    if check_jq && [ "$use_jq" = "true" ]; then
        curl -s -X POST "$MCP_URL" \
            -H "$CONTENT_TYPE" \
            -d "$request_data" | jq '.'
    else
        curl -s -X POST "$MCP_URL" \
            -H "$CONTENT_TYPE" \
            -d "$request_data" | python -m json.tool
    fi
}

# Function to extract tool result content
extract_tool_result() {
    local request_data="$1"
    
    print_colored $BLUE "=== Tool Result ==="
    
    if check_jq; then
        curl -s -X POST "$MCP_URL" \
            -H "$CONTENT_TYPE" \
            -d "$request_data" | jq -r '.result.content[0].text' | jq '.'
    else
        curl -s -X POST "$MCP_URL" \
            -H "$CONTENT_TYPE" \
            -d "$request_data"
    fi
}

# Main script logic
case "$1" in
    "init")
        print_colored $GREEN "Initializing MCP connection..."
        REQUEST='{
            "jsonrpc": "2.0",
            "id": "init-1",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "mcp-test-script",
                    "version": "1.0.0"
                }
            }
        }'
        make_mcp_request "$REQUEST" true
        ;;
    
    "tools")
        print_colored $GREEN "Listing available tools..."
        REQUEST='{
            "jsonrpc": "2.0",
            "id": "tools-1",
            "method": "tools/list",
            "params": {}
        }'
        if check_jq; then
            print_colored $BLUE "=== Available Tools ==="
            curl -s -X POST "$MCP_URL" \
                -H "$CONTENT_TYPE" \
                -d "$REQUEST" | jq '.result.tools[] | {name: .name, description: .description}'
        else
            make_mcp_request "$REQUEST" false
        fi
        ;;
    
    "call")
        if [ -z "$2" ]; then
            print_colored $RED "Error: Tool name required for 'call' command"
            echo "Usage: $0 call <tool_name> [arguments_json]"
            exit 1
        fi
        
        TOOL_NAME="$2"
        ARGUMENTS="${3:-{}}"
        
        print_colored $GREEN "Calling tool: $TOOL_NAME"
        REQUEST="{
            \"jsonrpc\": \"2.0\",
            \"id\": \"call-1\",
            \"method\": \"tools/call\",
            \"params\": {
                \"name\": \"$TOOL_NAME\",
                \"arguments\": $ARGUMENTS
            }
        }"
        extract_tool_result "$REQUEST"
        ;;
    
    "health")
        print_colored $GREEN "Checking database health..."
        REQUEST='{
            "jsonrpc": "2.0",
            "id": "health-1",
            "method": "tools/call",
            "params": {
                "name": "check_database_health",
                "arguments": {}
            }
        }'
        extract_tool_result "$REQUEST"
        ;;
    
    "databases")
        print_colored $GREEN "Getting database list..."
        REQUEST='{
            "jsonrpc": "2.0",
            "id": "db-1",
            "method": "tools/call",
            "params": {
                "name": "get_databases",
                "arguments": {}
            }
        }'
        extract_tool_result "$REQUEST"
        ;;
    
    "tables")
        DATABASE="${2:-}"
        if [ -n "$DATABASE" ]; then
            ARGS="{\"database\": \"$DATABASE\"}"
            print_colored $GREEN "Getting tables for database: $DATABASE"
        else
            ARGS="{}"
            print_colored $GREEN "Getting tables for current database..."
        fi
        
        REQUEST="{
            \"jsonrpc\": \"2.0\",
            \"id\": \"tables-1\",
            \"method\": \"tools/call\",
            \"params\": {
                \"name\": \"get_tables\",
                \"arguments\": $ARGS
            }
        }"
        extract_tool_result "$REQUEST"
        ;;
    
    "describe")
        if [ -z "$2" ] || [ -z "$3" ]; then
            print_colored $RED "Error: Database and table name required"
            echo "Usage: $0 describe <database> <table> [schema]"
            exit 1
        fi
        
        DATABASE="$2"
        TABLE="$3"
        SCHEMA="${4:-public}"
        
        print_colored $GREEN "Describing table: $DATABASE.$SCHEMA.$TABLE"
        REQUEST="{
            \"jsonrpc\": \"2.0\",
            \"id\": \"describe-1\",
            \"method\": \"tools/call\",
            \"params\": {
                \"name\": \"describe_table\",
                \"arguments\": {
                    \"database\": \"$DATABASE\",
                    \"table\": \"$TABLE\",
                    \"schema\": \"$SCHEMA\"
                }
            }
        }"
        extract_tool_result "$REQUEST"
        ;;
    
    "preview")
        if [ -z "$2" ] || [ -z "$3" ]; then
            print_colored $RED "Error: Database and table name required"
            echo "Usage: $0 preview <database> <table> [schema] [limit]"
            exit 1
        fi
        
        DATABASE="$2"
        TABLE="$3"
        SCHEMA="${4:-public}"
        LIMIT="${5:-5}"
        
        print_colored $GREEN "Previewing table: $DATABASE.$SCHEMA.$TABLE (limit: $LIMIT)"
        REQUEST="{
            \"jsonrpc\": \"2.0\",
            \"id\": \"preview-1\",
            \"method\": \"tools/call\",
            \"params\": {
                \"name\": \"preview_table_data\",
                \"arguments\": {
                    \"database\": \"$DATABASE\",
                    \"table\": \"$TABLE\",
                    \"schema\": \"$SCHEMA\",
                    \"limit\": $LIMIT
                }
            }
        }"
        extract_tool_result "$REQUEST"
        ;;
    
    "sql")
        if [ -z "$2" ] || [ -z "$3" ]; then
            print_colored $RED "Error: Database and SQL query required"
            echo "Usage: $0 sql <database> '<sql_query>' [limit]"
            exit 1
        fi
        
        DATABASE="$2"
        QUERY="$3"
        LIMIT="${4:-50}"
        
        print_colored $GREEN "Executing SQL on database: $DATABASE"
        print_colored $YELLOW "Query: $QUERY"
        REQUEST="{
            \"jsonrpc\": \"2.0\",
            \"id\": \"sql-1\",
            \"method\": \"tools/call\",
            \"params\": {
                \"name\": \"execute_sql_query\",
                \"arguments\": {
                    \"database\": \"$DATABASE\",
                    \"query\": \"$QUERY\",
                    \"limit\": $LIMIT
                }
            }
        }"
        extract_tool_result "$REQUEST"
        ;;
    
    "help"|*)
        print_colored $BLUE "MCP Testing Helper Script"
        echo ""
        echo "Usage: $0 <command> [arguments]"
        echo ""
        echo "Commands:"
        echo "  init                           - Initialize MCP connection"
        echo "  tools                          - List available tools"
        echo "  health                         - Check database health"
        echo "  databases                      - List all databases"
        echo "  tables [database]              - List tables (optionally for specific database)"
        echo "  describe <db> <table> [schema] - Describe table structure"
        echo "  preview <db> <table> [schema] [limit] - Preview table data"
        echo "  sql <db> '<query>' [limit]     - Execute SQL query"
        echo "  call <tool_name> [args_json]   - Call any tool with custom arguments"
        echo "  help                           - Show this help"
        echo ""
        echo "Examples:"
        echo "  $0 tools"
        echo "  $0 databases"
        echo "  $0 tables postgres"
        echo "  $0 describe postgres users"
        echo "  $0 preview postgres users public 10"
        echo "  $0 sql postgres 'SELECT version()'"
        echo "  $0 call get_database_size '{\"database\": \"postgres\"}'"
        echo ""
        print_colored $YELLOW "Note: Install jq for better JSON formatting: brew install jq"
        ;;
esac
