import json
import time
from datetime import date

import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.execucao import Execucao, ResultadoLinha, ResultadoValidacao
from app.models.validacao import RegraValidacao
from app.repositories import api_test_repository, execucao_repository, massa_repository, validacao_repository
from app.services import regra_engine, sanitizador
from app.services.massa_aplicador import aplicar_massa

TIMEOUT_SEGUNDOS = 15.0


def _garantir_teste_existe(db: Session, api_test_id: int) -> None:
    if api_test_repository.obter(db, api_test_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Teste não encontrado.")


def listar_por_teste(db: Session, api_test_id: int) -> list[Execucao]:
    _garantir_teste_existe(db, api_test_id)
    return execucao_repository.listar_por_teste(db, api_test_id)


def obter_do_teste(db: Session, api_test_id: int, execucao_id: int) -> Execucao:
    _garantir_teste_existe(db, api_test_id)
    execucao = execucao_repository.obter_do_teste(db, api_test_id, execucao_id)
    if execucao is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Execução não encontrada para este teste.")
    return execucao


def _parse_headers(texto: str | None) -> dict:
    headers = {}
    for linha in (texto or "").splitlines():
        if ":" in linha:
            chave, valor = linha.split(":", 1)
            if chave.strip():
                headers[chave.strip()] = valor.strip()
    return headers


def _parse_pares(texto: str | None) -> dict:
    pares = {}
    for par in (texto or "").split("&"):
        if "=" in par:
            chave, valor = par.split("=", 1)
            if chave.strip():
                pares[chave.strip()] = valor.strip()
    return pares


def _montar_endpoint(endpoint: str, path_params: str | None) -> str:
    resultado = endpoint
    for chave, valor in _parse_pares(path_params).items():
        resultado = resultado.replace("{" + chave + "}", valor)
    return resultado


def _selecionar_regras(regras: list[RegraValidacao], caso_id: str) -> list[RegraValidacao]:
    """Regras sem caso_id valem para todos os casos; regras com caso_id só valem
    para o caso correspondente."""
    return [regra for regra in regras if regra.caso_id is None or regra.caso_id == caso_id]


def executar(db: Session, api_test_id: int) -> Execucao:
    """Executa o teste de verdade: chama a API configurada via HTTP real para cada
    caso da massa (ou uma única vez, se não houver massa) e persiste o resultado
    genuíno (status HTTP, tempo, request/response reais) como uma Execucao tipo='real'.

    Sem uma regra de validação de campo configurada, o critério de PASS/FAIL é o
    status HTTP da resposta (2xx/3xx = PASS). Uma falha de conexão real (endpoint
    inexistente, timeout, etc.) também é registrada como FAIL com o motivo real.
    """
    teste = api_test_repository.obter(db, api_test_id)
    if teste is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Teste não encontrado.")

    headers = _parse_headers(teste.headers)
    query_params = _parse_pares(teste.query_params)
    endpoint = _montar_endpoint(teste.endpoint, teste.path_params)

    auth = None
    segredos: list[str] = []
    if teste.auth_type == "bearer_token" and teste.auth_token:
        headers["Authorization"] = f"Bearer {teste.auth_token}"
        segredos.append(teste.auth_token)
    elif teste.auth_type == "api_key" and teste.auth_token:
        headers["X-API-Key"] = teste.auth_token
        segredos.append(teste.auth_token)
    elif teste.auth_type == "basic" and teste.auth_token and ":" in teste.auth_token:
        usuario, senha = teste.auth_token.split(":", 1)
        auth = (usuario, senha)
        segredos.extend([teste.auth_token, senha])

    body_base = None
    if teste.body:
        try:
            body_base = json.loads(teste.body)
        except ValueError:
            body_base = None

    massa = massa_repository.obter_por_teste(db, api_test_id)
    if massa and massa.linhas:
        casos: dict[str, list] = {}
        for linha in massa.linhas:
            casos.setdefault(linha.caso_id, []).append(linha)
        casos_para_executar = [
            (caso_id, aplicar_massa(body_base, linhas)) for caso_id, linhas in casos.items()
        ]
    else:
        casos_para_executar = [(teste.nome, body_base)]

    todas_regras = validacao_repository.listar_por_teste(db, api_test_id)
    referencia = date.today()

    resultados: list[ResultadoLinha] = []
    total_pass = 0

    with httpx.Client(timeout=TIMEOUT_SEGUNDOS) as client:
        for caso_id, payload in casos_para_executar:
            inicio = time.perf_counter()
            status_http = None
            response_texto = None
            response_json = None
            motivo_falha = None
            avaliacoes: list[dict] = []

            try:
                resposta = client.request(
                    teste.metodo_http,
                    endpoint,
                    headers=headers or None,
                    params=query_params or None,
                    json=payload if payload is not None else None,
                    auth=auth,
                )
                status_http = resposta.status_code
                response_texto = resposta.text[:4000]
                try:
                    response_json = resposta.json()
                except ValueError:
                    response_json = None

                regras_do_caso = _selecionar_regras(todas_regras, caso_id)
                if regras_do_caso:
                    avaliacoes, passou_geral = regra_engine.avaliar_regras(regras_do_caso, response_json, referencia)
                    resultado_caso = "PASS" if passou_geral else "FAIL"
                    if not passou_geral:
                        motivo_falha = "; ".join(
                            f"{a['campo']}: {a['detalhe']}" for a in avaliacoes if not a["passou"] and a["detalhe"]
                        )
                elif 200 <= status_http < 400:
                    resultado_caso = "PASS"
                else:
                    resultado_caso = "FAIL"
                    motivo_falha = f"A API respondeu com status HTTP {status_http}."
            except httpx.HTTPError as exc:
                resultado_caso = "FAIL"
                motivo_falha = f"Falha ao chamar a API real: {exc}"

            if resultado_caso == "PASS":
                total_pass += 1

            tempo_ms = int((time.perf_counter() - inicio) * 1000)

            request_enviado = json.dumps(payload, ensure_ascii=False) if payload is not None else None

            resultados.append(
                ResultadoLinha(
                    caso_id=caso_id,
                    resultado=resultado_caso,
                    status_http=status_http,
                    tempo_ms=tempo_ms,
                    request_enviado=sanitizador.sanitizar_texto(request_enviado, segredos),
                    response_recebido=sanitizador.sanitizar_texto(response_texto, segredos),
                    motivo_falha=sanitizador.sanitizar_texto(motivo_falha, segredos) if motivo_falha else None,
                    validacoes=[
                        ResultadoValidacao(
                            campo=a["campo"],
                            operador=a["operador"],
                            valor_esperado=a["valor_esperado"],
                            valor_obtido=None if a["valor_obtido"] is None else str(a["valor_obtido"]),
                            passou=a["passou"],
                            descricao=a.get("descricao"),
                            detalhe=a["detalhe"],
                        )
                        for a in avaliacoes
                    ],
                )
            )

    execucao = Execucao(
        api_test_id=api_test_id,
        tipo="real",
        total_casos=len(resultados),
        total_pass=total_pass,
        total_fail=len(resultados) - total_pass,
    )
    execucao.resultados = resultados
    db.add(execucao)
    db.commit()
    db.refresh(execucao)
    return execucao
