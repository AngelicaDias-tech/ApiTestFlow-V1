"""Aplica as linhas de uma massa (path/acao/novo_valor) sobre o body base de um teste.

Usado pelo motor de execução real: cada caso_id da massa gera uma cópia do body
configurado no teste com as alterações da planilha aplicadas, antes de enviar a
requisição real.
"""

import copy
import json
import re
from typing import Any, Optional

_TOKEN_RE = re.compile(r"^([a-zA-Z0-9_]+)(\[(\d+)\])?$")


def _parse_path(path: str) -> list[tuple[str, Optional[int]]]:
    tokens = []
    for parte in path.split("."):
        casado = _TOKEN_RE.match(parte.strip())
        if not casado:
            continue
        indice = int(casado.group(3)) if casado.group(3) is not None else None
        tokens.append((casado.group(1), indice))
    return tokens


def _converter_valor(valor: Optional[str], tipo: Optional[str]) -> Any:
    tipo_normalizado = (tipo or "string").strip().lower()
    if tipo_normalizado == "null":
        return None
    if valor is None:
        return None
    try:
        if tipo_normalizado in ("int", "integer"):
            return int(valor)
        if tipo_normalizado in ("float", "decimal", "number"):
            return float(valor) if "." in valor else int(valor)
        if tipo_normalizado in ("bool", "boolean"):
            return str(valor).strip().lower() in ("true", "1", "sim")
        if tipo_normalizado in ("object", "array"):
            return json.loads(valor)
    except (TypeError, ValueError):
        pass
    return valor


def aplicar_massa(body_base: Optional[dict], linhas: list) -> Optional[dict]:
    """Retorna uma cópia do body_base com as linhas ativas (set/delete) aplicadas.

    Linhas cujo path não existe no body base são ignoradas silenciosamente (a massa
    pode conter variações que não se aplicam a todos os casos).
    """
    if body_base is None:
        return None

    body = copy.deepcopy(body_base)

    for linha in linhas:
        if not linha.ativo:
            continue
        tokens = _parse_path(linha.path)
        if not tokens:
            continue
        try:
            atual = body
            for chave, indice in tokens[:-1]:
                atual = atual[chave]
                if indice is not None:
                    atual = atual[indice]

            ultima_chave, ultimo_indice = tokens[-1]
            if linha.acao == "delete":
                if ultimo_indice is not None:
                    del atual[ultima_chave][ultimo_indice]
                else:
                    del atual[ultima_chave]
            else:
                valor = _converter_valor(linha.novo_valor, linha.tipo)
                if ultimo_indice is not None:
                    atual[ultima_chave][ultimo_indice] = valor
                else:
                    atual[ultima_chave] = valor
        except (KeyError, IndexError, TypeError):
            continue

    return body
