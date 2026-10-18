import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from database import Base

# Estados del ciclo editorial
class PublicationStatus(str, enum.Enum):
    BORRADOR = "BORRADOR"
    EN_REVISION = "EN_REVISION"
    APROBADO = "APROBADO"
    PUBLICADO = "PUBLICADO"
    RECHAZADO = "RECHAZADO"

# Helper para marcas de tiempo en formato UTC
def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)

# Tipo enumerado reutilizado de la base de datos existente
publication_status_enum = SQLEnum(
    PublicationStatus,
    name="publication_status_enum"
)

# Modelo de categorias para consultas de solo lectura
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    # Relacion con publicaciones asociadas
    publications = relationship("Publication", back_populates="category")

# Modelo de publicaciones para consultas de solo lectura
class Publication(Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    status = Column(
        publication_status_enum,
        default=PublicationStatus.BORRADOR,
        nullable=False,
        index=True
    )
    author_id = Column(Integer, nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=get_utc_now,
        onupdate=get_utc_now,
        nullable=False
    )

    # Relaciones de consulta con categoria e historial
    category = relationship("Category", back_populates="publications")
    history = relationship(
        "History",
        back_populates="publication",
        order_by="History.timestamp.desc()"
    )

# Modelo de auditoria e historial para trazabilidad en consultas
class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True)
    publication_id = Column(Integer, ForeignKey("publications.id"), nullable=False, index=True)
    reviewer_id = Column(Integer, nullable=False)
    previous_status = Column(publication_status_enum, nullable=False)
    new_status = Column(publication_status_enum, nullable=False)
    comments = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    # Relacion inversa con la publicacion consultada
    publication = relationship("Publication", back_populates="history")
