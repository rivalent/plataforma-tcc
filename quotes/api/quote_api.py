from quotes.repository.sqlite_quote_repository import SqliteQuoteRepository
from quotes.service.quote_service import QuoteService
from quotes.exceptions import DatabaseError, QuoteServiceUnavailable
from shared.response_formatter import format_response
from shared.database import SqliteManager
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from time import time

router = APIRouter()
manager = SqliteManager("quotes/database", "db_quotes.db")
repo = SqliteQuoteRepository(manager)
service = QuoteService(repo)

@router.get('/quotes/{code}', status_code=status.HTTP_200_OK)
def get_quote_by_code(code: str):
    start_time = time()
    try:
        quote = service.get_quote(code)

        return format_response(
            data=quote, 
            start_time=start_time, 
            message="Quote retrieved successfully"
        )

    except QuoteServiceUnavailable as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            content=format_response(start_time=start_time, message="Quote service unavailable", error=str(e))
        )
    
    except DatabaseError as e:
        return JSONResponse(
             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
             content=format_response(start_time=start_time, message="Internal server error", error=str(e))
        )
    except Exception as e:
        return JSONResponse(
             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
             content=format_response(start_time=start_time, message="Unexpected error", error=str(e))
        )

@router.get('/quotes', status_code=status.HTTP_200_OK)
def get_all_quotes():
    start_time = time()
    try:
        expected_currencies = ["USD", "EUR", "GBP", "CNY"]
        all_quotes = [service.get_quote(code) for code in expected_currencies]

        return format_response(
            data=all_quotes, 
            start_time=start_time, 
            message="All quotes retrieved successfully"
        )

    except QuoteServiceUnavailable as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            content=format_response(start_time=start_time, message="Quote service unavailable", error=str(e))
        )
    except DatabaseError as e:
        return JSONResponse(
             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
             content=format_response(start_time=start_time, message="Internal server error", error=str(e))
        )
    except Exception as e:
        return JSONResponse(
             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
             content=format_response(start_time=start_time, message="Unexpected error", error=str(e))
        )