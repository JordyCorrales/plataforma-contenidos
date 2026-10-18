from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from models import PublicationStatus

# Esquema base de categoria
class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=100, description="Nombre de la categoria")
    description: Optional[str] = Field(default=None, description="Descripcion de la categoria")

# Esquema para creacion de categoria
class CategoryCreate(CategoryBase):
    pass

# Esquema de respuesta para categoria
class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Esquema de respuesta para registro de auditoria e historial
class HistoryResponse(BaseModel):
    id: int
    publication_id: int
    reviewer_id: int
    previous_status: PublicationStatus
    new_status: PublicationStatus
    comments: Optional[str] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

# Esquema base de publicacion
class PublicationBase(BaseModel):
    title: str = Field(min_length=1, max_length=200, description="Titulo de la publicacion")
    content: str = Field(min_length=1, description="Contenido del articulo")
    category_id: int = Field(description="Identificador de la categoria asociada")

# Esquema para creacion de publicacion
class PublicationCreate(PublicationBase):
    pass

# Esquema para actualizacion de contenido de publicacion
class PublicationUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200, description="Nuevo titulo")
    content: Optional[str] = Field(default=None, min_length=1, description="Nuevo contenido")
    category_id: Optional[int] = Field(default=None, description="Nueva categoria")

# Esquema para cambio de estado editorial
class PublicationStatusUpdate(BaseModel):
    new_status: PublicationStatus = Field(description="Nuevo estado editorial a aplicar")
    comments: Optional[str] = Field(default=None, description="Observaciones o motivo del cambio")

# Esquema de respuesta para publicacion con relaciones anidadas
class PublicationResponse(BaseModel):
    id: int
    title: str
    content: str
    status: PublicationStatus
    author_id: int
    category_id: int
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None
    history: List[HistoryResponse] = []

    model_config = ConfigDict(from_attributes=True)
