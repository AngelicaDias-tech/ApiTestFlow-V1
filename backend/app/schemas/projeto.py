from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.cliente import StatusCliente

AmbienteProjeto = Literal["desenvolvimento", "homologacao", "producao"]
StatusProjeto = Literal["ativo", "inativo"]


class ProjetoBase(BaseModel):
    nome: str = Field(min_length=1, max_length=150)
    descricao: Optional[str] = None
    ambiente: AmbienteProjeto = "homologacao"
    status: StatusProjeto = "ativo"


class ProjetoCreate(ProjetoBase):
    cliente_id: int


class ProjetoUpdate(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=1, max_length=150)
    descricao: Optional[str] = None
    ambiente: Optional[AmbienteProjeto] = None
    status: Optional[StatusProjeto] = None
    cliente_id: Optional[int] = None


class ClienteResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    status: StatusCliente


class ProjetoRead(ProjetoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_id: int
    cliente: ClienteResumo
    total_testes: int
    created_at: datetime
    updated_at: datetime
