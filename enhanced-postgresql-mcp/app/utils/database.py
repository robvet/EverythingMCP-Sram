"""
Database Connection Manager
Enterprise-grade PostgreSQL connection management with pooling
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
import asyncpg
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages PostgreSQL database connections with connection pooling"""
    
    def __init__(self, database_url: str, min_connections: int = 5, max_connections: int = 20):
        self.database_url = database_url
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.pool: Optional[asyncpg.Pool] = None
        
    async def initialize(self):
        """Initialize database connection pool"""
        try:
            logger.info("Initializing database connection pool...")
            
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=self.min_connections,
                max_size=self.max_connections,
                command_timeout=30,
                server_settings={
                    'application_name': 'enhanced_postgresql_mcp',
                    'jit': 'off'  # Disable JIT for better predictability
                }
            )
            
            # Test the connection
            await self.check_health()
            
            logger.info(f"Database pool initialized with {self.min_connections}-{self.max_connections} connections")
            
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            logger.info("Closing database connection pool...")
            await self.pool.close()
            logger.info("Database pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool (context manager)"""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        
        connection = None
        try:
            connection = await self.pool.acquire()
            yield connection
        finally:
            if connection:
                await self.pool.release(connection)
    
    async def execute_query(self, query: str, params: List[Any] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results as list of dictionaries"""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        
        async with self.get_connection() as conn:
            try:
                # Execute query with parameters
                if params:
                    rows = await conn.fetch(query, *params)
                else:
                    rows = await conn.fetch(query)
                
                # Convert to list of dictionaries
                results = []
                for row in rows:
                    result_dict = {}
                    for key, value in row.items():
                        result_dict[key] = value
                    results.append(result_dict)
                
                return results
                
            except Exception as e:
                logger.error(f"Database query failed: {e}")
                logger.error(f"Query: {query}")
                logger.error(f"Params: {params}")
                raise
    
    async def execute_single_query(self, query: str, params: List[Any] = None) -> Optional[Dict[str, Any]]:
        """Execute a query and return single result as dictionary"""
        results = await self.execute_query(query, params)
        return results[0] if results else None
    
    async def check_health(self) -> Dict[str, Any]:
        """Check database health and connection status"""
        try:
            # Test basic connectivity
            result = await self.execute_single_query("SELECT 1 as health_check, version(), current_timestamp")
            
            if result and result.get('health_check') == 1:
                # Get pool statistics
                pool_stats = {
                    "status": "healthy",
                    "version": result.get("version", "unknown"),
                    "current_time": result.get("current_timestamp"),
                    "pool_size": self.pool.get_size() if self.pool else 0,
                    "pool_available": self.pool.get_idle_size() if self.pool else 0,
                    "pool_max": self.max_connections,
                    "pool_min": self.min_connections
                }
                
                return pool_stats
            else:
                return {"status": "unhealthy", "error": "Health check query failed"}
                
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    async def get_pool_stats(self) -> Dict[str, Any]:
        """Get detailed connection pool statistics"""
        if not self.pool:
            return {"error": "Pool not initialized"}
        
        return {
            "pool_size": self.pool.get_size(),
            "idle_connections": self.pool.get_idle_size(),
            "max_connections": self.max_connections,
            "min_connections": self.min_connections,
            "pool_status": "active" if self.pool else "inactive"
        }
    
    async def execute_query_on_database(self, database_name: str, query: str, params: List[Any] = None) -> List[Dict[str, Any]]:
        """Execute a query on a specific database by creating a temporary connection"""
        # Parse the base URL and replace the database name
        base_url = self.database_url.rsplit('/', 1)[0]  # Remove database name
        target_db_url = f"{base_url}/{database_name}"
        
        # Create temporary connection to target database
        temp_conn = None
        try:
            temp_conn = await asyncpg.connect(target_db_url)
            
            # Execute query
            if params:
                rows = await temp_conn.fetch(query, *params)
            else:
                rows = await temp_conn.fetch(query)
            
            # Convert to list of dictionaries
            results = []
            for row in rows:
                result_dict = {}
                for key, value in row.items():
                    result_dict[key] = value
                results.append(result_dict)
            
            return results
            
        except Exception as e:
            logger.error(f"Database query failed on {database_name}: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
        finally:
            if temp_conn:
                await temp_conn.close()

    async def test_query_performance(self, query: str, params: List[Any] = None) -> Dict[str, Any]:
        """Test query performance and return timing information"""
        import time
        
        start_time = time.time()
        
        try:
            results = await self.execute_query(query, params)
            end_time = time.time()
            
            return {
                "success": True,
                "execution_time_seconds": round(end_time - start_time, 4),
                "rows_returned": len(results),
                "query": query[:100] + "..." if len(query) > 100 else query
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "execution_time_seconds": round(end_time - start_time, 4),
                "error": str(e),
                "query": query[:100] + "..." if len(query) > 100 else query
            }