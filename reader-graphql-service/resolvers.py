from typing import Optional, List
import strawberry
from sqlalchemy.orm import joinedload, selectinload

from database import SessionLocal
from models import Category, Publication
from schemas import CategoryType, PublicationType

# Definicion de consultas raiz de GraphQL
@strawberry.type
class Query:

    # Consulta de publicaciones con filtros opcionales de estado y categoria
    @strawberry.field
    def list_publications(
        self,
        status: Optional[str] = None,
        category_id: Optional[int] = None
    ) -> List[PublicationType]:
        db_session = SessionLocal()
        try:
            query = (
                db_session.query(Publication)
                .options(joinedload(Publication.category), selectinload(Publication.history))
            )
            if category_id is not None:
                query = query.filter(Publication.category_id == category_id)
            if status is not None:
                query = query.filter(Publication.status == status)
            publications = query.order_by(Publication.created_at.desc()).all()
            return [PublicationType.from_model(item) for item in publications]
        finally:
            db_session.close()

    # Consulta de una publicacion por identificador con categoria e historial
    @strawberry.field
    def get_publication(self, publication_id: int) -> Optional[PublicationType]:
        db_session = SessionLocal()
        try:
            publication = (
                db_session.query(Publication)
                .options(joinedload(Publication.category), selectinload(Publication.history))
                .filter(Publication.id == publication_id)
                .first()
            )
            if not publication:
                return None
            return PublicationType.from_model(publication)
        finally:
            db_session.close()

    # Consulta del catalogo completo de categorias editoriales
    @strawberry.field
    def list_categories(self) -> List[CategoryType]:
        db_session = SessionLocal()
        try:
            categories = db_session.query(Category).order_by(Category.name.asc()).all()
            return [CategoryType.from_model(item) for item in categories]
        finally:
            db_session.close()
