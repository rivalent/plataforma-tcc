from products.repository.sqlite_product_repository import SqliteProductRepository
from products.service.product_service import ProductService
from products.gateway.quotes_gateway import QuotesGateway
from products.schema.product_schema import ProductCreateRequest, ProductUpdateRequest, ProductStockUpdateRequest
from products.exceptions import ProductNotFound, DatabaseError, UnsupportedCurrency
from shared.response_formatter import format_response
from shared.database import SqliteManager
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from time import time

router = APIRouter()
manager = SqliteManager("products/database", "db_products.db")
repo = SqliteProductRepository(manager)
quotes_gateway = QuotesGateway("http://quotes-api:8000")
service = ProductService(repo, quotes_gateway)

@router.post('/products', status_code=status.HTTP_201_CREATED)
def create_product(product_data: ProductCreateRequest):
    start_time = time()
    try:
        new_product = service.create_product(
            name = product_data.name,
            desc = product_data.desc,
            price = product_data.price,
            quantity = product_data.quantity
        )

        return format_response(
            data=new_product, 
            start_time=start_time, 
            message="Product successfully created"
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

@router.get('/products/search', status_code=status.HTTP_200_OK)
def search_products(min_price: float = None, max_price: float = None, name_or_desc: str = None, min_quantity: int = None, currency: str = None):
    start_time = time()
    try:
        results = service.search(min_price, max_price, name_or_desc, min_quantity, currency)

        return format_response(
            data=results, 
            start_time=start_time, 
            message="Product search completed successfully"
        )

    except UnsupportedCurrency as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=format_response(start_time=start_time, message="Bad request", error=str(e))
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

@router.get('/products/{product_id}', status_code=status.HTTP_200_OK)
def get_product_by_id(product_id: str):
    start_time = time()
    try:
        product = service.get_by_id(product_id)

        return format_response(
            data=product, 
            start_time=start_time, 
            message="Product retrieved successfully"
        )

    except ProductNotFound as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content=format_response(start_time=start_time, message="Product not found", error=str(e))
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

@router.put('/products/{product_id}', status_code=status.HTTP_200_OK)
def update_product(product_id: str, product_data: ProductUpdateRequest):
    start_time = time()
    try:
        updated_product = service.update_product(product_id, product_data)

        return format_response(
            data=updated_product, 
            start_time=start_time, 
            message="Product updated successfully"
        )

    except ProductNotFound as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content=format_response(start_time=start_time, message="Product not found", error=str(e))
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

@router.put('/products/{product_id}/stock', status_code=status.HTTP_200_OK)
def update_product_stock(product_id: str, stock_data: ProductStockUpdateRequest):
    start_time = time()
    try:
        service.update_stock(product_id, stock_data.quantity)
        updated_product = service.get_by_id(product_id)

        return format_response(
            data=updated_product, 
            start_time=start_time, 
            message="Stock updated successfully via Integration."
        )

    except ProductNotFound as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content=format_response(start_time=start_time, message="Product not found!", error=str(e))
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            content=format_response(start_time=start_time, message="Internal Error", error=str(e))
        )

@router.delete('/products/{product_id}', status_code=status.HTTP_200_OK)
def delete_product(product_id: str):
    start_time = time()
    try:
        service.delete_product(product_id)

        return format_response(
            start_time=start_time, 
            message="Product deleted successfully"
        )

    except ProductNotFound as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content=format_response(start_time=start_time, message="Product not found", error=str(e))
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