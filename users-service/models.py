import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum

from database import Base

# Roles del sistema editorial
class UserRole(str, enum.Enum):
    PUBLICADOR = "PUBLICADOR"
    APROBADOR = "APROBADOR"
    LECTOR = "LECTOR"

# Helper para marca temporal en UTC
def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)

# Modelo de usuario
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(
        SQLEnum(UserRole, name="user_role_enum"),
        default=UserRole.LECTOR,
        nullable=False
    )
    created_at = Column(
        DateTime(timezone=True),
        default=get_utc_now,
        nullable=False
    )
