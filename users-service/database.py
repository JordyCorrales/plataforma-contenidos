import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Conexion a PostgreSQL
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://editorial_user:editorial_pass_local@postgres-db:5432/editorial_db"
)

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
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
