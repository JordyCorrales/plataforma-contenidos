from __future__ import annotations
from typing import Optional, List
from datetime import datetime
import strawberry

# Tipo de GraphQL para registros de auditoria e historial
@strawberry.type
class HistoryType:
    id: int
    publication_id: int
    reviewer_id: int
    previous_status: str
    new_status: str
    comments: Optional[str] = None
    timestamp: datetime

    # Constructor auxiliar desde entidad ORM
    @classmethod
    def from_model(cls, model) -> HistoryType:
        return cls(
            id=model.id,
            publication_id=model.publication_id,
            reviewer_id=model.reviewer_id,
            previous_status=model.previous_status.value if hasattr(model.previous_status, "value") else str(model.previous_status),
            new_status=model.new_status.value if hasattr(model.new_status, "value") else str(model.new_status),
            comments=model.comments,
            timestamp=model.timestamp
        )

# Tipo de GraphQL para categorias tematicas
@strawberry.type
class CategoryType:
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime

    # Constructor auxiliar desde entidad ORM
    @classmethod
    def from_model(cls, model) -> CategoryType:
        return cls(
            id=model.id,
            name=model.name,
            description=model.description,
            created_at=model.created_at
        )

# Tipo de GraphQL para publicaciones y contenidos editoriales
@strawberry.type
class PublicationType:
    id: int
    title: str
    content: str
    status: str
    author_id: int
    category_id: int
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryType] = None
    history: List[HistoryType] = strawberry.field(default_factory=list)

    # Constructor auxiliar desde entidad ORM
    @classmethod
    def from_model(cls, model) -> PublicationType:
        return cls(
            id=model.id,
            title=model.title,
            content=model.content,
            status=model.status.value if hasattr(model.status, "value") else str(model.status),
            author_id=model.author_id,
            category_id=model.category_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            category=CategoryType.from_model(model.category) if model.category else None,
            history=[HistoryType.from_model(h) for h in model.history] if model.history else []
        )
