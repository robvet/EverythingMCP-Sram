from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from app.database import get_db
from app.models.loan import LoanResponse, LoanSummaryResponse, InsightResponse
from app.services.insights import LoanInsightsService

router = APIRouter(prefix="/loans", tags=["loans"])

@router.get("/", response_model=List[LoanResponse])
async def get_loans(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    status: Optional[str] = Query(None, description="Filter by loan status"),
    min_credit_score: Optional[int] = Query(None, ge=300, le=850, description="Minimum credit score"),
    max_credit_score: Optional[int] = Query(None, ge=300, le=850, description="Maximum credit score"),
    home_ownership: Optional[str] = Query(None, description="Filter by home ownership"),
    purpose: Optional[str] = Query(None, description="Filter by loan purpose"),
    db: Session = Depends(get_db)
):
    """Get loans with optional filters"""
    query = text("""
        SELECT id, loan_id, customer_id, status, amount, term, credit_score, 
               years_employment, home_ownership, annual_income, purpose, 
               monthly_debt, risk_score
        FROM loans_clean 
        WHERE 1=1
        {status_filter}
        {credit_score_filter}
        {home_ownership_filter}
        {purpose_filter}
        ORDER BY id
        LIMIT :limit OFFSET :skip
    """.format(
        status_filter="AND status = :status" if status else "",
        credit_score_filter="AND credit_score BETWEEN :min_credit_score AND :max_credit_score" if min_credit_score or max_credit_score else "",
        home_ownership_filter="AND home_ownership = :home_ownership" if home_ownership else "",
        purpose_filter="AND purpose = :purpose" if purpose else ""
    ))
    
    params = {"skip": skip, "limit": limit}
    if status:
        params["status"] = status
    if min_credit_score:
        params["min_credit_score"] = min_credit_score
    if max_credit_score:
        params["max_credit_score"] = max_credit_score
    if home_ownership:
        params["home_ownership"] = home_ownership
    if purpose:
        params["purpose"] = purpose
        
    results = db.execute(query, params).fetchall()
    
    return [
        LoanResponse(
            id=row.id,
            loan_id=row.loan_id,
            customer_id=row.customer_id,
            status=row.status,
            amount=float(row.amount) if row.amount else None,
            term=row.term,
            credit_score=row.credit_score,
            years_employment=row.years_employment,
            home_ownership=row.home_ownership,
            annual_income=float(row.annual_income) if row.annual_income else None,
            purpose=row.purpose,
            monthly_debt=float(row.monthly_debt) if row.monthly_debt else None,
            risk_score=row.risk_score
        ) for row in results
    ]

@router.get("/summary", response_model=List[LoanSummaryResponse])
async def get_loan_summary(
    db: Session = Depends(get_db)
):
    """Get loan summary statistics"""
    query = text("""
        SELECT status, term, home_ownership, purpose, loan_count, 
               avg_credit_score, avg_amount, avg_income, avg_monthly_debt, avg_risk_score
        FROM loan_summary
        ORDER BY loan_count DESC
        LIMIT 50
    """)
    
    results = db.execute(query).fetchall()
    
    return [
        LoanSummaryResponse(
            status=row.status,
            term=row.term,
            home_ownership=row.home_ownership,
            purpose=row.purpose,
            loan_count=row.loan_count,
            avg_credit_score=float(row.avg_credit_score) if row.avg_credit_score else None,
            avg_amount=float(row.avg_amount) if row.avg_amount else None,
            avg_income=float(row.avg_income) if row.avg_income else None,
            avg_monthly_debt=float(row.avg_monthly_debt) if row.avg_monthly_debt else None,
            avg_risk_score=float(row.avg_risk_score) if row.avg_risk_score else None
        ) for row in results
    ]

@router.get("/insights/default-rates", response_model=List[InsightResponse])
async def get_default_rate_insights(
    category: str = Query(..., description="Category: credit_score_range, home_ownership, or purpose"),
    db: Session = Depends(get_db)
):
    """Get default rate insights by category"""
    if category not in ["credit_score_range", "home_ownership", "purpose"]:
        raise HTTPException(status_code=400, detail="Invalid category. Choose from: credit_score_range, home_ownership, purpose")
    
    return LoanInsightsService.get_default_rate_by_category(db, category)

@router.get("/insights/risk-analysis", response_model=List[InsightResponse])
async def get_risk_analysis(
    db: Session = Depends(get_db)
):
    """Get comprehensive risk analysis insights"""
    return LoanInsightsService.get_risk_analysis(db)

@router.get("/insights/portfolio", response_model=List[InsightResponse])
async def get_portfolio_metrics(
    db: Session = Depends(get_db)
):
    """Get portfolio performance metrics"""
    return LoanInsightsService.get_portfolio_metrics(db)

@router.get("/stats")
async def get_basic_stats(
    db: Session = Depends(get_db)
):
    """Get basic statistics about the loan portfolio"""
    query = text("""
        SELECT 
            COUNT(*) as total_loans,
            COUNT(DISTINCT customer_id) as unique_customers,
            COUNT(CASE WHEN status = 'Fully Paid' THEN 1 END) as fully_paid_count,
            COUNT(CASE WHEN status = 'Charged Off' THEN 1 END) as charged_off_count,
            ROUND(AVG(credit_score), 0) as avg_credit_score,
            ROUND(AVG(amount), 2) as avg_loan_amount,
            ROUND(AVG(annual_income), 2) as avg_annual_income,
            MIN(credit_score) as min_credit_score,
            MAX(credit_score) as max_credit_score
        FROM loans_clean
        WHERE credit_score IS NOT NULL AND amount IS NOT NULL AND annual_income IS NOT NULL
    """)
    
    result = db.execute(query).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="No data found")
    
    return {
        "total_loans": result.total_loans,
        "unique_customers": result.unique_customers,
        "fully_paid_count": result.fully_paid_count,
        "charged_off_count": result.charged_off_count,
        "default_rate_percentage": round((result.charged_off_count / result.total_loans) * 100, 2),
        "avg_credit_score": int(result.avg_credit_score),
        "avg_loan_amount": float(result.avg_loan_amount),
        "avg_annual_income": float(result.avg_annual_income),
        "credit_score_range": {
            "min": result.min_credit_score,
            "max": result.max_credit_score
        }
    }