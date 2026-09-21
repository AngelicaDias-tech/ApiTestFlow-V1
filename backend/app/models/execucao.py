from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


def _agora() -> datetime:
    return datetime.now(timezone.utc)


class Execucao(Base):
    """Execução de um teste (uma rodada da massa contra a API).

    tipo='demonstracao' identifica execuções de seed usadas apenas para visualizar a
    interface durante o desenvolvimento — nunca deve ser confundido com uma execução
    real (tipo='real'), que só existirá quando o motor de execução (pytest + request
    HTTP real) for implementado.
    """

    __tablename__ = "execucoes"

    id = Column(Integer, primary_key=True, index=True)
    api_test_id = Column(Integer, ForeignKey("api_tests.id"), nullable=False, index=True)
    tipo = Column(String(20), nullable=False, default="real")
    executado_em = Column(DateTime(timezone=True), nullable=False, default=_agora)
    total_casos = Column(Integer, nullable=False, default=0)
    total_pass = Column(Integer, nullable=False, default=0)
    total_fail = Column(Integer, nullable=False, default=0)

    teste = relationship("ApiTest", back_populates="execucoes")
    resultados = relationship(
        "ResultadoLinha", back_populates="execucao", cascade="all, delete-orphan"
    )


class ResultadoLinha(Base):
    """Resultado de um caso (caso_id da massa) dentro de uma execução.

    Um caso agrupa VÁRIAS linhas da massa (mesmo caso_id) em UMA request, UMA
    chamada de API e UMA response — o PASS/FAIL do caso é decidido pelas suas
    ResultadoValidacao (regras de negócio configuradas para o teste/caso).
    """

    __tablename__ = "resultado_linhas"

    id = Column(Integer, primary_key=True, index=True)
    execucao_id = Column(Integer, ForeignKey("execucoes.id"), nullable=False, index=True)
    caso_id = Column(String(100), nullable=False)
    resultado = Column(String(10), nullable=False)  # PASS | FAIL
    status_http = Column(Integer, nullable=True)
    tempo_ms = Column(Integer, nullable=True)
    request_enviado = Column(Text, nullable=True)
    response_recebido = Column(Text, nullable=True)
    motivo_falha = Column(Text, nullable=True)

    execucao = relationship("Execucao", back_populates="resultados")
    validacoes = relationship(
        "ResultadoValidacao", back_populates="resultado_linha", cascade="all, delete-orphan"
    )


class ResultadoValidacao(Base):
    """Avaliação de UMA regra de negócio (campo x operador x esperado) para UM
    caso dentro de uma execução — obtido vem sempre da response real; esperado
    vem sempre da regra configurada (RegraValidacao)."""

    __tablename__ = "resultado_validacoes"

    id = Column(Integer, primary_key=True, index=True)
    resultado_linha_id = Column(Integer, ForeignKey("resultado_linhas.id"), nullable=False, index=True)
    campo = Column(String(300), nullable=False)
    operador = Column(String(30), nullable=False)
    valor_esperado = Column(String(500), nullable=True)
    valor_obtido = Column(Text, nullable=True)
    passou = Column(Boolean, nullable=False)
    descricao = Column(String(300), nullable=True)
    detalhe = Column(Text, nullable=True)

    resultado_linha = relationship("ResultadoLinha", back_populates="validacoes")
