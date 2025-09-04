"""
Enhanced PostgreSQL Tools Manager
Comprehensive set of safe, read-only PostgreSQL database tools
"""

import json
import logging
import re
from typing import Dict, Any, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class PostgreSQLToolsManager:
    """Manages PostgreSQL database tools with enterprise features"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.tools = {}
        
    async def initialize(self):
        """Initialize tools manager"""
        logger.info("Initializing PostgreSQL tools manager...")
        await self._register_tools()
        logger.info(f"Registered {len(self.tools)} PostgreSQL tools")
    
    async def _register_tools(self):
        """Register all available PostgreSQL tools"""
        
        # Database schema tools
        self.tools["get_databases"] = {
            "name": "get_databases",
            "description": "List all PostgreSQL databases with size information",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        }
        
        self.tools["get_tables"] = {
            "name": "get_tables",
            "description": "List all tables in a specific database and schema with size and row count information",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "Name of the database to query (optional, uses current connection if not provided)"
                    },
                    "schema": {
                        "type": "string",
                        "description": "Schema name (optional, defaults to 'public')",
                        "default": "public"
                    }
                },
                "required": [],
                "additionalProperties": False
            }
        }
        
        self.tools["describe_table"] = {
            "name": "describe_table",
            "description": "Get detailed information about table structure, columns, and constraints",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "Name of the database"
                    },
                    "table": {
                        "type": "string",
                        "description": "Name of the table to describe"
                    },
                    "schema": {
                        "type": "string",
                        "description": "Schema name (optional, defaults to 'public')",
                        "default": "public"
                    }
                },
                "required": ["database", "table"],
                "additionalProperties": False
            }
        }
        
        self.tools["get_indexes"] = {
            "name": "get_indexes",
            "description": "List all indexes for a specific table",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "Name of the database"
                    },
                    "table": {
                        "type": "string",
                        "description": "Name of the table"
                    },
                    "schema": {
                        "type": "string",
                        "description": "Schema name (optional, defaults to 'public')",
                        "default": "public"
                    }
                },
                "required": ["database", "table"],
                "additionalProperties": False
            }
        }
        
        # Database statistics tools
        self.tools["get_table_stats"] = {
            "name": "get_table_stats",
            "description": "Get comprehensive statistics for a table including size, row counts, and activity",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "Name of the database"
                    },
                    "table": {
                        "type": "string",
                        "description": "Name of the table"
                    },
                    "schema": {
                        "type": "string",
                        "description": "Schema name (optional, defaults to 'public')",
                        "default": "public"
                    }
                },
                "required": ["database", "table"],
                "additionalProperties": False
            }
        }
        
        self.tools["get_database_size"] = {
            "name": "get_database_size",
            "description": "Get size information for databases",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "Name of specific database (optional, shows all if not provided)"
                    }
                },
                "additionalProperties": False
            }
        }
        
        # Data preview tools
        self.tools["preview_table_data"] = {
            "name": "preview_table_data",
            "description": "Preview first few rows of a table (limited to 10 rows for safety)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "Name of the database"
                    },
                    "table": {
                        "type": "string",
                        "description": "Name of the table"
                    },
                    "schema": {
                        "type": "string",
                        "description": "Schema name (optional, defaults to 'public')",
                        "default": "public"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of rows to return (max 10)",
                        "minimum": 1,
                        "maximum": 10,
                        "default": 5
                    }
                },
                "required": ["database", "table"],
                "additionalProperties": False
            }
        }
        
        self.tools["count_table_rows"] = {
            "name": "count_table_rows",
            "description": "Get accurate row count for a table",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "Name of the database"
                    },
                    "table": {
                        "type": "string",
                        "description": "Name of the table"
                    },
                    "schema": {
                        "type": "string",
                        "description": "Schema name (optional, defaults to 'public')",
                        "default": "public"
                    }
                },
                "required": ["database", "table"],
                "additionalProperties": False
            }
        }
        
        # System monitoring tools
        self.tools["get_active_connections"] = {
            "name": "get_active_connections",
            "description": "Show current active database connections (limited to 50 for safety)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "Filter by specific database (optional)"
                    }
                },
                "additionalProperties": False
            }
        }
        
        self.tools["check_database_health"] = {
            "name": "check_database_health",
            "description": "Perform basic health check of the PostgreSQL database",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        }
        
        # SQL Query execution tool (with safety limits)
        self.tools["execute_sql_query"] = {
            "name": "execute_sql_query",
            "description": "Execute a custom SQL query (read-only operations only, limited to 100 rows for safety)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "Name of the database to execute query against"
                    },
                    "query": {
                        "type": "string",
                        "description": "SQL query to execute (SELECT statements only for safety)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of rows to return (max 100)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 50
                    }
                },
                "required": ["database", "query"],
                "additionalProperties": False
            }
        }
    
    async def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get all available tools"""
        return list(self.tools.values())
    
    async def get_tools_count(self) -> int:
        """Get count of available tools"""
        return len(self.tools)
    
    def _validate_identifier(self, identifier: str, name: str = "identifier") -> None:
        """Validate database identifier to prevent SQL injection"""
        if not identifier:
            raise ValueError(f"{name} cannot be empty")
        
        if not re.match(r'^[a-zA-Z0-9_]+$', identifier):
            raise ValueError(f"{name} contains invalid characters. Only letters, numbers, and underscores allowed.")
        
        if len(identifier) > 63:  # PostgreSQL identifier limit
            raise ValueError(f"{name} too long (max 63 characters)")
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a specific tool with given arguments"""
        
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        logger.info(f"Executing tool: {tool_name} with args: {arguments}")
        
        try:
            # Route to appropriate tool method
            if tool_name == "get_databases":
                result = await self._get_databases()
            elif tool_name == "get_tables":
                result = await self._get_tables(arguments)
            elif tool_name == "describe_table":
                result = await self._describe_table(arguments)
            elif tool_name == "get_indexes":
                result = await self._get_indexes(arguments)
            elif tool_name == "get_table_stats":
                result = await self._get_table_stats(arguments)
            elif tool_name == "get_database_size":
                result = await self._get_database_size(arguments)
            elif tool_name == "preview_table_data":
                result = await self._preview_table_data(arguments)
            elif tool_name == "count_table_rows":
                result = await self._count_table_rows(arguments)
            elif tool_name == "get_active_connections":
                result = await self._get_active_connections(arguments)
            elif tool_name == "check_database_health":
                result = await self._check_database_health()
            elif tool_name == "execute_sql_query":
                result = await self._execute_sql_query(arguments)
            else:
                raise ValueError(f"Tool {tool_name} not implemented")
            
            # Format result as JSON string
            return json.dumps(result, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            error_result = {
                "error": str(e),
                "tool": tool_name,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            return json.dumps(error_result, indent=2)
    
    # Tool implementations
    async def _get_databases(self) -> Dict[str, Any]:
        """Get list of databases with size information"""
        query = """
        SELECT 
            datname as database_name,
            pg_size_pretty(pg_database_size(datname)) as size_pretty,
            pg_database_size(datname) as size_bytes,
            datcollate as collation,
            datctype as character_type
        FROM pg_database 
        WHERE datistemplate = false
        ORDER BY pg_database_size(datname) DESC;
        """
        
        results = await self.db_manager.execute_query(query)
        
        return {
            "databases": results,
            "total_count": len(results),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _get_tables(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get list of tables in database and schema"""
        database = args.get("database")
        schema = args.get("schema", "public")
        
        self._validate_identifier(schema, "schema")
        if database:
            self._validate_identifier(database, "database")
        
        query = """
        SELECT 
            t.table_name,
            t.table_type,
            pg_size_pretty(pg_total_relation_size(quote_ident(t.table_schema)||'.'||quote_ident(t.table_name))) as size_pretty,
            pg_total_relation_size(quote_ident(t.table_schema)||'.'||quote_ident(t.table_name)) as size_bytes,
            s.n_live_tup as estimated_rows,
            s.last_analyze,
            s.last_autoanalyze
        FROM information_schema.tables t
        LEFT JOIN pg_stat_user_tables s ON s.relname = t.table_name AND s.schemaname = t.table_schema
        WHERE t.table_schema = $1
        AND t.table_type = 'BASE TABLE'
        ORDER BY pg_total_relation_size(quote_ident(t.table_schema)||'.'||quote_ident(t.table_name)) DESC NULLS LAST;
        """
        
        try:
            if database:
                # Query specific database
                results = await self.db_manager.execute_query_on_database(database, query, [schema])
                target_database = database
            else:
                # Query current database
                results = await self.db_manager.execute_query(query, [schema])
                current_db_result = await self.db_manager.execute_query("SELECT current_database() as db_name")
                target_database = current_db_result[0]["db_name"] if current_db_result else "unknown"
            
            return {
                "database": target_database,
                "schema": schema,
                "tables": results,
                "total_count": len(results),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "error": f"Failed to get tables: {str(e)}",
                "database": database or "current",
                "schema": schema,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def _describe_table(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed table structure"""
        database = args["database"]
        table = args["table"] 
        schema = args.get("schema", "public")
        
        self._validate_identifier(database, "database")
        self._validate_identifier(table, "table")
        self._validate_identifier(schema, "schema")
        
        # Get column information
        columns_query = """
        SELECT 
            column_name,
            data_type,
            character_maximum_length,
            numeric_precision,
            numeric_scale,
            is_nullable,
            column_default,
            ordinal_position
        FROM information_schema.columns 
        WHERE table_catalog = $1 
        AND table_name = $2 
        AND table_schema = $3
        ORDER BY ordinal_position;
        """
        
        columns = await self.db_manager.execute_query_on_database(database, columns_query, [database, table, schema])
        
        # Get constraints information
        constraints_query = """
        SELECT 
            tc.constraint_name,
            tc.constraint_type,
            kcu.column_name,
            ccu.table_name as foreign_table_name,
            ccu.column_name as foreign_column_name
        FROM information_schema.table_constraints tc
        LEFT JOIN information_schema.key_column_usage kcu 
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        LEFT JOIN information_schema.constraint_column_usage ccu 
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        WHERE tc.table_catalog = $1 
        AND tc.table_name = $2 
        AND tc.table_schema = $3;
        """
        
        constraints = await self.db_manager.execute_query_on_database(database, constraints_query, [database, table, schema])
        
        return {
            "database": database,
            "schema": schema,
            "table": table,
            "columns": columns,
            "constraints": constraints,
            "column_count": len(columns),
            "constraint_count": len(constraints),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _get_indexes(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get indexes for a table"""
        database = args["database"]
        table = args["table"]
        schema = args.get("schema", "public")
        
        self._validate_identifier(database, "database")
        self._validate_identifier(table, "table") 
        self._validate_identifier(schema, "schema")
        
        query = """
        SELECT 
            indexname as index_name,
            indexdef as index_definition,
            tablespace,
            CASE 
                WHEN indexdef LIKE '%UNIQUE%' THEN true 
                ELSE false 
            END as is_unique
        FROM pg_indexes 
        WHERE tablename = $1 
        AND schemaname = $2;
        """
        
        results = await self.db_manager.execute_query_on_database(database, query, [table, schema])
        
        return {
            "database": database,
            "schema": schema, 
            "table": table,
            "indexes": results,
            "index_count": len(results),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _get_table_stats(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive table statistics"""
        database = args["database"]
        table = args["table"]
        schema = args.get("schema", "public")
        
        self._validate_identifier(database, "database")
        self._validate_identifier(table, "table")
        self._validate_identifier(schema, "schema")
        
        query = """
        SELECT 
            schemaname,
            tablename,
            n_tup_ins as total_inserts,
            n_tup_upd as total_updates,
            n_tup_del as total_deletes,
            n_live_tup as live_rows,
            n_dead_tup as dead_rows,
            n_tup_hot_upd as hot_updates,
            n_mod_since_analyze as modifications_since_analyze,
            last_vacuum,
            last_autovacuum,
            last_analyze,
            last_autoanalyze,
            vacuum_count,
            autovacuum_count,
            analyze_count,
            autoanalyze_count
        FROM pg_stat_user_tables 
        WHERE tablename = $1 
        AND schemaname = $2;
        """
        
        results = await self.db_manager.execute_query_on_database(database, query, [table, schema])
        
        if not results:
            return {
                "error": f"Table {schema}.{table} not found or no statistics available",
                "database": database,
                "schema": schema,
                "table": table
            }
        
        return {
            "database": database,
            "statistics": results[0],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _get_database_size(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get database size information"""
        specific_db = args.get("database")
        
        if specific_db:
            self._validate_identifier(specific_db, "database")
            query = """
            SELECT 
                datname as database_name,
                pg_size_pretty(pg_database_size(datname)) as size_pretty,
                pg_database_size(datname) as size_bytes
            FROM pg_database 
            WHERE datname = $1 AND datistemplate = false;
            """
            results = await self.db_manager.execute_query(query, [specific_db])
        else:
            query = """
            SELECT 
                datname as database_name,
                pg_size_pretty(pg_database_size(datname)) as size_pretty,
                pg_database_size(datname) as size_bytes
            FROM pg_database 
            WHERE datistemplate = false
            ORDER BY pg_database_size(datname) DESC;
            """
            results = await self.db_manager.execute_query(query)
        
        total_size = sum(row['size_bytes'] for row in results) if results else 0
        
        return {
            "databases": results,
            "total_databases": len(results),
            "total_size_pretty": self._format_bytes(total_size),
            "total_size_bytes": total_size,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _preview_table_data(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Preview table data (limited rows for safety)"""
        database = args["database"]
        table = args["table"]
        schema = args.get("schema", "public")
        limit = min(args.get("limit", 5), 10)  # Max 10 rows for safety
        
        self._validate_identifier(database, "database")
        self._validate_identifier(table, "table")
        self._validate_identifier(schema, "schema")
        
        # Use parameterized query for safety
        query = f"SELECT * FROM {schema}.{table} LIMIT $1"
        
        try:
            results = await self.db_manager.execute_query_on_database(database, query, [limit])
            
            return {
                "database": database,
                "schema": schema,
                "table": table,
                "rows_returned": len(results),
                "limit_applied": limit,
                "data": results,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "error": f"Failed to preview table data: {str(e)}",
                "database": database,
                "schema": schema,
                "table": table
            }
    
    async def _count_table_rows(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get exact row count for table"""
        database = args["database"]
        table = args["table"]
        schema = args.get("schema", "public")
        
        self._validate_identifier(database, "database")
        self._validate_identifier(table, "table")
        self._validate_identifier(schema, "schema")
        
        query = f"SELECT COUNT(*) as row_count FROM {schema}.{table}"
        
        try:
            results = await self.db_manager.execute_query_on_database(database, query)
            row_count = results[0]['row_count'] if results else 0
            
            return {
                "database": database,
                "schema": schema,
                "table": table,
                "row_count": row_count,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "error": f"Failed to count table rows: {str(e)}",
                "database": database,
                "schema": schema,
                "table": table
            }
    
    async def _get_active_connections(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get active database connections"""
        specific_db = args.get("database")
        
        query = """
        SELECT 
            pid,
            usename as username,
            datname as database_name,
            application_name,
            client_addr,
            client_port,
            backend_start,
            query_start,
            state,
            state_change
        FROM pg_stat_activity 
        WHERE state = 'active' 
        AND pid <> pg_backend_pid()
        """
        
        params = []
        if specific_db:
            self._validate_identifier(specific_db, "database")
            query += " AND datname = $1"
            params.append(specific_db)
        
        query += " ORDER BY query_start DESC LIMIT 50"
        
        results = await self.db_manager.execute_query(query, params)
        
        return {
            "active_connections": results,
            "connection_count": len(results),
            "filtered_by_database": specific_db,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Perform basic database health check"""
        try:
            # Test basic connectivity
            test_query = "SELECT version(), current_timestamp, pg_is_in_recovery()"
            result = await self.db_manager.execute_query(test_query)
            
            if result:
                version_info = result[0]
                
                # Get database stats
                stats_query = """
                SELECT 
                    COUNT(*) as total_connections,
                    COUNT(CASE WHEN state = 'active' THEN 1 END) as active_connections
                FROM pg_stat_activity
                """
                stats = await self.db_manager.execute_query(stats_query)
                
                return {
                    "status": "healthy",
                    "database_version": version_info.get("version", "unknown"),
                    "current_time": version_info.get("current_timestamp"),
                    "is_standby": version_info.get("pg_is_in_recovery", False),
                    "connections": stats[0] if stats else {},
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": "No response from database",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        except Exception as e:
            return {
                "status": "unhealthy", 
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def _execute_sql_query(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a custom SQL query with safety restrictions"""
        database = args["database"]
        query = args["query"].strip()
        limit = min(args.get("limit", 50), 100)  # Max 100 rows for safety
        
        self._validate_identifier(database, "database")
        
        # Safety checks - only allow SELECT statements
        query_upper = query.upper().strip()
        if not query_upper.startswith('SELECT'):
            return {
                "error": "Only SELECT queries are allowed for safety reasons",
                "database": database,
                "query": query[:100] + "..." if len(query) > 100 else query
            }
        
        # Check for potentially dangerous operations
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'TRUNCATE', 'CREATE']
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return {
                    "error": f"Query contains potentially dangerous keyword: {keyword}",
                    "database": database,
                    "query": query[:100] + "..." if len(query) > 100 else query
                }
        
        # Add limit to query if not present
        if 'LIMIT' not in query_upper:
            query = f"{query.rstrip(';')} LIMIT {limit}"
        
        try:
            start_time = datetime.now(timezone.utc)
            # Use the multi-database method to query the specified database
            results = await self.db_manager.execute_query_on_database(database, query)
            end_time = datetime.now(timezone.utc)
            execution_time = (end_time - start_time).total_seconds()
            
            return {
                "database": database,
                "query": query,
                "results": results,
                "row_count": len(results) if results else 0,
                "execution_time_seconds": round(execution_time, 3),
                "timestamp": end_time.isoformat()
            }
        except Exception as e:
            return {
                "error": f"Query execution failed: {str(e)}",
                "database": database,
                "query": query[:200] + "..." if len(query) > 200 else query,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes to human readable string"""
        if bytes_value == 0:
            return "0 B"
        
        units = ["B", "KB", "MB", "GB", "TB"]
        unit_index = 0
        size = float(bytes_value)
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.2f} {units[unit_index]}"