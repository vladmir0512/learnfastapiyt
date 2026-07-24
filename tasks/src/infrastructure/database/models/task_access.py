from sqlalchemy import Integer, Column, DateTime, ForeignKey, func, UniqueConstraint
from infrastructure.database.base import Base


class TaskAccess(Base):
    __tablename__ = "task_access"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, nullable=False)
    granted_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("task_id", "user_id", name="uq_task_user_access"),
    )
