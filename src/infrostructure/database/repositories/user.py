from poetry.utils import password_manager
from sqlalchemy.orm import Session

from core.user.entities import BaseUser
from infrostructure.database.base import SessionLocal
from infrostructure.database.models.user import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_username(self, username: str):
        return self.session.query(User).filter(User.username == username).first()

    def get_all(self):
        return self.session.query(User).all()

    def add(self, user: BaseUser):
        self.session.add(
                User(
                    email=user.email,
                    password=user.password,
                    username=user.username,
                    is_admin=user.is_admin
            )
        )


def user_repository_factory(session):
    return UserRepository(session)