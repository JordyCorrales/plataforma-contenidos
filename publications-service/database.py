import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Cadena de conexion 
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://editorial_user:editorial_pass_local@postgres-db:5432/editorial_db"
)

# Normalizacion automatica de prefijo para compatibilidad con SQLAlchemy
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)

# Motor de conexion y verificacion de disponibilidad
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# Fabrica de sesiones de base de datos
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base declarativa para modelos del ORM
Base = declarative_base()

# Generador de sesiones de base de datos
def get_db() -> Generator[Session, None, None]:
    db_session: Session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
