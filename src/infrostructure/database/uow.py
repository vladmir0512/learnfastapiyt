from contextlib import contextmanager

from infrostructure.database.base import SessionLocal
from infrostructure.database.exceptions import UnitOfWorkError


class UnitOfWork:
    def __init__(self):
        self.session = SessionLocal()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def close(self):
        self.session.close()


@contextmanager
def unit_of_work():
    uow = UnitOfWork()
    try:
        yield uow
        uow.commit()
    except Exception:
        uow.rollback()
        raise UnitOfWorkError
    finally:
        uow.close()