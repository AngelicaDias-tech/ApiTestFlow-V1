from typing import Optional

from pydantic import BaseModel, ConfigDict


class RegraValidacaoBase(BaseModel):
    caso_id: Optional[str] = None
    campo: str
    operador: str
    valor_esperado: Optional[str] = None
    grupo: Optional[str] = None
    descricao: Optional[str] = None


class RegraValidacaoCreate(RegraValidacaoBase):
    pass


class RegraValidacaoUpdate(RegraValidacaoBase):
    pass


class RegraValidacaoRead(RegraValidacaoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    api_test_id: int
    ordem: int
