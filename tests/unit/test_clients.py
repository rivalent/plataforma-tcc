from clients.service.client_service import ClientService
from clients.repository.sqlite_client_repository import SqliteClientRepository
from clients.domain.client_domain import ClientDomain
from clients.exceptions import ClientAlreadyExists
from shared.database import SqliteManager
from datetime import date
import os
import time
import pytest

test_manager = SqliteManager("clients/database", "db_test_clients.db")
test_repo = SqliteClientRepository(test_manager)
test_repo.create_tables()

test_service = ClientService(test_repo)

UNIQUE_EMAIL = f"MiyaSashi{int(time.time())}@email.com"
created_client_id = None

def test_register_client_directly():
    global created_client_id

    new_client = test_service.register_client(
        name="Miyamoto",
        surname="Musashi",
        email=UNIQUE_EMAIL,
        birthdate=date(1600, 5, 24)
    )

    assert new_client.id is not None
    assert new_client.name == "miyamoto"
    assert new_client.surname == "musashi"
    assert new_client.email == UNIQUE_EMAIL.lower()
    assert new_client.active is True

    created_client_id = new_client.id

def test_prevent_registration_with_duplicate_email():
    with pytest.raises(ClientAlreadyExists):
        test_service.register_client(
            name="Leorio",
            surname="Paradknight",
            email=UNIQUE_EMAIL,
            birthdate=date(1995, 3, 3)
        )

def test_fetch_client_by_id():
    fetched_client = test_service.get_client_by_id(created_client_id)

    assert fetched_client is not None
    assert fetched_client.id == created_client_id
    assert fetched_client.name == "miyamoto"

def test_fetch_client_by_email():
    fetched_client = test_service.get_client_by_email(UNIQUE_EMAIL)

    assert fetched_client is not None
    assert fetched_client.email == UNIQUE_EMAIL.lower()
    assert fetched_client.surname == "musashi"

def test_get_all_clients():
    clients_list = test_service.get_all_client()

    assert isinstance(clients_list, list)
    assert len(clients_list) > 0

def test_update_client():
    update_data = ClientDomain(
        id=created_client_id, 
        name="Takezo",
        surname=None,
        email=None,
        birthdate=None,
        created_at=None,
        updated_at=None
    )
    updated_client = test_service.update_client(created_client_id, update_data)

    assert updated_client.name == "takezo"
    assert updated_client.surname == "musashi"

def test_soft_delete_client():
    result = test_service.delete_client(created_client_id)
    assert result is True

def test_return_none_when_fetching_deleted_client():
    fetched_client = test_service.get_client_by_id(created_client_id)
    assert fetched_client is None

def test_cleanup_test_database():
    db_path = "clients/database/db_test_clients.db"
    
    if os.path.exists(db_path):
        os.remove(db_path)
    
    assert not os.path.exists(db_path)
