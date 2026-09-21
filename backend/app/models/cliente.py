from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


def _agora() -> datetime:
    return datetime.now(timezone.utc)


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="ativo")
    created_at = Column(DateTime(timezone=True), nullable=False, default=_agora)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_agora, onupdate=_agora)

    projetos = relationship("Projeto", back_populates="cliente", cascade="all, delete-orphan")
