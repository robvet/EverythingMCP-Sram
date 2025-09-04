from sqlalchemy import Column, Integer, String, Numeric, DateTime, func
from pydantic import BaseModel
from typing import Optional
from app.database import Base

class LoanClean(Base):
    __tablename__ = "loans_clean"
    
    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(String)
    customer_id = Column(String)
    status = Column(String)
    amount = Column(Numeric)
    term = Column(String)
    credit_score = Column(Integer)
    years_employment = Column(String)
    home_ownership = Column(String)
    annual_income = Column(Numeric)
    purpose = Column(String)
    monthly_debt = Column(Numeric)
    years_credit_history = Column(Numeric)
    months_last_delinquent = Column(Integer)
    open_accounts = Column(Integer)
    credit_problems = Column(Integer)
    credit_balance = Column(Numeric)
    open_credit = Column(Numeric)
    bankruptcies = Column(Integer)
    tax_liens = Column(Integer)
    months_last_delinquent_new = Column(Integer)
    credit_problems_new = Column(Integer)
    purpose_new = Column(String)
    risk_score = Column(Integer)
    created_at = Column(DateTime, default=func.now())

class LoanResponse(BaseModel):
    id: int
    loan_id: Optional[str]
    customer_id: Optional[str]
    status: str
    amount: Optional[float]
    term: Optional[str]
    credit_score: Optional[int]
    years_employment: Optional[str]
    home_ownership: Optional[str]
    annual_income: Optional[float]
    purpose: Optional[str]
    monthly_debt: Optional[float]
    risk_score: Optional[int]
    
    class Config:
        from_attributes = True

class LoanSummaryResponse(BaseModel):
    status: str
    term: Optional[str]
    home_ownership: Optional[str]
    purpose: Optional[str]
    loan_count: int
    avg_credit_score: Optional[float]
    avg_amount: Optional[float]
    avg_income: Optional[float]
    avg_monthly_debt: Optional[float]
    avg_risk_score: Optional[float]

class InsightResponse(BaseModel):
    insight_type: str
    description: str
    value: float
    additional_info: Optional[dict] = None