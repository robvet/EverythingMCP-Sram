from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routers import loans
import os

app = FastAPI(
    title="Loan Insights API",
    description="API for generating insights about loan portfolio data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(loans.router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Loan Insights API",
        "version": "1.0.0",
        "description": "API for generating insights about loan portfolio data",
        "endpoints": {
            "loans": "/api/v1/loans",
            "loan_summary": "/api/v1/loans/summary",
            "basic_stats": "/api/v1/loans/stats",
            "default_rates": "/api/v1/loans/insights/default-rates",
            "risk_analysis": "/api/v1/loans/insights/risk-analysis",
            "portfolio_metrics": "/api/v1/loans/insights/portfolio"
        },
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "loan-insights-api"}

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    
    uvicorn.run(app, host=host, port=port)