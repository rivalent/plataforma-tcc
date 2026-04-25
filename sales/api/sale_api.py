from sales.repository.sqlite_sales_repository import SqliteSalesRepository
from sales.schema.sales_schema import SaleCreateRequest, SaleItemCreateRequest
from sales.service.sales_service import SalesService
from sales.gateway.api_gateway import APIGateway
from sales.exceptions import (
    SaleNotFound, DatabaseError, ClientIntegrationError,
    ProductIntegrationError, InsufficientStockIntegration,
    ExternalServiceUnavailable, InvalidSaleState,
    EmptySaleCannotBeCompleted
)
from shared.database import SqliteManager
from shared.response_formatter import format_response
from time import time
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

router = APIRouter()
gateway = APIGateway()
manager = SqliteManager("sales/database", "db_sales.db")
repo = SqliteSalesRepository(manager)
service = SalesService(repo, gateway)

@router.post('/sales', status_code=status.HTTP_201_CREATED)
def create_sale(sale_data: SaleCreateRequest):
    start_time = time()
    try:
        items_list = []
        for item in sale_data.items:
            
            formatted_item = {
                "product_id": item.product_id,
                "quantity": item.quantity
            }

            items_list.append(formatted_item)

        new_sale = service.save_sale(
            client_id = sale_data.client_id,
            items_data = items_list
        )

        return format_response(
            data=new_sale, 
            start_time=start_time, 
            message="Sale successfully created"
        )

    except (ClientIntegrationError, ProductIntegrationError) as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=format_response(start_time=start_time, message="Request failed", error=str(e))
        )
    except InsufficientStockIntegration as e:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=format_response(start_time=start_time, message="Request failed", error=str(e))
        )
    except ExternalServiceUnavailable as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=format_response(start_time=start_time, message="External service unavailable", error=str(e))
        )
    except SaleNotFound as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content=format_response(start_time=start_time, message="Request failed", error=str(e))
        )
    except DatabaseError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            content=format_response(start_time=start_time, message="Internal server error", error=str(e))
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, 
            content=format_response(start_time=start_time, message="Bad request", error=str(e))
        )

@router.get('/sales/{sale_id}', status_code=status.HTTP_200_OK)
def get_sale_by_id(sale_id: str):
    start_time = time()
    try:
        sale = service.get_sale_by_id(sale_id)

        return format_response(
            data=sale, 
            start_time=start_time, 
            message="Sale successfully retrieved"
        )

    except SaleNotFound as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content=format_response(start_time=start_time, message="Request failed", error=str(e))
        )
    except DatabaseError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            content=format_response(start_time=start_time, message="Internal server error", error=str(e))
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, 
            content=format_response(start_time=start_time, message="Bad request", error=str(e))
        )

@router.get('/sales/product/{product_id}', status_code=status.HTTP_200_OK)
def get_sales_by_product_id(product_id: str):
    start_time = time()
    try:
        sales = service.get_sale_by_product_id(product_id)

        return format_response(
            data=sales, 
            start_time=start_time, 
            message="Sales successfully retrieved for the given product ID"
        )

    except DatabaseError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            content=format_response(start_time=start_time, message="Internal server error", error=str(e))
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, 
            content=format_response(start_time=start_time, message="Bad request", error=str(e))
        )

@router.get('/sales/status/{status}', status_code=status.HTTP_200_OK)
def get_sales_by_status(status: int):
    start_time = time()
    try:
        sales = service.get_sale_by_status(status)

        return format_response(
            data=sales, 
            start_time=start_time, 
            message="Sales successfully retrieved for the given status"
        )

    except DatabaseError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            content=format_response(start_time=start_time, message="Internal server error", error=str(e))
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, 
            content=format_response(start_time=start_time, message="Bad request", error=str(e))
        )

@router.get('/sales/count/product/{product_id}/status/{status}', status_code=status.HTTP_200_OK)
def count_sales_by_product_and_status(product_id: str, status: int):
    start_time = time()
    try:
        count = service.count_sales_by_product_and_status(product_id, status)

        return format_response(
            data={"total_sales": count},
            start_time=start_time, 
            message="Sales count successfully retrieved"
        )

    except DatabaseError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            content=format_response(start_time=start_time, message="Internal server error", error=str(e))
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, 
            content=format_response(start_time=start_time, message="Bad request", error=str(e))
        )

@router.put('/sales/{sale_id}/finish', status_code=status.HTTP_200_OK)
def finish_sale(sale_id: str):
    start_time = time()
    try:
        result = service.finish_sale(sale_id)

        return format_response(
            data=result, 
            start_time=start_time, 
            message="Sale completed, stock updated, and prices calculated successfully"
        )

    except SaleNotFound as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=format_response(start_time=start_time, message="Sale not found", error=str(e))
        )
    except InvalidSaleState as e:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=format_response(start_time=start_time, message="Invalid sale state", error=str(e))
        )
    except EmptySaleCannotBeCompleted as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=format_response(start_time=start_time, message="Cannot complete sale", error=str(e))
        )
    except (ProductIntegrationError, ClientIntegrationError) as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=format_response(start_time=start_time, message="Request failed", error=str(e))
        )
    except InsufficientStockIntegration as e:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=format_response(start_time=start_time, message="Insufficient stock", error=str(e))
        )
    except ExternalServiceUnavailable as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=format_response(start_time=start_time, message="External service unavailable", error=str(e))
        )
    except DatabaseError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=format_response(start_time=start_time, message="Internal server error", error=str(e))
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=format_response(start_time=start_time, message="The sale could not be completed", error=str(e))
        )

@router.put('/sales/{sale_id}/cancel', status_code=status.HTTP_200_OK)
def cancel_sale(sale_id: str):
    start_time = time()
    try:
        canceled_sale = service.cancel_sale(sale_id)

        return format_response(
            data=canceled_sale, 
            start_time=start_time, 
            message="Sale canceled successfully"
        )

    except SaleNotFound as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=format_response(start_time=start_time, message="Sale not found", error=str(e))
        )
    except InvalidSaleState as e:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=format_response(start_time=start_time, message="Invalid sale state", error=str(e))
        )
    except ExternalServiceUnavailable as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=format_response(start_time=start_time, message="External service unavailable", error=str(e))
        )
    except DatabaseError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=format_response(start_time=start_time, message="Internal server error", error=str(e))
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=format_response(start_time=start_time, message="The sale could not be canceled", error=str(e))
        )
