# Modulos de gestion de fechas
from datetime import datetime

# Componentes de definicion de esquemas y validacion de Pydantic v2
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# Importacion del enum de roles para garantizar coherencia con los modelos del dominio
from models import UserRole

# Esquema base con atributos comunes compartidos entre operaciones de usuario
class UserBase(BaseModel):
    # Nombre de usuario unico con restricciones de longitud
    username: str = Field(min_length=3, max_length=50, description="Nombre de usuario unico")
    # Direccion de correo electronico con validacion estricta de formato RFC
    email: EmailStr = Field(description="Correo electronico valido")
    # Perfil editorial asignado, por defecto LECTOR
    role: UserRole = Field(default=UserRole.LECTOR, description="Rol de acceso asignado al usuario")

# Principio L de SOLID: Sustitucion de Liskov (Liskov Substitution Principle)
# UserCreate extiende a UserBase agregando el campo password sin alterar los contratos
# ni violar las expectativas de los atributos existentes (username, email, role).
# Cualquier componente que requiera datos base de usuario puede aceptar instancias compatibles.
class UserCreate(UserBase):
    # Contraseña en texto plano para el registro con longitud minima obligatoria de 6 caracteres
    password: str = Field(min_length=6, max_length=128, description="Contraseña en texto plano a hashear")

# Esquema de salida para respuesta de datos de usuario hacia clientes y servicios
# Por diseno de seguridad omite el campo password_hash, protegiendo las credenciales
class UserResponse(UserBase):
    # Identificador unico de la entidad en la base de datos
    id: int
    # Marca temporal de registro del usuario en formato UTC
    created_at: datetime

    # Configuracion de Pydantic v2 para serializar directamente desde modelos ORM de SQLAlchemy
    model_config = ConfigDict(from_attributes=True)

# Esquema de solicitud para inicio de sesion y recepcion de credenciales
class LoginRequest(BaseModel):
    # Nombre de usuario registrado para autenticacion
    username: str = Field(min_length=1, description="Nombre de usuario del solicitante")
    # Contraseña en texto plano para verificar contra el hash de base de datos
    password: str = Field(min_length=1, description="Contraseña del solicitante")

# Esquema de respuesta para emision de credenciales de sesion Bearer JWT
class TokenResponse(BaseModel):
    # Token JWT firmado y codificado
    access_token: str
    # Tipo de token de autenticacion HTTP
    token_type: str = "bearer"
    # Rol del usuario asociado a los permisos del token
    role: UserRole
    # Identificador unico del usuario autenticado
    user_id: int
