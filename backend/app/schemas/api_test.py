from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

MetodoHttp = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
StatusApiTest = Literal["ativo", "inativo"]
TipoAutenticacao = Literal["nenhuma", "bearer_token", "api_key", "basic"]


class ApiTestBase(BaseModel):
    # Identificação
    nome: str = Field(min_length=1, max_length=150)
    descricao: Optional[str] = None

    # Request
    endpoint: str = Field(min_length=1, max_length=500)
    metodo_http: MetodoHttp = "GET"
    headers: Optional[str] = None
    query_params: Optional[str] = None
    path_params: Optional[str] = None
    body: Optional[str] = None

    # Autenticação — ver nota de segurança em app/models/api_test.py
    auth_type: TipoAutenticacao = "nenhuma"
    auth_token: Optional[str] = None

    ambiente: Optional[str] = None
    status: StatusApiTest = "ativo"


class ApiTestCreate(ApiTestBase):
    pass


class ApiTestUpdate(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=1, max_length=150)
    descricao: Optional[str] = None
    endpoint: Optional[str] = Field(default=None, min_length=1, max_length=500)
    metodo_http: Optional[MetodoHttp] = None
    headers: Optional[str] = None
    query_params: Optional[str] = None
    path_params: Optional[str] = None
    body: Optional[str] = None
    auth_type: Optional[TipoAutenticacao] = None
    auth_token: Optional[str] = None
    ambiente: Optional[str] = None
    status: Optional[StatusApiTest] = None


class ApiTestRead(BaseModel):
    """Schema de leitura enviado ao Angular — nunca inclui `auth_token`.

    O token fica disponível apenas dentro do backend (via o modelo ORM) para
    montar a chamada real da API. Expor esse valor em texto pleno no GET seria
    visível em qualquer inspeção de rede (DevTools), então o campo é omitido
    aqui; `possui_token` apenas informa se um token está configurado.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int

    nome: str
    descricao: Optional[str] = None

    endpoint: str
    metodo_http: MetodoHttp
    headers: Optional[str] = None
    query_params: Optional[str] = None
    path_params: Optional[str] = None
    body: Optional[str] = None

    auth_type: TipoAutenticacao
    possui_token: bool = False

    ambiente: Optional[str] = None
    status: StatusApiTest
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def _calcular_possui_token(cls, dados):
        if hasattr(dados, "auth_token"):
            campos = (
                "id", "project_id", "nome", "descricao", "endpoint", "metodo_http",
                "headers", "query_params", "path_params", "body", "auth_type",
                "ambiente", "status", "created_at", "updated_at",
            )
            convertido = {campo: getattr(dados, campo) for campo in campos}
            convertido["possui_token"] = bool(getattr(dados, "auth_token"))
            return convertido
        return dados
