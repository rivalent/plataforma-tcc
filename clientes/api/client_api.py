from fastapi import APIRouter, HTTPException, status
from service.client_service import ClientService
from schema.client_schema import ClientCreateRequest, ClientUpdateRequest
from config.logger_config import LoggerFactory
import exceptions

logger = LoggerFactory.get_logger("ClientApiLogger")
router = APIRouter()
service = ClientService()

