from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import UserCreate, UserResponse, LoginRequest, TokenResponse
from repositories import UserRepository
from services import UserService
from security import get_current_user

# Enrutador principal de usuarios
router = APIRouter(prefix="/api/users", tags=["Users Auth"])

# Proveedor del servicio de usuarios con sesion inyectada
def get_user_service(db_session: Session = Depends(get_db)) -> UserService:
    user_repository = UserRepository(db_session)
    return UserService(user_repository)

# Registro de un nuevo usuario
@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def register(
    user_in: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    return user_service.register_user(user_in)

# Inicio de sesion y emision de token JWT
@router.post("/login", response_model=TokenResponse)
def login(
    login_in: LoginRequest,
    user_service: UserService = Depends(get_user_service)
):
    return user_service.authenticate_user(login_in)

# Perfil del usuario autenticado
@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: Dict[str, Any] = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    user_id = int(current_user.get("user_id") or current_user.get("sub"))
    return user_service.get_user(user_id)

# Listado de usuarios registrados
@router.get("/", response_model=List[UserResponse])
def list_users(
    current_user: Dict[str, Any] = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    return user_service.list_users()

# Consulta de usuario por identificador
@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    return user_service.get_user(user_id)
