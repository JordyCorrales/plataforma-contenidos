from typing import List, Optional
from sqlalchemy.orm import Session

from models import User
from schemas import UserCreate

# Acceso a datos de la entidad usuario
class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    # Busca usuario por nombre de usuario
    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    # Busca usuario por correo electronico
    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    # Busca usuario por identificador unico
    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    # Obtiene el listado completo de usuarios
    def get_all(self) -> List[User]:
        return self.db.query(User).all()

    # Crea y persiste un nuevo usuario en la base de datos
    def create(self, user_in: UserCreate, password_hash: str) -> User:
        db_user = User(
            username=user_in.username,
            email=user_in.email,
            password_hash=password_hash,
            role=user_in.role
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
