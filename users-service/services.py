from typing import List
from fastapi import HTTPException, status

from models import User
from schemas import UserCreate, LoginRequest, TokenResponse
from repositories import UserRepository
from security import get_password_hash, verify_password, create_access_token

# Servicios de logica de negocio para usuarios
class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    # Registra un nuevo usuario validando unicidad de username y email
    def register_user(self, user_in: UserCreate) -> User:
        if self.repository.get_by_username(user_in.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya se encuentra registrado"
            )
        if self.repository.get_by_email(user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electronico ya se encuentra registrado"
            )

        password_hash = get_password_hash(user_in.password)
        return self.repository.create(user_in, password_hash)

    # Valida credenciales de acceso y genera token JWT
    def authenticate_user(self, login_in: LoginRequest) -> TokenResponse:
        user = self.repository.get_by_username(login_in.username)
        if not user or not verify_password(login_in.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales invalidas",
                headers={"WWW-Authenticate": "Bearer"}
            )

        token_data = {
            "sub": str(user.id),
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value if hasattr(user.role, "value") else str(user.role)
        }
        access_token = create_access_token(token_data)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            role=user.role,
            user_id=user.id
        )

    # Retorna todos los usuarios registrados
    def list_users(self) -> List[User]:
        return self.repository.get_all()

    # Busca un usuario por id o lanza error si no existe
    def get_user(self, user_id: int) -> User:
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return user
