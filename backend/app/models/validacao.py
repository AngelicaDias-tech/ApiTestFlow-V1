from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class RegraValidacao(Base):
    """Regra de validação de negócio configurada para um teste (e, opcionalmente,
    para um caso_id específico da massa — se caso_id for nulo, a regra vale para
    todos os casos do teste).

    A massa (Atualizacoes) define os dados de ENTRADA da request. Esta tabela
    define o que se espera da RESPONSE — são conceitos diferentes e não devem
    ser confundidos.
    """

    __tablename__ = "regras_validacao"

    id = Column(Integer, primary_key=True, index=True)
    api_test_id = Column(Integer, ForeignKey("api_tests.id"), nullable=False, index=True)
    caso_id = Column(String(100), nullable=True, index=True)
    ordem = Column(Integer, nullable=False, default=0)

    campo = Column(String(300), nullable=False)
    operador = Column(String(30), nullable=False)
    valor_esperado = Column(String(500), nullable=True)

    # Regras com o mesmo grupo (não nulo) são combinadas em OR entre si;
    # regras sem grupo (ou grupos distintos) exigem que TODAS passem (AND).
    grupo = Column(String(50), nullable=True)
    descricao = Column(String(300), nullable=True)

    teste = relationship("ApiTest", back_populates="regras_validacao")
