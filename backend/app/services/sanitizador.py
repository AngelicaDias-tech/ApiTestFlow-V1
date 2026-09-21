"""Remove segredos de textos de request/response ANTES de persistir ou exibir.

Duas camadas de proteção, aplicadas juntas:
1. Por VALOR: qualquer ocorrência literal do(s) segredo(s) realmente usados na
   chamada (token configurado no teste, credenciais de basic auth) é mascarada,
   onde quer que apareça no texto — cobre o caso de uma API de destino ecoar o
   segredo de volta na response.
2. Por NOME DE CAMPO: se o texto for um JSON, qualquer chave conhecida por
   carregar segredo (Authorization, auth_token, access_token, refresh_token,
   client_secret, api_key, token) tem o valor mascarado, mesmo que o valor não
   bata com nenhum segredo conhecido — cobre segredos gerados pela própria API
   (ex.: um novo access_token emitido na resposta).

A avaliação das regras de negócio SEMPRE usa a response original (em memória),
nunca a versão sanitizada — sanitização só afeta o que é persistido/exibido.
"""

import json
from typing import Any, Optional

MASCARA = "***MASCARADO***"

_CHAVES_SENSIVEIS = {
    "authorization",
    "auth_token",
    "access_token",
    "refresh_token",
    "client_secret",
    "api_key",
    "apikey",
    "token",
}


def _mascarar_valor(valor: Any) -> Any:
    if isinstance(valor, str) and valor.lower().startswith("bearer "):
        return f"Bearer {MASCARA}"
    return MASCARA


def _sanitizar_estrutura(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {
            chave: (
                _mascarar_valor(valor)
                if isinstance(chave, str) and chave.lower() in _CHAVES_SENSIVEIS
                else _sanitizar_estrutura(valor)
            )
            for chave, valor in obj.items()
        }
    if isinstance(obj, list):
        return [_sanitizar_estrutura(item) for item in obj]
    return obj


def sanitizar_texto(texto: Optional[str], segredos: Optional[list[str]] = None) -> Optional[str]:
    if texto is None:
        return None

    resultado = texto
    for segredo in segredos or []:
        if segredo:
            resultado = resultado.replace(segredo, MASCARA)

    try:
        objeto = json.loads(resultado)
    except ValueError:
        return resultado

    return json.dumps(_sanitizar_estrutura(objeto), ensure_ascii=False)
