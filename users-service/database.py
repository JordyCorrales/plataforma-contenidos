import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Conexion a PostgreSQL con driver psycopg2
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://editorial_user:editorial_pass_local@postgres-db:5432/editorial_db"
)

# Normaliza esquema a psycopg2 si se proporciona postgresql generico
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)

# Motor de base de datos y pool de conexiones
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# Fabrica de sesiones
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base declarativa para modelos ORM
Base = declarative_base()

# Dependencia para inyeccion de sesion de base de datos
def get_db() -> Generator[Session, None, None]:
    db_session: Session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
