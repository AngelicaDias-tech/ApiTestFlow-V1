"""Motor de avaliação de regras de validação (campo x operador x esperado).

Determinístico: a mesma response + as mesmas regras sempre produzem o mesmo
resultado. Não há decisão por IA aqui — só comparação estruturada.

OBTIDO vem sempre da response real da API. ESPERADO vem sempre da regra de
negócio configurada (RegraValidacao). A massa (Atualizacoes) não é usada aqui:
ela define a request, não o resultado esperado da response.
"""

import re
from datetime import date, datetime, timedelta
from typing import Any, Optional

_TOKEN_RE = re.compile(r"^([a-zA-Z0-9_]+)(\[(\d+)\])?$")
_RANGE_RE = re.compile(r"\{(\d+)-(\d+)\}")
_SEQUENCE_RE = re.compile(r"^D\+(-?\d+)\.\.D\+(-?\d+)$", re.IGNORECASE)
_RELATIVE_RE = re.compile(r"^D\+(-?\d+)$", re.IGNORECASE)

_VAZIO = object()  # sentinel: caminho não encontrado na response (diferente de None)

OPERADORES_VALIDOS = [
    "EQUALS",
    "NOT_EQUALS",
    "GREATER_THAN",
    "GREATER_THAN_OR_EQUAL",
    "LESS_THAN",
    "LESS_THAN_OR_EQUAL",
    "CONTAINS",
    "NOT_CONTAINS",
    "EXISTS",
    "NOT_EXISTS",
    "IS_NULL",
    "IS_NOT_NULL",
    "COUNT",
    "SEQUENCE",
    "RELATIVE_DATE",
]


def _parse_path(path: str) -> list[tuple[str, Optional[int]]]:
    tokens = []
    for parte in path.split("."):
        casado = _TOKEN_RE.match(parte.strip())
        if not casado:
            continue
        indice = int(casado.group(3)) if casado.group(3) is not None else None
        tokens.append((casado.group(1), indice))
    return tokens


def obter_valor(response: Any, path: str) -> Any:
    """Retorna o valor no path, ou o sentinel _VAZIO se o path não existir."""
    atual = response
    for chave, indice in _parse_path(path):
        if not isinstance(atual, dict) or chave not in atual:
            return _VAZIO
        atual = atual[chave]
        if indice is not None:
            if not isinstance(atual, list) or indice >= len(atual):
                return _VAZIO
            atual = atual[indice]
    return atual


def _expandir_campo(campo: str) -> list[str]:
    casado = _RANGE_RE.search(campo)
    if not casado:
        return [campo]
    inicio, fim = int(casado.group(1)), int(casado.group(2))
    return [campo[: casado.start()] + str(i) + campo[casado.end():] for i in range(inicio, fim + 1)]


def _vazio_ou_nulo(valor: Any) -> bool:
    return valor is _VAZIO or valor is None or valor == ""


def _parse_data(valor: Any) -> Optional[date]:
    if valor is None or valor is _VAZIO:
        return None
    texto = str(valor)[:10]
    for formato in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            continue
    return None


def _para_numero(valor: Any) -> Optional[float]:
    if valor is None or valor is _VAZIO:
        return None
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


def _avaliar_operador_simples(response: Any, campo: str, operador: str, esperado: Optional[str]) -> dict:
    obtido = obter_valor(response, campo)
    obtido_repr = None if obtido is _VAZIO else obtido

    if operador == "EXISTS":
        passou = obtido is not _VAZIO
    elif operador == "NOT_EXISTS":
        passou = obtido is _VAZIO
    elif operador == "IS_NULL":
        passou = _vazio_ou_nulo(obtido)
    elif operador == "IS_NOT_NULL":
        passou = not _vazio_ou_nulo(obtido)
    elif operador == "EQUALS":
        passou = (not _vazio_ou_nulo(obtido)) and str(obtido_repr) == str(esperado)
    elif operador == "NOT_EQUALS":
        passou = _vazio_ou_nulo(obtido) or str(obtido_repr) != str(esperado)
    elif operador == "CONTAINS":
        passou = (not _vazio_ou_nulo(obtido)) and str(esperado) in str(obtido_repr)
    elif operador == "NOT_CONTAINS":
        passou = _vazio_ou_nulo(obtido) or str(esperado) not in str(obtido_repr)
    elif operador in ("GREATER_THAN", "GREATER_THAN_OR_EQUAL", "LESS_THAN", "LESS_THAN_OR_EQUAL"):
        num_obtido, num_esperado = _para_numero(obtido_repr), _para_numero(esperado)
        if num_obtido is None or num_esperado is None:
            passou = False
        elif operador == "GREATER_THAN":
            passou = num_obtido > num_esperado
        elif operador == "GREATER_THAN_OR_EQUAL":
            passou = num_obtido >= num_esperado
        elif operador == "LESS_THAN":
            passou = num_obtido < num_esperado
        else:
            passou = num_obtido <= num_esperado
    else:
        passou = False

    detalhe = None if passou else f"obtido={obtido_repr!r}, esperado ({operador}) {esperado!r}"
    return {"obtido": obtido_repr, "passou": passou, "detalhe": detalhe}


def _avaliar_count(response: Any, campo: str, esperado: Optional[str]) -> dict:
    campos = _expandir_campo(campo)
    preenchidos = sum(1 for c in campos if not _vazio_ou_nulo(obter_valor(response, c)))
    try:
        esperado_num = int(esperado)
    except (TypeError, ValueError):
        esperado_num = None
    passou = esperado_num is not None and preenchidos == esperado_num
    return {
        "obtido": str(preenchidos),
        "passou": passou,
        "detalhe": None if passou else f"{preenchidos} campo(s) preenchido(s), esperado {esperado}",
    }


def _avaliar_relative_date(response: Any, campo: str, esperado: Optional[str], referencia: date) -> dict:
    casado = _RELATIVE_RE.match((esperado or "").strip())
    obtido = obter_valor(response, campo)
    data_obtida = _parse_data(obtido)
    if not casado or data_obtida is None:
        return {
            "obtido": None if obtido is _VAZIO else obtido,
            "passou": False,
            "detalhe": "Data ausente/inválida na response ou regra RELATIVE_DATE malformada (use 'D+X').",
        }
    data_esperada = referencia + timedelta(days=int(casado.group(1)))
    passou = data_obtida == data_esperada
    return {
        "obtido": data_obtida.isoformat(),
        "passou": passou,
        "detalhe": None if passou else f"esperado {data_esperada.isoformat()}, obtido {data_obtida.isoformat()}",
    }


def _avaliar_sequence(response: Any, campo: str, esperado: Optional[str], referencia: date) -> dict:
    casado = _SEQUENCE_RE.match((esperado or "").strip())
    campos = _expandir_campo(campo)
    if not casado:
        return {
            "obtido": None,
            "passou": False,
            "detalhe": "Regra SEQUENCE malformada (use 'D+X..D+Y').",
        }

    offset_inicio, offset_fim = int(casado.group(1)), int(casado.group(2))
    quantidade_esperada = offset_fim - offset_inicio + 1
    datas_obtidas = [_parse_data(obter_valor(response, c)) for c in campos]
    obtido_repr = ", ".join(d.isoformat() if d else "—" for d in datas_obtidas)

    problemas = []
    if len(campos) != quantidade_esperada:
        problemas.append(f"esperado {quantidade_esperada} datas, campo cobre {len(campos)}")
    if any(d is None for d in datas_obtidas):
        problemas.append("há data ausente ou inválida na sequência")
    else:
        for indice, data_obtida in enumerate(datas_obtidas):
            data_esperada = referencia + timedelta(days=offset_inicio + indice)
            if data_obtida != data_esperada:
                problemas.append(
                    f"{campos[indice]}: obtido {data_obtida.isoformat()}, esperado {data_esperada.isoformat()}"
                )
        if len(set(datas_obtidas)) != len(datas_obtidas):
            problemas.append("há datas duplicadas na sequência")

    passou = not problemas
    return {
        "obtido": obtido_repr,
        "passou": passou,
        "detalhe": None if passou else "; ".join(problemas),
    }


def avaliar_regra(response: Any, campo: str, operador: str, valor_esperado: Optional[str], referencia: date) -> dict:
    """Avalia uma regra isolada e retorna {campo, operador, valor_esperado, valor_obtido, passou, detalhe}."""
    operador_normalizado = (operador or "").strip().upper()

    if operador_normalizado == "SEQUENCE":
        resultado = _avaliar_sequence(response, campo, valor_esperado, referencia)
    elif operador_normalizado == "COUNT":
        resultado = _avaliar_count(response, campo, valor_esperado)
    elif operador_normalizado == "RELATIVE_DATE":
        resultado = _avaliar_relative_date(response, campo, valor_esperado, referencia)
    else:
        resultado = _avaliar_operador_simples(response, campo, operador_normalizado, valor_esperado)

    return {
        "campo": campo,
        "operador": operador_normalizado,
        "valor_esperado": valor_esperado,
        "valor_obtido": resultado["obtido"],
        "passou": resultado["passou"],
        "detalhe": resultado["detalhe"],
    }


def avaliar_regras(regras: list, response: Any, referencia: date) -> tuple[list[dict], bool]:
    """Avalia todas as regras de um caso e retorna (avaliacoes, passou_geral).

    Regras com o mesmo `grupo` (não nulo) são combinadas em OR entre si; regras
    sem grupo, ou de grupos diferentes, precisam TODAS passar (AND) — replica
    a combinação AND/OR pedida para o motor de validações.
    """
    avaliacoes = []
    grupos_or: dict[str, list[bool]] = {}
    resultados_and: list[bool] = []

    for regra in regras:
        avaliacao = avaliar_regra(response, regra.campo, regra.operador, regra.valor_esperado, referencia)
        avaliacao["regra_id"] = regra.id
        avaliacao["descricao"] = regra.descricao
        avaliacoes.append(avaliacao)

        if regra.grupo:
            grupos_or.setdefault(regra.grupo, []).append(avaliacao["passou"])
        else:
            resultados_and.append(avaliacao["passou"])

    passou_geral = all(resultados_and) and all(any(grupo) for grupo in grupos_or.values())
    return avaliacoes, passou_geral
