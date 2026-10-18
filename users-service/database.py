# Modulos del sistema operativo y tipado estatico
import os
from typing import Generator

# Componentes fundamentales del ORM SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Cadena de conexion a la base de datos leida desde variables de entorno con fallback de docker-compose
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://editorial_user:editorial_pass_local@postgres-db:5432/editorial_db"
)

# Motor de conexion de SQLAlchemy que administra el pool de conexiones hacia PostgreSQL
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# Fabrica generadora de sesiones de base de datos vinculada al engine
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Clase base declarativa para el mapeo objeto-relacional de modelos
Base = declarative_base()

# Generador de sesiones para inyeccion de dependencias en endpoints de FastAPI
# Principio D de SOLID: Inversion de Dependencias (Dependency Inversion Principle)
# Los controladores de alto nivel dependen de la abstraccion Session inyectada por get_db,
# desacoplandose de la creacion concreta de conexiones y facilitando pruebas unitarias mediante mocks.
def get_db() -> Generator[Session, None, None]:
    # Instanciacion de una sesion local independiente para el contexto de la solicitud
    db: Session = SessionLocal()
    try:
        # Entrega de la sesion activa al llamador mediante el patron generador
        yield db
    finally:
        # Cierre garantizado de la sesion al concluir el procesamiento de la solicitud
        db.close()
