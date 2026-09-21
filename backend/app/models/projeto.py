from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


def _agora() -> datetime:
    return datetime.now(timezone.utc)


class Projeto(Base):
    __tablename__ = "projetos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    nome = Column(String(150), nullable=False)
    descricao = Column(Text, nullable=True)
    ambiente = Column(String(30), nullable=False, default="homologacao")
    status = Column(String(20), nullable=False, default="ativo")
    created_at = Column(DateTime(timezone=True), nullable=False, default=_agora)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_agora, onupdate=_agora)

    cliente = relationship("Cliente", back_populates="projetos")
    testes = relationship("ApiTest", back_populates="projeto", cascade="all, delete-orphan")
