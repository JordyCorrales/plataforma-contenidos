from typing import List, Optional
from fastapi import HTTPException, status

from models import Category, Publication, PublicationStatus
from schemas import CategoryCreate, PublicationCreate, PublicationUpdate, PublicationStatusUpdate
from repositories import PublicationRepository

# Matriz de transiciones validas del ciclo editorial
VALID_TRANSITIONS = {
    PublicationStatus.BORRADOR: [PublicationStatus.EN_REVISION],
    PublicationStatus.RECHAZADO: [PublicationStatus.EN_REVISION],
    PublicationStatus.EN_REVISION: [PublicationStatus.APROBADO, PublicationStatus.RECHAZADO],
    PublicationStatus.APROBADO: [PublicationStatus.PUBLICADO],
    PublicationStatus.PUBLICADO: []
}

# Logica de negocio para categorias, articulos y flujo editorial
class PublicationService:
    def __init__(self, publication_repository: PublicationRepository):
        self.publication_repository = publication_repository

    # Registra una nueva categoria validando que el nombre no este duplicado
    def create_category(self, category_in: CategoryCreate) -> Category:
        existing_category = self.publication_repository.get_category_by_name(category_in.name)
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una categoria con ese nombre"
            )
        return self.publication_repository.create_category(category_in)

    # Obtiene una categoria por id o lanza error 404
    def get_category(self, category_id: int) -> Category:
        category = self.publication_repository.get_category_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria no encontrada"
            )
        return category

    # Lista todas las categorias disponibles
    def list_categories(self) -> List[Category]:
        return self.publication_repository.get_all_categories()

    # Crea un articulo en estado borrador
    def create_publication(self, publication_in: PublicationCreate, author_id: int) -> Publication:
        category = self.publication_repository.get_category_by_id(publication_in.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La categoria especificada no existe"
            )
        return self.publication_repository.create_publication(publication_in, author_id)

    # Obtiene un articulo por su identificador
    def get_publication(self, publication_id: int) -> Publication:
        publication = self.publication_repository.get_publication_by_id(publication_id)
        if not publication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Publicacion no encontrada"
            )
        return publication

    # Lista publicaciones con filtros opcionales de categoria y estado
    def list_publications(
        self,
        category_id: Optional[int] = None,
        status_filter: Optional[PublicationStatus] = None
    ) -> List[Publication]:
        return self.publication_repository.get_all_publications(category_id, status_filter)

    # Actualiza contenido solo si el articulo esta en borrador o rechazado
    def update_publication(
        self,
        publication_id: int,
        publication_in: PublicationUpdate,
        user_id: int
    ) -> Publication:
        publication = self.get_publication(publication_id)

        if publication.author_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el autor puede modificar esta publicacion"
            )

        if publication.status not in [PublicationStatus.BORRADOR, PublicationStatus.RECHAZADO]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede editar una publicacion en estado {publication.status.value}"
            )

        update_data = publication_in.model_dump(exclude_unset=True)
        if "category_id" in update_data and update_data["category_id"] is not None:
            category = self.publication_repository.get_category_by_id(update_data["category_id"])
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La categoria especificada no existe"
                )

        return self.publication_repository.update_publication(publication, update_data)

    # Ejecuta transicion de estado editorial con registro de auditoria
    def change_status(
        self,
        publication_id: int,
        status_in: PublicationStatusUpdate,
        reviewer_id: int,
        reviewer_role: str
    ) -> Publication:
        publication = self.get_publication(publication_id)

        allowed_target_states = VALID_TRANSITIONS.get(publication.status, [])
        if status_in.new_status not in allowed_target_states:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Transicion no permitida de {publication.status.value} a {status_in.new_status.value}"
            )

        if status_in.new_status in [PublicationStatus.APROBADO, PublicationStatus.RECHAZADO]:
            if reviewer_role != "APROBADOR":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Solo los usuarios con rol APROBADOR pueden aprobar o rechazar publicaciones"
                )

        previous_status = publication.status
        publication.status = status_in.new_status
        self.publication_repository.db_session.commit()
        self.publication_repository.db_session.refresh(publication)

        self.publication_repository.create_history_entry(
            publication_id=publication.id,
            reviewer_id=reviewer_id,
            previous_status=previous_status,
            new_status=status_in.new_status,
            comments=status_in.comments
        )

        return publication
