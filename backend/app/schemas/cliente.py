from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

StatusCliente = Literal["ativo", "inativo"]


class ClienteBase(BaseModel):
    nome: str = Field(min_length=1, max_length=150)
    status: StatusCliente = "ativo"


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=1, max_length=150)
    status: Optional[StatusCliente] = None


class ClienteRead(ClienteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
