from fastapi import APIRouter, HTTPException, status
from config.database import SqliteManager
from repository.sqlite_client_repository import SqliteClientRepository
from service.client_service import ClientService
from schema.client_schema import ClientCreateRequest, ClientUpdateRequest
from exceptions import ClientAlreadyExists, InternalServerError, ClientNotFound

router = APIRouter()
manager = SqliteManager()
repo = SqliteClientRepository(manager)
service = ClientService(repo)

@router.post('/clients', status_code=status.HTTP_201_CREATED)
def create_client(client_data: ClientCreateRequest):
    try:
        new_client = service.register_client(
            name = client_data.name,
            surname = client_data.surname,
            email = client_data.email,
            birthdate = client_data.birthdate
        )

        return new_client

    except ClientAlreadyExists as e:
        raise HTTPException(status_code=409, detail=str(e))
    except InternalServerError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/clients', status_code=status.HTTP_200_OK)
def get_all_client():
    try:
        clients = service.get_all_client()

        return clients
    
    except InternalServerError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/clients/id/{client_id}', status_code=status.HTTP_200_OK)
def get_client_by_id(client_id: str):
    try:
        client = service.get_client_by_id(client_id)

        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        return client

    except InternalServerError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/clients/email/{client_email}', status_code=status.HTTP_200_OK)
def get_client_by_email(client_email: str):
    try:
        client = service.get_client_by_email(client_email)

        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        return client

    except InternalServerError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put('/clients/{client_id}', status_code=status.HTTP_200_OK)
def update_client(client_id: str, client_data: ClientUpdateRequest):
    try:
        update = service.update_client(
            client_id,
            client_data
        )

        return update

    except ClientNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ClientAlreadyExists as e:
        raise HTTPException(status_code=409, detail=str(e))
    except InternalServerError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete('/clients/{client_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_client(client_id: str):
    try:
        delete = service.delete_client(client_id)
        return

    except ClientNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InternalServerError as e:
        raise HTTPException(status_code=500, detail=str(e))
