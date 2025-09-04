# EverythingMCP - Comprehensive Model Context Protocol Implementation

A complete enterprise ecosystem for Model Context Protocol (MCP) servers with multiple implementations including PostgreSQL database tools, loan insights API, and Azure AI Foundation integration.

## 📁 Project Structure

```
EverythingMCP/
├── enhanced-postgresql-mcp/        # Enterprise PostgreSQL MCP Server
├── fastmcpimplementation/          # FastMCP Framework Implementation
├── loan-insights-api/              # REST API for loan portfolio analytics  
├── AzureFoundryAgent/             # Azure AI Foundation agent integration
├── CopilotStudio/                 # Copilot Studio configuration files
├── claude_desktop_config.json     # Claude Desktop MCP configuration
├── loansclean.csv                 # Sample loan portfolio dataset
└── samplepolicy.xml               # APIM policy sample
```

## 🌟 Key Components

### 1. Enhanced PostgreSQL MCP Server
**Location**: `enhanced-postgresql-mcp/`

Enterprise-grade MCP server with 10 comprehensive PostgreSQL tools:

#### ✨ Features
- **10 PostgreSQL Tools**: Database inspection, statistics, monitoring, and data preview
- **Enterprise Security**: SQL injection prevention, input validation, read-only operations
- **Performance**: Async connection pooling (5-20 connections), query timeout protection
- **Production Ready**: Structured logging, Kubernetes health probes, Docker containerization

#### 🛠️ Available Tools
1. `get_databases` - List all databases with size information
2. `get_tables` - List tables with statistics and size info
3. `describe_table` - Detailed table structure and constraints
4. `get_indexes` - Index information for tables
5. `get_table_stats` - Comprehensive table statistics
6. `get_database_size` - Database size analytics
7. `preview_table_data` - Safe data preview (max 10 rows)
8. `count_table_rows` - Accurate row counts
9. `get_active_connections` - Connection monitoring
10. `check_database_health` - System health checks

#### 🚀 Quick Start
```bash
cd enhanced-postgresql-mcp
cp .env.example .env
# Edit .env with your database credentials
pip install -r requirements.txt
python -m app.main
```

#### 🐳 Docker Deployment
```bash
docker build -t enhanced-postgresql-mcp .
docker run -d -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
  enhanced-postgresql-mcp
```

### 2. FastMCP Implementation
**Location**: `fastmcpimplementation/`

Alternative implementation using the FastMCP framework with enhanced features:

#### ✨ Features
- **FastMCP Framework**: Lightweight, fast implementation
- **Enhanced Database Manager**: Advanced connection pooling and monitoring
- **HTTP & STDIO Support**: Dual transport modes
- **Enhanced Logging**: Comprehensive request/response logging
- **Health Monitoring**: Periodic health checks and pool statistics

#### 🚀 Usage
```bash
cd fastmcpimplementation
pip install -r requirements.txt

# STDIO mode (default)
python fastmcp.py

# HTTP mode
python fastmcp.py --http 8001 localhost
```

### 3. Loan Insights API
**Location**: `loan-insights-api/`

RESTful API for loan portfolio analytics with 174,693 loan records:

#### 📊 API Features
- **Portfolio Analytics**: Default rates, risk analysis, performance metrics
- **Data Access**: Filtered loan data with pagination
- **Business Insights**: Credit score analysis, risk factors, portfolio performance
- **OpenAPI Spec**: Complete documentation with examples

#### 🔗 Live Deployment
- **Base URL**: `https://your-loan-insights-api.azurecontainerapps.io`
- **Documentation**: `/docs` endpoint
- **Health Check**: `/health` endpoint

#### 📈 Key Insights
- **Overall Default Rate**: 26.08% (45,557 defaults out of 174,693 loans)
- **Credit Score Impact**: Poor (<650): 53.57% vs Excellent (750+): 5.36%
- **Average Credit Score**: 722 (range: 585-751)

#### 🚀 Usage Examples
```bash
# Get portfolio statistics
curl "https://your-loan-insights-api.azurecontainerapps.io/api/v1/loans/stats"

# Get risk analysis
curl "https://your-loan-insights-api.azurecontainerapps.io/api/v1/loans/insights/risk-analysis"

# Get filtered loans
curl "https://your-loan-insights-api.azurecontainerapps.io/api/v1/loans?min_credit_score=750&limit=10"
```

### 4. Azure AI Foundation Agent
**Location**: `AzureFoundryAgent/`

Integration with Azure AI Foundation for MCP-enabled AI agents:

#### ✨ Features
- **Semantic Kernel Integration**: Azure AI agent framework
- **MCP Tool Configuration**: Automatic tool discovery and execution
- **Tool Approval Handling**: Secure tool execution workflow
- **Enhanced Error Handling**: Comprehensive logging and debugging

#### 🚀 Usage
```bash
cd AzureFoundryAgent
cp .env.example .env
# Configure Azure credentials and MCP endpoints
python semantic_kernel_agent.py
```

### 5. Copilot Studio Configuration
**Location**: `CopilotStudio/`

Configuration files for Microsoft Copilot Studio MCP integration:

#### 📄 Files
- `mcpschemaapim.yaml` - OpenAPI schema for APIM-backed MCP server
- `apim-mcp-policy.xml` - Azure API Management policies
- `loan-insights-api.yaml` - API specification for loan insights

#### 🔐 Security Configuration
```yaml
securityDefinitions:
  apiKeyHeader:
    type: apiKey
    name: Ocp-Apim-Subscription-Key
    in: header
```

## ⚙️ Configuration

### Environment Variables
Create `.env` files in each component directory:

#### PostgreSQL MCP Server
```env
DATABASE_URL=postgresql://username:password@host:5432/database
DB_MIN_CONNECTIONS=5
DB_MAX_CONNECTIONS=20
LOG_LEVEL=INFO
DEBUG=false
QUERY_TIMEOUT_SECONDS=30
MAX_PREVIEW_ROWS=10
```

#### Azure AI Foundation Agent  
```env
PROJECT_ENDPOINT=https://your-project.openai.azure.com
MCP_SERVER_URL=https://your-mcp-server.com
MCP_SERVER_LABEL=PostgreSQL MCP Server
MCP_SUBSCRIPTION_KEY=your-subscription-key
```

### Claude Desktop Configuration
Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "postgresql-mcp": {
      "command": "python",
      "args": ["/path/to/enhanced-postgresql-mcp/app/main.py"],
      "env": {
        "DATABASE_URL": "postgresql://user:pass@host:5432/db"
      }
    }
  }
}
```

## 🔐 Security Features

### SQL Injection Prevention
- Parameterized queries for all database operations
- Input validation with regex patterns
- Identifier sanitization (alphanumeric + underscore only)
- Query result size limits

### Authentication & Authorization
- API key authentication for APIM-backed servers
- Subscription key validation
- Read-only database operations
- Schema access restrictions

### Error Handling
- Sanitized error messages (no sensitive data exposure)
- Comprehensive logging with request tracking
- Graceful degradation on failures

## 📊 Monitoring & Health Checks

### Health Endpoints
- `/health` - Comprehensive health check with database status
- `/health/ready` - Kubernetes readiness probe  
- `/health/live` - Kubernetes liveness probe

### Metrics & Logging
- Structured JSON logging
- Request/response timing
- Database connection pool metrics
- Tool execution statistics
- Error rate monitoring

## 🚀 Deployment Options

### 1. Azure Container Apps (Recommended)
```bash
# Build and push
docker build -t myregistry.azurecr.io/mcp-server:latest .
docker push myregistry.azurecr.io/mcp-server:latest

# Deploy
az containerapp create \
  --name postgresql-mcp-server \
  --resource-group myResourceGroup \
  --environment myContainerEnvironment \
  --image myregistry.azurecr.io/mcp-server:latest \
  --target-port 8000 \
  --ingress external \
  --env-vars DATABASE_URL="postgresql://..."
```

### 2. Docker Compose
```yaml
version: '3.8'
services:
  mcp-server:
    build: ./enhanced-postgresql-mcp
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:pass@postgres:5432/mydb
    depends_on:
      - postgres
      
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
```

### 3. Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python -m app.main

# Or with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🧪 Testing

### Unit Tests
```bash
# PostgreSQL MCP Server
cd enhanced-postgresql-mcp
pytest tests/ -v --cov=app

# Loan Insights API
cd loan-insights-api
pytest tests/ -v
```

### Integration Testing
```bash
# Test MCP protocol
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "tools/list",
    "params": {}
  }'

# Test tool execution
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0", 
    "id": "2",
    "method": "tools/call",
    "params": {
      "name": "get_databases",
      "arguments": {}
    }
  }'
```

## 📈 Performance Optimization

### Database Optimization
- Connection pooling with configurable limits
- Query timeout protection
- Efficient system catalog queries
- Result pagination for large datasets

### Application Optimization
- Async/await throughout the stack
- Memory-efficient processing
- Structured error handling
- Request deduplication

### Scaling Considerations
- Stateless server design
- Horizontal scaling ready
- Container-native architecture
- Resource limit configuration

## 🛣️ Architecture Patterns

### 1. MCP Protocol Compliance
- JSON-RPC 2.0 standard implementation
- Tool discovery and execution
- Error handling as per MCP specification
- Capability negotiation

### 2. Enterprise Patterns
- Repository pattern for data access
- Factory pattern for tool creation
- Observer pattern for monitoring
- Strategy pattern for different implementations

### 3. Cloud-Native Design
- 12-factor app compliance
- Health check endpoints
- Graceful shutdown handling
- Configuration via environment variables

## 🔧 Development Guide

### Adding New Tools
1. Extend `PostgreSQLToolsManager` in respective implementation
2. Add tool method with proper validation
3. Register tool in `_register_tools()` method
4. Add comprehensive tests
5. Update documentation

### Custom Implementations
1. Implement `MCPProtocolHandler` interface
2. Create tool manager extending base class
3. Add transport layer (HTTP/STDIO)
4. Implement health checks
5. Add monitoring and logging

## 🚨 Troubleshooting

### Common Issues

#### Database Connection Failures
```bash
# Check connection string
DATABASE_URL=postgresql://user:pass@host:5432/db

# Test connection
psql "postgresql://user:pass@host:5432/db" -c "SELECT 1"
```

#### MCP Protocol Errors
```bash
# Enable debug logging
LOG_LEVEL=DEBUG
DEBUG=true

# Check MCP request format
{
  "jsonrpc": "2.0",
  "id": "unique-id",
  "method": "tools/list",
  "params": {}
}
```

#### Performance Issues
```bash
# Increase connection pool
DB_MAX_CONNECTIONS=30

# Optimize query timeout
QUERY_TIMEOUT_SECONDS=60

# Monitor pool usage
curl http://localhost:8000/health
```

## 📚 API Documentation

### PostgreSQL MCP Server
- **Live Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`
- **Tools List**: `http://localhost:8000/tools`

### Loan Insights API
- **Live Docs**: `https://your-loan-insights-api.azurecontainerapps.io/docs`
- **OpenAPI Spec**: `https://your-loan-insights-api.azurecontainerapps.io/openapi.json`

## 🤝 Contributing

### Development Setup
```bash
git clone <repository>
cd EverythingMCP

# Set up each component
for dir in enhanced-postgresql-mcp fastmcpimplementation loan-insights-api; do
  cd $dir
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  cd ..
done
```

### Code Standards
- Python 3.11+ required
- Type hints throughout
- Comprehensive docstrings
- Unit test coverage >80%
- Security-first approach

## 📄 License

MIT License - see individual component directories for specific licensing information.

## 🚀 Getting Started

1. **Choose Your Implementation**:
   - Enterprise features → `enhanced-postgresql-mcp/`
   - Lightweight/Fast → `fastmcpimplementation/`
   - API analytics → `loan-insights-api/`

2. **Set Up Environment**:
   ```bash
   cp .env.example .env
   # Edit with your configuration
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Server**:
   ```bash
   python -m app.main  # or appropriate entry point
   ```

5. **Test the Integration**:
   ```bash
   curl http://localhost:8000/health
   ```

---

**🎉 You now have a complete MCP ecosystem with enterprise PostgreSQL tools, loan analytics API, and Azure AI Foundation integration!**

For specific component documentation, see the README files in each subdirectory.
