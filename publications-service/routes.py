from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from database import get_db
from models import PublicationStatus
from schemas import (
    CategoryCreate,
    CategoryResponse,
    PublicationCreate,
    PublicationUpdate,
    PublicationStatusUpdate,
    PublicationResponse
)
from repositories import PublicationRepository
from services import PublicationService
from security import get_current_user, require_role

# Enrutador principal de publicaciones y categorias
router = APIRouter(prefix="/api/publications", tags=["publications"])

# Proveedor del servicio de publicaciones con sesion inyectada
def get_publication_service(db_session: Session = Depends(get_db)) -> PublicationService:
    publication_repository = PublicationRepository(db_session)
    return PublicationService(publication_repository)

# Registro de una nueva categoria editorial
@router.post("/categories", status_code=status.HTTP_201_CREATED, response_model=CategoryResponse)
def create_category(
    category_in: CategoryCreate,
    current_user: Dict[str, Any] = Depends(require_role("PUBLICADOR", "APROBADOR")),
    publication_service: PublicationService = Depends(get_publication_service)
):
    return publication_service.create_category(category_in)

# Listado de todas las categorias registradas
@router.get("/categories", response_model=List[CategoryResponse])
def list_categories(
    publication_service: PublicationService = Depends(get_publication_service)
):
    return publication_service.list_categories()

# Creacion de una publicacion en estado borrador
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PublicationResponse)
def create_publication(
    publication_in: PublicationCreate,
    current_user: Dict[str, Any] = Depends(require_role("PUBLICADOR")),
    publication_service: PublicationService = Depends(get_publication_service)
):
    author_id = int(current_user.get("user_id") or current_user.get("sub"))
    return publication_service.create_publication(publication_in, author_id)

# Listado de publicaciones con filtros opcionales
@router.get("/", response_model=List[PublicationResponse])
def list_publications(
    category_id: Optional[int] = Query(default=None, description="Filtrar por identificador de categoria"),
    status: Optional[PublicationStatus] = Query(default=None, description="Filtrar por estado editorial"),
    publication_service: PublicationService = Depends(get_publication_service)
):
    return publication_service.list_publications(category_id=category_id, status_filter=status)

# Detalle de una publicacion con historial de cambios
@router.get("/{publication_id}", response_model=PublicationResponse)
def get_publication(
    publication_id: int,
    publication_service: PublicationService = Depends(get_publication_service)
):
    return publication_service.get_publication(publication_id)

# Actualizacion de titulo o contenido por el autor original
@router.put("/{publication_id}", response_model=PublicationResponse)
def update_publication(
    publication_id: int,
    publication_in: PublicationUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    publication_service: PublicationService = Depends(get_publication_service)
):
    user_id = int(current_user.get("user_id") or current_user.get("sub"))
    return publication_service.update_publication(publication_id, publication_in, user_id)

# Transicion de estado editorial ejecutada por un aprobador
@router.patch("/{publication_id}/status", response_model=PublicationResponse)
def update_publication_status(
    publication_id: int,
    status_in: PublicationStatusUpdate,
    current_user: Dict[str, Any] = Depends(require_role("APROBADOR")),
    publication_service: PublicationService = Depends(get_publication_service)
):
    reviewer_id = int(current_user.get("user_id") or current_user.get("sub"))
    reviewer_role = str(current_user.get("role", "APROBADOR"))
    return publication_service.change_status(publication_id, status_in, reviewer_id, reviewer_role)
