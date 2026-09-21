from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


def _agora() -> datetime:
    return datetime.now(timezone.utc)


class MassaImportacao(Base):
    """Massa de teste importada a partir do modelo oficial (modelo_atualizacao_request.xlsx).

    Cada teste tem no máximo uma massa ativa: uma nova importação substitui a anterior
    (suas linhas são removidas em cascata).
    """

    __tablename__ = "massa_importacoes"

    id = Column(Integer, primary_key=True, index=True)
    api_test_id = Column(Integer, ForeignKey("api_tests.id"), nullable=False, unique=True, index=True)
    nome_arquivo = Column(String(255), nullable=False)
    total_casos = Column(Integer, nullable=False, default=0)
    total_linhas = Column(Integer, nullable=False, default=0)
    importado_em = Column(DateTime(timezone=True), nullable=False, default=_agora)

    teste = relationship("ApiTest", back_populates="massa")
    linhas = relationship(
        "MassaLinha", back_populates="massa", cascade="all, delete-orphan", order_by="MassaLinha.id"
    )


class MassaLinha(Base):
    """Uma linha da aba 'Atualizacoes' do modelo oficial. Várias linhas com o mesmo
    caso_id são agrupadas para formar o payload daquele caso (path/acao/novo_valor
    aplicados sobre o body base do teste)."""

    __tablename__ = "massa_linhas"

    id = Column(Integer, primary_key=True, index=True)
    massa_id = Column(Integer, ForeignKey("massa_importacoes.id"), nullable=False, index=True)
    caso_id = Column(String(100), nullable=False, index=True)
    path = Column(String(500), nullable=False)
    acao = Column(String(20), nullable=False, default="set")
    tipo = Column(String(20), nullable=True)
    novo_valor = Column(Text, nullable=True)
    ativo = Column(Boolean, nullable=False, default=True)
    observacao = Column(Text, nullable=True)

    massa = relationship("MassaImportacao", back_populates="linhas")
