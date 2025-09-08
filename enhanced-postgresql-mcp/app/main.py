"""
Enhanced PostgreSQL MCP Server
Enterprise-grade MCP server with comprehensive PostgreSQL tools
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
import asyncio
import json
import logging
import time
from datetime import datetime

from .mcp.protocol_handler import MCPProtocolHandler
from .mcp.postgresql_tools import PostgreSQLToolsManager
from .utils.database import DatabaseManager
from .utils.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get configuration
settings = get_settings()

# Initialize FastAPI app
app = FastAPI(
    title="Enhanced PostgreSQL MCP Server",
    description="Enterprise-grade MCP server with comprehensive PostgreSQL database tools",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize components
db_manager = DatabaseManager(settings.database_url)
tools_manager = PostgreSQLToolsManager(db_manager)
mcp_handler = MCPProtocolHandler(tools_manager)

@app.on_event("startup")
async def startup_event():
    """Initialize database connections and components"""
    logger.info("Starting Enhanced PostgreSQL MCP Server...")
    
    logger.info(f"DATABASE_URL being used: {settings.database_url}")  # Add this

    await db_manager.initialize()
    await tools_manager.initialize()
    logger.info("Server initialization complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources"""
    logger.info("Shutting down Enhanced PostgreSQL MCP Server...")
    await db_manager.close()
    logger.info("Shutdown complete")

# Request/Response Models
class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    method: str
    params: Optional[Dict[str, Any]] = {}

class MCPSuccessResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    result: Dict[str, Any]

class MCPErrorResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    error: Dict[str, Any]

# Union type for response
MCPResponse = Union[MCPSuccessResponse, MCPErrorResponse]

@app.get("/")
async def root():
    """Root endpoint with server information"""
    return {
        "message": "Enhanced PostgreSQL MCP Server",
        "version": "2.0.0",
        "description": "Enterprise-grade MCP server with comprehensive PostgreSQL tools",
        "endpoints": {
            "/mcp": "POST - MCP JSON-RPC endpoint",
            "/health": "GET - Health check endpoint", 
            "/health/ready": "GET - Readiness check endpoint",
            "/health/live": "GET - Liveness check endpoint",
            "/tools": "GET - List available tools",
            "/docs": "GET - API documentation",
        },
        "protocol_version": "2024-11-05",
        "tools_count": await tools_manager.get_tools_count()
    }

@app.post("/mcp", response_model=MCPResponse)
async def mcp_endpoint(request: MCPRequest):
    """Main MCP protocol endpoint"""
    start_time = time.time()
    
    try:
        logger.info(f"MCP request: {request.method} with params: {request.params}")
        
        # Process MCP request through protocol handler
        result = await mcp_handler.handle_request(
            method=request.method,
            params=request.params or {},
            request_id=request.id
        )
        
        response = MCPSuccessResponse(
            id=request.id,
            result=result
        )
        
        processing_time = time.time() - start_time
        logger.info(f"MCP request processed in {processing_time:.3f}s")
        
        return response
        
    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        return MCPErrorResponse(
            id=request.id,
            error={
                "code": -32602,
                "message": "Invalid params",
                "data": {"details": str(e)}
            }
        )
    except Exception as e:
        logger.error(f"Internal error processing MCP request: {e}")
        return MCPErrorResponse(
            id=request.id,
            error={
                "code": -32603,
                "message": "Internal error",
                "data": {"details": str(e) if settings.debug else "Internal server error"}
            }
        )

@app.get("/health")
async def health_check():
    """Basic health check"""
    try:
        db_status = await db_manager.check_health()
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "server": "Enhanced PostgreSQL MCP Server",
            "version": "2.0.0",
            "database": db_status,
            "tools_available": await tools_manager.get_tools_count()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/health/ready")
async def readiness_check():
    """Kubernetes readiness probe"""
    try:
        await db_manager.check_health()
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="Not ready")

@app.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}

@app.get("/tools")
async def list_tools():
    """List all available PostgreSQL tools"""
    try:
        tools = await tools_manager.get_all_tools()
        return {
            "tools_count": len(tools),
            "tools": tools
        }
    except Exception as e:
        logger.error(f"Failed to list tools: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve tools")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000,
        reload=settings.debug,
        log_level="info"
    )