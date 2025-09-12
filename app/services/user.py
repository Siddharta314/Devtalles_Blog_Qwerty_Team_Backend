from sqlalchemy.orm import Session
from typing import Optional

from app.models.user import User


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, name: str, lastname: str, email: str, password: str) -> User:
        user = User.create(
            name=name,
            lastname=lastname,
            email=email,
            password=password,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.get_user_by_email(email)
        if user is None or not user.verify_password(password):
            return None
        return user
