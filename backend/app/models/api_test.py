from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


def _agora() -> datetime:
    return datetime.now(timezone.utc)


class ApiTest(Base):
    """Cadastro de um teste de API dentro de um projeto.

    Guarda a configuração necessária para montar a chamada (endpoint, método,
    headers, query/path params, body e autenticação). A execução real via pytest,
    a comparação de regras (PASS/FAIL) e a massa de teste em planilha são etapas
    futuras que vão consumir esta configuração — o modelo já fica preparado para
    isso sem exigir migração estrutural.

    `auth_token` fica em texto simples nesta etapa (SQLite local de desenvolvimento).
    PENDENTE DE DECISÃO: integração com um secret manager/cofre antes de qualquer
    uso em produção — não é uma solução definitiva de segurança.
    """

    __tablename__ = "api_tests"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projetos.id"), nullable=False, index=True)

    # Identificação
    nome = Column(String(150), nullable=False)
    descricao = Column(Text, nullable=True)

    # Request
    endpoint = Column(String(500), nullable=False)
    metodo_http = Column(String(10), nullable=False, default="GET")
    headers = Column(Text, nullable=True)
    query_params = Column(Text, nullable=True)
    path_params = Column(Text, nullable=True)
    body = Column(Text, nullable=True)

    # Autenticação (estrutura inicial — ver nota de segurança acima)
    auth_type = Column(String(30), nullable=False, default="nenhuma")
    auth_token = Column(Text, nullable=True)

    ambiente = Column(String(30), nullable=True)
    status = Column(String(20), nullable=False, default="ativo")
    created_at = Column(DateTime(timezone=True), nullable=False, default=_agora)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_agora, onupdate=_agora)

    projeto = relationship("Projeto", back_populates="testes")
    massa = relationship(
        "MassaImportacao", back_populates="teste", uselist=False, cascade="all, delete-orphan"
    )
    execucoes = relationship("Execucao", back_populates="teste", cascade="all, delete-orphan")
    regras_validacao = relationship(
        "RegraValidacao", back_populates="teste", cascade="all, delete-orphan", order_by="RegraValidacao.ordem"
    )
