from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from models import UserRole

# Esquema base de usuario
class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50, description="Nombre de usuario")
    email: EmailStr = Field(description="Correo electronico")
    role: UserRole = Field(default=UserRole.LECTOR, description="Rol del usuario")

# Esquema para registro de usuario
class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128, description="Contraseña")

# Esquema de respuesta de usuario
class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Esquema para inicio de sesion
class LoginRequest(BaseModel):
    username: str = Field(min_length=1, description="Nombre de usuario")
    password: str = Field(min_length=1, description="Contraseña")

# Esquema de respuesta de autenticacion
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    user_id: int
