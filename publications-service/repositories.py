from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from models import Category, Publication, History, PublicationStatus
from schemas import CategoryCreate, PublicationCreate

# Acceso a datos para publicaciones, categorias e historial
class PublicationRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    # Persiste una nueva categoria
    def create_category(self, category_in: CategoryCreate) -> Category:
        new_category = Category(
            name=category_in.name,
            description=category_in.description
        )
        self.db_session.add(new_category)
        self.db_session.commit()
        self.db_session.refresh(new_category)
        return new_category

    # Busca categoria por id
    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        return self.db_session.query(Category).filter(Category.id == category_id).first()

    # Busca categoria por nombre
    def get_category_by_name(self, name: str) -> Optional[Category]:
        return self.db_session.query(Category).filter(Category.name == name).first()

    # Obtiene listado de categorias
    def get_all_categories(self) -> List[Category]:
        return self.db_session.query(Category).all()

    # Persiste una nueva publicacion en estado borrador
    def create_publication(self, publication_in: PublicationCreate, author_id: int) -> Publication:
        new_publication = Publication(
            title=publication_in.title,
            content=publication_in.content,
            category_id=publication_in.category_id,
            author_id=author_id,
            status=PublicationStatus.BORRADOR
        )
        self.db_session.add(new_publication)
        self.db_session.commit()
        self.db_session.refresh(new_publication)
        return new_publication

    # Busca publicacion por id
    def get_publication_by_id(self, publication_id: int) -> Optional[Publication]:
        return self.db_session.query(Publication).filter(Publication.id == publication_id).first()

    # Obtiene publicaciones con filtros opcionales
    def get_all_publications(
        self,
        category_id: Optional[int] = None,
        status: Optional[PublicationStatus] = None
    ) -> List[Publication]:
        query = self.db_session.query(Publication)
        if category_id is not None:
            query = query.filter(Publication.category_id == category_id)
        if status is not None:
            query = query.filter(Publication.status == status)
        return query.order_by(Publication.created_at.desc()).all()

    # Actualiza atributos de una publicacion
    def update_publication(self, publication: Publication, update_data: Dict[str, Any]) -> Publication:
        for attribute, value in update_data.items():
            if hasattr(publication, attribute) and value is not None:
                setattr(publication, attribute, value)
        self.db_session.commit()
        self.db_session.refresh(publication)
        return publication

    # Registra una transicion en el historial de revisiones
    def create_history_entry(
        self,
        publication_id: int,
        reviewer_id: int,
        previous_status: PublicationStatus,
        new_status: PublicationStatus,
        comments: Optional[str] = None
    ) -> History:
        history_entry = History(
            publication_id=publication_id,
            reviewer_id=reviewer_id,
            previous_status=previous_status,
            new_status=new_status,
            comments=comments
        )
        self.db_session.add(history_entry)
        self.db_session.commit()
        self.db_session.refresh(history_entry)
        return history_entry
