from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer

from app.database.base import Base


class {{CLASS_NAME}}(Base):

    __tablename__ = "{{TABLE_NAME}}"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )