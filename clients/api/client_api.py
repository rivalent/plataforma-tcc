from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from shared.database import SqliteManager
from clients.repository.sqlite_client_repository import SqliteClientRepository
from clients.service.client_service import ClientService
from clients.schema.client_schema import ClientCreateRequest, ClientUpdateRequest
from clients.exceptions import ClientAlreadyExists, InternalServerError, ClientNotFound
from shared.response_formatter import format_response
from time import time

router = APIRouter()
manager = SqliteManager("clients/database", "db_clients.db")
repo = SqliteClientRepository(manager)
service = ClientService(repo)

@router.post('/clients', status_code=status.HTTP_201_CREATED)
def create_client(client_data: ClientCreateRequest):
    start_time = time()
    try:
        new_client = service.register_client(
            name = client_data.name,
            surname = client_data.surname,
            email = client_data.email,
            birthdate = client_data.birthdate
        )

        return format_response(
            data=new_client, 
            start_time=start_time, 
            message="Client successfully registered"
        )

    except ClientAlreadyExists as e:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, 
            content=format_response(start_time=start_time, message="Request failed", error=str(e))
        )
    except InternalServerError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            content=format_response(start_time=start_time, message="Internal server error", error=str(e))
        )

@router.get('/clients', status_code=status.HTTP_200_OK)
def get_all_client():
    start_time = time()
    try:
        clients = service.get_all_client()

        return format_response(
            data=clients, 
            start_time=start_time, 
            message="Client list successfully retrieved"
        )
    
    except InternalServerError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            content=format_response(start_time=start_time, message="Internal server error", error=str(e))
        )

@router.get('/clients/{client_id}', status_code=status.HTTP_200_OK)
def get_client_by_id(client_id: str):
    start_time = time()
    try:
        client = service.get_client_by_id(client_id)

        if not client:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, 
                content=format_response(start_time=start_time, message="Request failed", error="Client not found")
            )

        return format_response(
            data=client, 
            start_time=start_time, 
            message="Client successfully retrieved"
        )

    except InternalServerError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            content=format_response(start_time=start_time, message="Internal server error", error=str(e))
        )
    except ClientNotFound as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content=format_response(start_time=start_time, message="Request failed", error=str(e))
        )

@router.get('/clients/email/{client_email}', status_code=status.HTTP_200_OK)
def get_client_by_email(client_email: str):
    start_time = time()
    try:
        client = service.get_client_by_email(client_email)

        if not client:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, 
                content=format_response(start_time=start_time, message="Request failed", error="Client not found")
            )

        return format_response(
            data=client, 
            start_time=start_time, 
            message="Client successfully retrieved"
        )

    except InternalServerError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            content=format_response(start_time=start_time, message="Internal server error", error=str(e))
        )

@router.put('/clients/{client_id}', status_code=status.HTTP_200_OK)
def update_client(client_id: str, client_data: ClientUpdateRequest):
    start_time = time()
    try:
        updated_client = service.update_client(
            client_id,
            client_data
        )

        return format_response(
            data=updated_client, 
            start_time=start_time, 
            message="Client successfully updated"
        )

    except ClientNotFound as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content=format_response(start_time=start_time, message="Request failed", error=str(e))
        )
    except ClientAlreadyExists as e:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, 
            content=format_response(start_time=start_time, message="Request failed", error=str(e))
        )
    except InternalServerError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            content=format_response(start_time=start_time, message="Internal server error", error=str(e))
        )

@router.delete('/clients/{client_id}', status_code=status.HTTP_200_OK)
def delete_client(client_id: str):
    start_time = time()
    try:
        service.delete_client(client_id)
        
        return format_response(
            start_time=start_time, 
            message="Client successfully deleted (logically)"
        )

    except ClientNotFound as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content=format_response(start_time=start_time, message="Request failed", error=str(e))
        )
    except InternalServerError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            content=format_response(start_time=start_time, message="Internal server error", error=str(e))
        )
