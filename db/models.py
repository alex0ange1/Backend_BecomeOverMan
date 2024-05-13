import uuid

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=False, unique=True)  # Уникальное поле username
    is_active = Column(Boolean(), default=True)
    hashed_password = Column(String, nullable=False)
    password = Column(String, nullable=False)
    completed_tasks = Column(ARRAY(String), nullable=False, default=[])
    pending_tasks = Column(ARRAY(String), nullable=False, default=[])
