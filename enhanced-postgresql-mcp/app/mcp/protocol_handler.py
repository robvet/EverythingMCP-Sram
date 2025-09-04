"""
MCP Protocol Handler
Handles Model Context Protocol communication following the official specification
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class MCPProtocolHandler:
    """Handles MCP protocol methods and routing"""
    
    def __init__(self, tools_manager):
        self.tools_manager = tools_manager
        self.protocol_version = "2024-11-05"
        self.server_info = {
            "name": "enhanced-postgresql-mcp",
            "version": "2.0.0",
            "description": "Enterprise-grade PostgreSQL MCP server"
        }
        self.initialized = False
        self.client_info = None
        
    async def handle_request(self, method: str, params: Dict[str, Any], request_id: Optional[str] = None) -> Dict[str, Any]:
        """Route MCP method to appropriate handler"""
        
        logger.info(f"Handling MCP method: {method}")
        
        # Route to appropriate method handler
        if method == "initialize":
            return await self._handle_initialize(params)
        elif method == "initialized":
            return await self._handle_initialized(params)
        elif method == "tools/list":
            return await self._handle_tools_list(params)
        elif method == "tools/call":
            return await self._handle_tools_call(params)
        elif method == "ping":
            return await self._handle_ping(params)
        elif method == "logging/setLevel":
            return await self._handle_logging_set_level(params)
        elif method == "notifications/initialized":
            return await self._handle_notifications_initialized(params)
        elif method == "prompts/list":
            return await self._handle_prompts_list(params)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    async def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request"""
        logger.info("Handling initialize request")
        
        # Validate required parameters
        if "protocolVersion" not in params:
            raise ValueError("Missing required parameter: protocolVersion")
        
        client_protocol_version = params["protocolVersion"]
        
        # Check protocol compatibility
        if client_protocol_version != self.protocol_version:
            logger.warning(f"Protocol version mismatch: client={client_protocol_version}, server={self.protocol_version}")
        
        # Store client information
        self.client_info = params.get("clientInfo", {})
        
        # Mark as initialized
        self.initialized = True
        
        logger.info(f"Initialized with client: {self.client_info}")
        
        return {
            "protocolVersion": self.protocol_version,
            "serverInfo": self.server_info,
            "capabilities": {
                "tools": {},
                "resources": {},
                "prompts": {},
                "logging": {}
            }
        }
    
    async def _handle_initialized(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialized notification"""
        logger.info("Client initialization complete")
        return {}
    
    async def _handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request"""
        if not self.initialized:
            raise ValueError("Session not initialized. Call 'initialize' first.")
        
        logger.info("Handling tools/list request")
        
        tools = await self.tools_manager.get_all_tools()
        
        return {
            "tools": tools
        }
    
    async def _handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request"""
        if not self.initialized:
            raise ValueError("Session not initialized. Call 'initialize' first.")
        
        # Validate required parameters
        if "name" not in params:
            raise ValueError("Missing required parameter: name")
        
        tool_name = params["name"]
        tool_arguments = params.get("arguments", {})
        
        logger.info(f"Calling tool: {tool_name} with arguments: {tool_arguments}")
        
        # Execute the tool
        result = await self.tools_manager.execute_tool(tool_name, tool_arguments)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": result
                }
            ]
        }
    
    async def _handle_ping(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ping request for connectivity testing"""
        return {
            "status": "pong",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "server": self.server_info["name"]
        }
    
    async def _handle_logging_set_level(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle logging/setLevel request"""
        level = params.get("level", "info")
        logger.info(f"Setting log level to: {level}")
        # Note: In a production implementation, you would actually set the logging level
        # For now, we'll just acknowledge the request
        return {}
    
    async def _handle_notifications_initialized(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle notifications/initialized notification"""
        logger.info("Client has completed initialization")
        # This is a notification, so we return an empty response
        return {}
    
    async def _handle_prompts_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prompts/list request"""
        # This server doesn't provide any prompts, so return empty list
        return {
            "prompts": []
        }