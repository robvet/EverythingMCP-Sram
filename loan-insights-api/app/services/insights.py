from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.models.loan import LoanClean, InsightResponse
from typing import List, Dict, Any

class LoanInsightsService:
    
    @staticmethod
    def get_default_rate_by_category(db: Session, category: str) -> List[InsightResponse]:
        """Get default rates by different categories"""
        insights = []
        
        if category == "credit_score_range":
            query = text("""
                SELECT 
                    CASE 
                        WHEN credit_score < 650 THEN 'Poor (< 650)'
                        WHEN credit_score BETWEEN 650 AND 699 THEN 'Fair (650-699)'
                        WHEN credit_score BETWEEN 700 AND 749 THEN 'Good (700-749)'
                        ELSE 'Excellent (750+)'
                    END as score_range,
                    COUNT(*) as total_loans,
                    COUNT(CASE WHEN status = 'Charged Off' THEN 1 END) as defaults,
                    ROUND(
                        COUNT(CASE WHEN status = 'Charged Off' THEN 1 END)::numeric / COUNT(*) * 100, 2
                    ) as default_rate
                FROM loans_clean 
                WHERE credit_score IS NOT NULL
                GROUP BY score_range
                ORDER BY default_rate DESC
            """)
            results = db.execute(query).fetchall()
            
            for row in results:
                insights.append(InsightResponse(
                    insight_type="default_rate_by_credit_score",
                    description=f"Default rate for credit score range {row.score_range}",
                    value=float(row.default_rate),
                    additional_info={
                        "total_loans": row.total_loans,
                        "defaults": row.defaults,
                        "credit_score_range": row.score_range
                    }
                ))
                
        elif category == "home_ownership":
            query = text("""
                SELECT 
                    home_ownership,
                    COUNT(*) as total_loans,
                    COUNT(CASE WHEN status = 'Charged Off' THEN 1 END) as defaults,
                    ROUND(
                        COUNT(CASE WHEN status = 'Charged Off' THEN 1 END)::numeric / COUNT(*) * 100, 2
                    ) as default_rate
                FROM loans_clean 
                WHERE home_ownership IS NOT NULL
                GROUP BY home_ownership
                ORDER BY default_rate DESC
            """)
            results = db.execute(query).fetchall()
            
            for row in results:
                insights.append(InsightResponse(
                    insight_type="default_rate_by_home_ownership",
                    description=f"Default rate for {row.home_ownership} owners",
                    value=float(row.default_rate),
                    additional_info={
                        "total_loans": row.total_loans,
                        "defaults": row.defaults,
                        "home_ownership": row.home_ownership
                    }
                ))
                
        elif category == "purpose":
            query = text("""
                SELECT 
                    purpose,
                    COUNT(*) as total_loans,
                    COUNT(CASE WHEN status = 'Charged Off' THEN 1 END) as defaults,
                    ROUND(
                        COUNT(CASE WHEN status = 'Charged Off' THEN 1 END)::numeric / COUNT(*) * 100, 2
                    ) as default_rate
                FROM loans_clean 
                WHERE purpose IS NOT NULL
                GROUP BY purpose
                HAVING COUNT(*) >= 1000
                ORDER BY default_rate DESC
            """)
            results = db.execute(query).fetchall()
            
            for row in results:
                insights.append(InsightResponse(
                    insight_type="default_rate_by_purpose",
                    description=f"Default rate for {row.purpose} loans",
                    value=float(row.default_rate),
                    additional_info={
                        "total_loans": row.total_loans,
                        "defaults": row.defaults,
                        "purpose": row.purpose
                    }
                ))
        
        return insights
    
    @staticmethod
    def get_risk_analysis(db: Session) -> List[InsightResponse]:
        """Get comprehensive risk analysis insights"""
        insights = []
        
        # High-risk loan characteristics
        query = text("""
            SELECT 
                AVG(CASE WHEN status = 'Charged Off' THEN credit_score END) as avg_default_credit_score,
                AVG(CASE WHEN status = 'Fully Paid' THEN credit_score END) as avg_paid_credit_score,
                AVG(CASE WHEN status = 'Charged Off' THEN amount END) as avg_default_amount,
                AVG(CASE WHEN status = 'Fully Paid' THEN amount END) as avg_paid_amount,
                AVG(CASE WHEN status = 'Charged Off' THEN annual_income END) as avg_default_income,
                AVG(CASE WHEN status = 'Fully Paid' THEN annual_income END) as avg_paid_income
            FROM loans_clean
            WHERE credit_score IS NOT NULL AND amount IS NOT NULL AND annual_income IS NOT NULL
        """)
        result = db.execute(query).fetchone()
        
        if result:
            credit_score_diff = float(result.avg_paid_credit_score - result.avg_default_credit_score)
            insights.append(InsightResponse(
                insight_type="credit_score_risk_differential",
                description="Credit score difference between paid and defaulted loans",
                value=credit_score_diff,
                additional_info={
                    "avg_default_credit_score": float(result.avg_default_credit_score),
                    "avg_paid_credit_score": float(result.avg_paid_credit_score)
                }
            ))
            
            income_ratio = float(result.avg_paid_income / result.avg_default_income)
            insights.append(InsightResponse(
                insight_type="income_risk_ratio",
                description="Income ratio between paid and defaulted loans",
                value=income_ratio,
                additional_info={
                    "avg_default_income": float(result.avg_default_income),
                    "avg_paid_income": float(result.avg_paid_income)
                }
            ))
        
        # Debt-to-income risk analysis
        query = text("""
            SELECT 
                CASE 
                    WHEN (monthly_debt * 12) / annual_income < 0.2 THEN 'Low DTI (< 20%)'
                    WHEN (monthly_debt * 12) / annual_income BETWEEN 0.2 AND 0.35 THEN 'Medium DTI (20-35%)'
                    ELSE 'High DTI (> 35%)'
                END as dti_category,
                COUNT(*) as total_loans,
                COUNT(CASE WHEN status = 'Charged Off' THEN 1 END) as defaults,
                ROUND(
                    COUNT(CASE WHEN status = 'Charged Off' THEN 1 END)::numeric / COUNT(*) * 100, 2
                ) as default_rate
            FROM loans_clean
            WHERE monthly_debt IS NOT NULL AND annual_income IS NOT NULL AND annual_income > 0
            GROUP BY dti_category
            ORDER BY default_rate DESC
        """)
        results = db.execute(query).fetchall()
        
        for row in results:
            insights.append(InsightResponse(
                insight_type="debt_to_income_risk",
                description=f"Default rate for {row.dti_category} debt-to-income ratio",
                value=float(row.default_rate),
                additional_info={
                    "total_loans": row.total_loans,
                    "defaults": row.defaults,
                    "dti_category": row.dti_category
                }
            ))
        
        return insights
    
    @staticmethod
    def get_portfolio_metrics(db: Session) -> List[InsightResponse]:
        """Get overall portfolio performance metrics"""
        insights = []
        
        # Overall default rate
        query = text("""
            SELECT 
                COUNT(*) as total_loans,
                COUNT(CASE WHEN status = 'Charged Off' THEN 1 END) as defaults,
                ROUND(
                    COUNT(CASE WHEN status = 'Charged Off' THEN 1 END)::numeric / COUNT(*) * 100, 2
                ) as overall_default_rate,
                SUM(amount) as total_loan_volume,
                SUM(CASE WHEN status = 'Charged Off' THEN amount ELSE 0 END) as default_amount
            FROM loans_clean
            WHERE amount IS NOT NULL
        """)
        result = db.execute(query).fetchone()
        
        if result:
            insights.append(InsightResponse(
                insight_type="portfolio_default_rate",
                description="Overall portfolio default rate",
                value=float(result.overall_default_rate),
                additional_info={
                    "total_loans": result.total_loans,
                    "defaults": result.defaults,
                    "total_loan_volume": float(result.total_loan_volume),
                    "default_amount": float(result.default_amount)
                }
            ))
            
            loss_rate = float(result.default_amount / result.total_loan_volume * 100)
            insights.append(InsightResponse(
                insight_type="portfolio_loss_rate",
                description="Portfolio loss rate by amount",
                value=loss_rate,
                additional_info={
                    "total_loan_volume": float(result.total_loan_volume),
                    "default_amount": float(result.default_amount)
                }
            ))
        
        # Term analysis
        query = text("""
            SELECT 
                term,
                COUNT(*) as total_loans,
                COUNT(CASE WHEN status = 'Charged Off' THEN 1 END) as defaults,
                ROUND(
                    COUNT(CASE WHEN status = 'Charged Off' THEN 1 END)::numeric / COUNT(*) * 100, 2
                ) as default_rate,
                AVG(amount) as avg_amount
            FROM loans_clean
            WHERE term IS NOT NULL AND amount IS NOT NULL
            GROUP BY term
            ORDER BY default_rate DESC
        """)
        results = db.execute(query).fetchall()
        
        for row in results:
            insights.append(InsightResponse(
                insight_type="term_performance",
                description=f"Performance for {row.term} loans",
                value=float(row.default_rate),
                additional_info={
                    "term": row.term,
                    "total_loans": row.total_loans,
                    "defaults": row.defaults,
                    "avg_amount": float(row.avg_amount)
                }
            ))
        
        return insights