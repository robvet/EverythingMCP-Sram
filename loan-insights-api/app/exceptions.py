from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from typing import Any, Dict

class DatabaseError(HTTPException):
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(status_code=500, detail=detail)

class ValidationError(HTTPException):
    def __init__(self, detail: str = "Invalid input data"):
        super().__init__(status_code=422, detail=detail)

def handle_db_error(error: SQLAlchemyError) -> HTTPException:
    """Convert SQLAlchemy errors to HTTP exceptions"""
    error_msg = str(error)
    if "connection" in error_msg.lower():
        return HTTPException(
            status_code=503,
            detail="Database connection failed. Please try again later."
        )
    elif "timeout" in error_msg.lower():
        return HTTPException(
            status_code=504,
            detail="Database query timeout. Please try again with fewer results."
        )
    else:
        return HTTPException(
            status_code=500,
            detail="Internal database error occurred."
        )