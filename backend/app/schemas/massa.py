from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MassaLinhaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    caso_id: str
    path: str
    acao: str
    tipo: Optional[str] = None
    novo_valor: Optional[str] = None
    ativo: bool
    observacao: Optional[str] = None


class MassaImportacaoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    api_test_id: int
    nome_arquivo: str
    total_casos: int
    total_linhas: int
    importado_em: datetime
    linhas: list[MassaLinhaRead] = []
