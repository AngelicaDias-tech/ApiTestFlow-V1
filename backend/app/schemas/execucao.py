from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict

TipoExecucao = Literal["demonstracao", "real"]
ResultadoCaso = Literal["PASS", "FAIL"]


class ResultadoValidacaoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    campo: str
    operador: str
    valor_esperado: Optional[str] = None
    valor_obtido: Optional[str] = None
    passou: bool
    descricao: Optional[str] = None
    detalhe: Optional[str] = None


class ResultadoLinhaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    execucao_id: int
    caso_id: str
    resultado: ResultadoCaso
    status_http: Optional[int] = None
    tempo_ms: Optional[int] = None
    request_enviado: Optional[str] = None
    response_recebido: Optional[str] = None
    motivo_falha: Optional[str] = None
    validacoes: list[ResultadoValidacaoRead] = []


class ExecucaoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    api_test_id: int
    tipo: TipoExecucao
    executado_em: datetime
    total_casos: int
    total_pass: int
    total_fail: int
    resultados: list[ResultadoLinhaRead] = []
