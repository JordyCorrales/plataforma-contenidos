# Modulos para definicion de enumeraciones y marcas de tiempo UTC
import enum
from datetime import datetime, timezone

# Componentes de definicion de columnas y tipos de datos en SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum

# Clase base declarativa del ORM
from database import Base

# Principio O de SOLID: Abierto/Cerrado (Open/Closed Principle)
# La definicion del enum encapsula los roles permitidos en el dominio editorial.
# Permite extender el sistema incorporando nuevos roles sin necesidad de modificar
# o alterar la logica interna de las tablas y modelos existentes.
class UserRole(str, enum.Enum):
    # Rol responsable de redactar y enviar contenidos para revision
    PUBLICADOR = "PUBLICADOR"
    # Rol con privilegios para aprobar o rechazar publicaciones
    APROBADOR = "APROBADOR"
    # Rol con acceso exclusivo de consulta a contenidos aprobados
    LECTOR = "LECTOR"

# Funcion auxiliar para generar la marca temporal actual en formato UTC
def get_utc_now() -> datetime:
    # Retorna la marca temporal actual garantizando la zona horaria UTC
    return datetime.now(timezone.utc)

# Modelo entidad de usuario mapeado a la tabla relacional users
class User(Base):
    # Nombre de la tabla fisica en la base de datos PostgreSQL
    __tablename__ = "users"

    # Identificador unico de la entidad, clave primaria e indexada
    id = Column(Integer, primary_key=True, index=True)

    # Nombre de usuario unico en el sistema, indexado para acelerar consultas de autenticacion
    username = Column(String(50), unique=True, index=True, nullable=False)

    # Direccion de correo electronico unica e indexada
    email = Column(String(255), unique=True, index=True, nullable=False)

    # Hash seguro de la contraseña almacenada mediante bcrypt
    password_hash = Column(String(255), nullable=False)

    # Rol del usuario en el flujo editorial tipado mediante UserRole, por defecto LECTOR
    role = Column(
        SQLEnum(UserRole, name="user_role_enum"),
        default=UserRole.LECTOR,
        nullable=False
    )

    # Marca temporal de creacion en formato UTC asignada automaticamente en insercion
    created_at = Column(
        DateTime(timezone=True),
        default=get_utc_now,
        nullable=False
    )
