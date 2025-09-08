# Enhanced PostgreSQL MCP Server

Enterprise-grade Model Context Protocol (MCP) server for PostgreSQL database operations with comprehensive tooling, connection pooling, and production-ready features.

## ✨ Features

### 🛠️ Comprehensive PostgreSQL Tools (10 Tools)
- **Schema Inspection**: `get_databases`, `get_tables`, `describe_table`, `get_indexes`
- **Statistics & Monitoring**: `get_table_stats`, `get_database_size`, `count_table_rows`
- **Data Preview**: `preview_table_data` (safety-limited)
- **System Monitoring**: `get_active_connections`, `check_database_health`

### 🔒 Enterprise Security
- SQL injection prevention with input validation
- Parameter sanitization for all queries
- Read-only operations for data safety
- Error handling without information leakage

### ⚡ Performance & Reliability
- Async connection pooling with asyncpg
- Configurable connection limits (5-20 connections)
- Query timeout protection
- Comprehensive health checks

### 📊 Production Ready
- Structured JSON logging
- Kubernetes-ready health probes (`/health/live`, `/health/ready`)
- Docker containerization
- Environment-based configuration

## 🏗️ Architecture

```
Enhanced PostgreSQL MCP Server
├── MCP Protocol Handler (Standards Compliant)
├── PostgreSQL Tools Manager (10 Tools)
├── Database Manager (Connection Pooling)
└── FastAPI Web Framework
```

## 🚀 Quick Start

### 1. Clone and Setup
```bash
cd /Users/sreeram/workspace/EverythingMCP/enhanced-postgresql-mcp
cp .env.example .env
# Edit .env with your database credentials
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Database
```bash
# Edit .env file
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

### 4. Run Server
```bash
python -m app.main
# Or with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Test MCP Protocol
```bash
curl -X POST http://localhost:8000/mcp \\
  -H "Content-Type: application/json" \\
  -d '{
    "jsonrpc": "2.0",
    "id": "1", 
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "test-client", "version": "1.0.0"}
    }
  }'
```

## 🛠️ Available Tools

### Database Schema Tools

#### `get_databases`
List all PostgreSQL databases with size information.
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {"name": "get_databases", "arguments": {}}
}
```

#### `get_tables` 
List tables in a database with size and statistics.
```json
{
  "jsonrpc": "2.0", 
  "method": "tools/call",
  "params": {
    "name": "get_tables",
    "arguments": {"database": "test_db", "schema": "public"}
  }
}
```

#### `describe_table`
Get detailed table structure including columns and constraints.
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call", 
  "params": {
    "name": "describe_table",
    "arguments": {"database": "mydb", "table": "users"}
  }
}
```

### Statistics & Monitoring Tools

#### `get_table_stats`
Comprehensive table statistics including activity and performance metrics.

#### `get_database_size`  
Database size information across all databases.

#### `count_table_rows`
Exact row count for specific tables.

### Data Preview Tools

#### `preview_table_data`
Preview first few rows (max 10 for safety).
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "preview_table_data", 
    "arguments": {"database": "mydb", "table": "users", "limit": 5}
  }
}
```

### System Monitoring Tools

#### `get_active_connections`
Show current active database connections.

#### `check_database_health`
Comprehensive database health check.

## 🐳 Docker Deployment

### Build Image
```bash
docker build -t enhanced-postgresql-mcp .
```

### Run Container
```bash
docker run -d \\
  --name mcp-server \\
  -p 8000:8000 \\
  -e DATABASE_URL="postgresql://user:pass@host:5432/db" \\
  enhanced-postgresql-mcp
```

### Get the container's IP address for the database firewall
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' enhanced-postgresql-mcp


### Docker Compose (Recommended)
```yaml
version: '3.8'
services:
  mcp-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:pass@postgres:5432/mydb
      LOG_LEVEL: INFO
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/live"]
      interval: 30s
      timeout: 10s
      retries: 3
    depends_on:
      - postgres
      
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## ☁️ Azure Container Apps Deployment

### 1. Build and Push to Registry
```bash
# Build and tag
docker build -t myregistry.azurecr.io/enhanced-mcp:latest .

# Push to Azure Container Registry  
docker push myregistry.azurecr.io/enhanced-mcp:latest
```

### 2. Deploy Container App
```bash
az containerapp create \\
  --name enhanced-postgresql-mcp \\
  --resource-group myResourceGroup \\
  --environment myContainerEnvironment \\
  --image myregistry.azurecr.io/enhanced-mcp:latest \\
  --target-port 8000 \\
  --ingress external \\
  --env-vars \\
    DATABASE_URL=postgresql://user:pass@myserver.postgres.database.azure.com:5432/mydb \\
    LOG_LEVEL=INFO
```

## ⚙️ Configuration

### Environment Variables
```bash
# Required
DATABASE_URL=postgresql://user:pass@host:5432/db

# Server Configuration  
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO

# Database Pool
DB_MIN_CONNECTIONS=5
DB_MAX_CONNECTIONS=20

# Performance
QUERY_TIMEOUT_SECONDS=30
MAX_PREVIEW_ROWS=10

# Security
CORS_ORIGINS=*
RATE_LIMIT_PER_MINUTE=100
```

## 🧪 Testing

### Run Tests
```bash
pytest tests/ -v
```

### Test Coverage
```bash
pytest --cov=app tests/
```

### Load Testing
```bash
# Install wrk or similar tool
wrk -t12 -c400 -d30s --script=load_test.lua http://localhost:8000/mcp
```

## 📊 Monitoring & Health Checks

### Health Endpoints
- `GET /health` - Comprehensive health check with database status
- `GET /health/ready` - Kubernetes readiness probe
- `GET /health/live` - Kubernetes liveness probe

### Metrics (Future Enhancement)
- Request count and latency metrics
- Database connection pool metrics  
- Tool execution statistics
- Error rate monitoring

## 🔐 Security Features

### Input Validation
- SQL identifier validation (alphanumeric + underscore only)
- Parameter length limits
- Query result size limits

### Query Safety
- Parameterized queries prevent SQL injection
- Read-only operations only
- Connection timeout protection
- Error message sanitization

## 🚀 Performance Optimizations

### Connection Pooling
- Async connection pool with 5-20 connections
- Connection reuse and automatic cleanup
- Pool health monitoring

### Query Optimization
- Efficient queries using system catalogs
- Result pagination for large datasets
- Query timeout protection

## 📈 Scalability

### Horizontal Scaling
- Stateless server design
- Database connection pooling
- Container-ready architecture

### Resource Limits
- Configurable connection limits
- Query result size limits
- Memory-efficient async processing

## 🔧 Development

### Project Structure
```
enhanced-postgresql-mcp/
├── app/
│   ├── main.py              # FastAPI application
│   ├── mcp/
│   │   ├── protocol_handler.py  # MCP protocol implementation
│   │   └── postgresql_tools.py  # PostgreSQL tools
│   └── utils/
│       ├── database.py      # Database connection management
│       └── config.py        # Configuration management
├── tests/
├── Dockerfile
├── requirements.txt
└── README.md
```

### Adding New Tools
1. Add tool definition to `PostgreSQLToolsManager._register_tools()`
2. Implement tool method (e.g., `_my_new_tool()`)
3. Add route in `execute_tool()` method
4. Add tests in `tests/test_tools.py`

## 🔄 Migration from Basic MCP Server

### From Server A (postgresql-mcp-fixed)
1. Replace container image with enhanced version
2. Add `DATABASE_URL` environment variable
3. Update health check endpoints if needed
4. Test new tools with existing Copilot Studio configuration

## 📞 Support & Troubleshooting

### Common Issues

#### Connection Pool Exhaustion
```bash
# Increase pool size
DB_MAX_CONNECTIONS=30
```

#### Query Timeouts  
```bash
# Increase timeout
QUERY_TIMEOUT_SECONDS=60
```

#### Memory Usage
```bash
# Reduce pool size and preview limits
DB_MAX_CONNECTIONS=10
MAX_PREVIEW_ROWS=5
```

### Troubleshooting: Container Crashes

If your container starts and then stops/crashes:

1. Check logs:
   ```bash
   docker logs mcp-server
   ```
2. Common issues:
   - Database not reachable (firewall, credentials, network)
   - Missing or incorrect environment variables
   - Application errors at startup
   - Port 8000 already in use on host

3. Fix the root cause, then restart the container.

### Troubleshooting: Database Hostname

If you get DNS errors like `[Errno -2] Name or service not known`:

1. Go to the Azure Portal and copy the exact "Server name" for your PostgreSQL instance.
2. In your `.env` file, ensure the `DATABASE_URL` uses this hostname, e.g.:
   ```
   DATABASE_URL=postgresql://username:password@your-server-name.postgres.database.azure.com:5432/yourdb?sslmode=require
   ```
3. Test DNS from inside a container:
   ```bash
   docker run --rm busybox nslookup your-server-name.postgres.database.azure.com
   ```
   If this fails, check your Docker network and internet access.

4. After correcting, restart your container.

### Troubleshooting: Azure PostgreSQL Firewall and Docker

If your container cannot connect to Azure PostgreSQL:

1. **Get your public IP address** (from the host, not the container):
   ```bash
   curl ifconfig.me
   ```
2. **Go to the Azure Portal** → your PostgreSQL server → Networking/Firewall rules.
3. **Add your public IP** to the allowed list.
4. **Restart your container** and try connecting again.

> **Note:** The container uses the host's public IP for outbound connections. The internal Docker IP is not relevant for Azure firewall rules.

## 🗺️ Roadmap

### Phase 1: Core Enhancement ✅
- [x] 10 comprehensive PostgreSQL tools
- [x] Connection pooling
- [x] MCP protocol compliance
- [x] Docker containerization

### Phase 2: Security & Auth (Future)
- [ ] JWT authentication
- [ ] Role-based access control
- [ ] API key management
- [ ] Rate limiting middleware

### Phase 3: Observability (Future)  
- [ ] Prometheus metrics
- [ ] Distributed tracing
- [ ] Advanced logging
- [ ] Performance dashboards

### Phase 4: Advanced Features (Future)
- [ ] Query result caching
- [ ] Multi-database support
- [ ] Custom tool plugins
- [ ] GraphQL interface

---

**🎉 You now have an enterprise-grade PostgreSQL MCP server with 10 comprehensive tools, connection pooling, and production-ready features!**