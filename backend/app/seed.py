"""Seed de desenvolvimento — grava registros REAIS no banco (não é mock de frontend).

Cria clientes, projetos e testes suficientes para navegar por toda a hierarquia do
produto (Cliente -> Projeto -> Teste), mais a massa OFICIAL completa (20 caso_id,
440 linhas) importada de verdade do modelo_atualizacao_request.xlsx, as regras de
validação de negócio estruturadas para cada caso e uma execução de demonstração
com resultados por caso, para visualizar essas telas antes de rodar contra uma
API real.

Uso:
    python -m app.seed             # só semeia se o banco estiver vazio de clientes
    python -m app.seed --reset     # apaga todas as tabelas e semeia do zero
"""

import json
import sys
from datetime import date, timedelta

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.cliente import Cliente
from app.models.projeto import Projeto
from app.models.api_test import ApiTest
from app.models.validacao import RegraValidacao
from app.services import massa_service
from app.services.massa_aplicador import aplicar_massa
from app.services.regra_engine import avaliar_regras
from app.models.execucao import Execucao, ResultadoLinha, ResultadoValidacao

# Estrutura real da request, conforme a aba CATALOGO_PATHS do modelo oficial
# (modelo_atualizacao_request.xlsx) — é sobre este JSON que as linhas da massa
# (aba Atualizacoes) aplicam suas alterações por caso_id.
BODY_BASE_PROPOSTA = {
    "proposta": {
        "pessoa": [{"documento": "01292596830", "tipoPessoa": "F", "telefone": None}],
        "politica": "EP_v4.2",
        "produto": [
            {
                "nomeProduto": "EmprestimoPessoal",
                "variaveis": {
                    "score_interno": "561",
                    "dias_atraso": "0",
                    "valor_atraso": "0",
                    "var_dec_02": "4",
                    "var_dec_01": "2",
                    "var_dec_03": "2",
                    "segmentacao": "PUR",
                    "RENDA": "2700",
                    "var_texto_3": "3",
                    "var_texto_7": "0",
                    "var_texto_8": "C",
                    "testingBlock": {
                        "flagTestingActivated": "S",
                        "birthDate": "19970919",
                        "scoreHVM1": "841",
                        "scoreHVM2": "845",
                        "statusRegistrationCode": "2",
                        "negativeData": "N",
                    },
                },
            }
        ],
    }
}

# Casos aprovados com carência de 16 datas diárias, D+10 a D+25 (obs. da planilha oficial)
_CASOS_APROVADO_16_DATAS = ["TC-DF-01", "TC-DF-04"]
# Casos aprovados com carência de 36 datas diárias, D+10 a D+45
_CASOS_APROVADO_36_DATAS = ["TC-DF-02", "TC-DF-03", "TC-DF-05"]
# Caso de borda: 16 datas calculadas, campos excedentes (17-36) devem ficar vazios
_CASOS_CAMPOS_EXCEDENTES = ["TC-DF-06"]
# Aprovados por exceção/público especial — a obs. não define D+ exatos, só a contagem
_CASOS_APROVADO_SEM_DATA_EXPLICITA = ["TC-AI-01", "TC-AI-04"]
# Todos os demais casos da planilha (CMA/PB/AI-02/AI-03/DF-07) são recusas sem carência


def _regras_do_caso(caso_id: str) -> list[tuple[str, str, str | None, str]]:
    """Regras estruturadas correspondentes à coluna 'observacao' de cada caso_id
    da planilha oficial — nunca uma comparação textual da observação em si."""
    if caso_id in _CASOS_APROVADO_16_DATAS:
        return [
            ("decisao", "EQUALS", "Aprovado", "Decisão deve ser Aprovado"),
            ("carencia.dt_pag_{1-16}", "SEQUENCE", "D+10..D+25", "Carência: 16 datas diárias de D+10 a D+25"),
        ]
    if caso_id in _CASOS_APROVADO_36_DATAS:
        return [
            ("decisao", "EQUALS", "Aprovado", "Decisão deve ser Aprovado"),
            ("carencia.dt_pag_{1-36}", "SEQUENCE", "D+10..D+45", "Carência: 36 datas diárias de D+10 a D+45"),
        ]
    if caso_id in _CASOS_CAMPOS_EXCEDENTES:
        return [
            ("decisao", "EQUALS", "Aprovado", "Decisão deve ser Aprovado"),
            ("carencia.dt_pag_{1-16}", "COUNT", "16", "16 datas de carência calculadas"),
            ("carencia.dt_pag_{17-36}", "COUNT", "0", "Campos excedentes (17 a 36) ausentes/nulos/vazios"),
        ]
    if caso_id in _CASOS_APROVADO_SEM_DATA_EXPLICITA:
        return [
            ("decisao", "EQUALS", "Aprovado", "Decisão deve ser Aprovado"),
            ("carencia", "EXISTS", None, "Objeto carencia deve existir"),
            ("carencia.dt_pag_{1-16}", "COUNT", "16", "16 datas de carência calculadas"),
        ]
    return [
        ("decisao", "EQUALS", "Recusado", "Decisão deve ser Recusado"),
        ("carencia", "IS_NULL", None, "Carência não deve ser calculada (ausente/nula/vazia)"),
    ]


def _carencia(quantidade: int, offset_inicio_dias: int, referencia: date) -> dict:
    return {
        f"dt_pag_{i}": (referencia + timedelta(days=offset_inicio_dias + i - 1)).isoformat()
        for i in range(1, quantidade + 1)
    }


def _response_demo_do_caso(caso_id: str, referencia: date) -> dict:
    """Response fabricada só para a execução de DEMONSTRAÇÃO (nenhuma API real
    é chamada aqui) — mas avaliada pelo MESMO motor determinístico usado na
    execução real, nunca por um PASS/FAIL decidido manualmente."""
    if caso_id == "TC-DF-03":
        # Quebra proposital: dt_pag_36 sai um dia da sequência esperada, para
        # demonstrar um FAIL real (obtido != esperado) nesta tela.
        carencia = _carencia(36, 10, referencia)
        carencia["dt_pag_36"] = (referencia + timedelta(days=46)).isoformat()
        return {"decisao": "Aprovado", "carencia": carencia}
    if caso_id in _CASOS_APROVADO_16_DATAS:
        return {"decisao": "Aprovado", "carencia": _carencia(16, 10, referencia)}
    if caso_id in _CASOS_APROVADO_36_DATAS:
        return {"decisao": "Aprovado", "carencia": _carencia(36, 10, referencia)}
    if caso_id in _CASOS_CAMPOS_EXCEDENTES:
        return {"decisao": "Aprovado", "carencia": _carencia(16, 10, referencia)}
    if caso_id in _CASOS_APROVADO_SEM_DATA_EXPLICITA:
        return {"decisao": "Aprovado", "carencia": _carencia(16, 10, referencia)}
    return {"decisao": "Recusado", "carencia": None}


def _projeto(cliente_id: int, nome: str, descricao: str) -> Projeto:
    return Projeto(
        cliente_id=cliente_id,
        nome=nome,
        descricao=f"[Demonstração] {descricao}",
        ambiente="homologacao",
        status="ativo",
    )


def _teste(project_id: int, nome: str, descricao: str, **kwargs) -> ApiTest:
    dados = {
        "project_id": project_id,
        "nome": nome,
        "descricao": f"[Demonstração] {descricao}",
        "endpoint": "/api/v1/recurso",
        "metodo_http": "GET",
        "ambiente": "homologacao",
        "status": "ativo",
        "auth_type": "nenhuma",
    }
    dados.update(kwargs)
    return ApiTest(**dados)


def _seed(db) -> None:
    # ------------------------------------------------------------------ CLIENTES
    vivo = Cliente(nome="Vivo", status="ativo")
    porto_seguro = Cliente(nome="Porto Seguro", status="ativo")
    carrefour = Cliente(nome="Carrefour", status="ativo")
    itau = Cliente(nome="Itaú", status="ativo")
    db.add_all([vivo, porto_seguro, carrefour, itau])
    db.flush()  # garante os ids antes de criar os projetos

    # ------------------------------------------------------------------ PROJETOS
    ps_proposta = _projeto(porto_seguro.id, "Proposta", "Testes das APIs relacionadas ao fluxo de proposta.")
    ps_credito = _projeto(porto_seguro.id, "Crédito", "Testes de análise de crédito.")
    vivo_credito = _projeto(vivo.id, "Crédito", "Testes de análise de crédito - Homologação.")
    vivo_consulta_cliente = _projeto(vivo.id, "Consulta Cliente", "Testes de consulta e cadastro de cliente.")
    carrefour_consulta_cliente = _projeto(carrefour.id, "Consulta Cliente", "Testes de consulta de cliente.")
    carrefour_credito = _projeto(carrefour.id, "Análise de Crédito", "Testes de análise de crédito.")
    itau_credito = _projeto(itau.id, "Crédito", "Testes de crédito pessoal.")
    itau_conta = _projeto(itau.id, "Conta", "Testes de consulta de conta e saldo.")
    db.add_all(
        [
            ps_proposta,
            ps_credito,
            vivo_credito,
            vivo_consulta_cliente,
            carrefour_consulta_cliente,
            carrefour_credito,
            itau_credito,
            itau_conta,
        ]
    )
    db.flush()

    # -------------------------------------------------------------------- TESTES
    consulta_proposta = _teste(
        ps_proposta.id,
        "Consulta Proposta",
        "Consulta o status de uma proposta de crédito.",
        endpoint="/proposta/v1/consulta",
        metodo_http="POST",
        headers="Content-Type: application/json",
        body=json.dumps(BODY_BASE_PROPOSTA, ensure_ascii=False),
        auth_type="bearer_token",
        auth_token="demo-token-nao-usar-em-producao",
    )
    validacao_proposta = _teste(
        ps_proposta.id,
        "Validação Proposta",
        "Valida as regras de negócio de uma proposta.",
        endpoint="/proposta/v1/validacao",
        metodo_http="POST",
        headers="Content-Type: application/json",
        body='{"numeroProposta": "998877", "regra": "score_minimo"}',
        auth_type="api_key",
        auth_token="demo-api-key-nao-usar-em-producao",
    )
    analise_fraude = _teste(
        ps_proposta.id,
        "Análise de Fraude",
        "Verifica indícios de fraude na proposta.",
        endpoint="/proposta/v1/fraude",
        metodo_http="POST",
        headers="Content-Type: application/json",
        body='{"documento": "00000000000", "ip": "10.0.0.1"}',
        auth_type="basic",
        auth_token="demo:senha-nao-usar-em-producao",
    )
    teste_execucao_real = _teste(
        ps_proposta.id,
        "Teste de Execução Real (sandbox pública)",
        "Os testes acima usam endpoints internos fictícios da Serasa/Experian e por "
        "isso não existe um servidor de verdade para responder a eles neste ambiente. "
        "Este teste aponta para um serviço público de eco HTTP (httpbin.org) só para "
        "provar, de ponta a ponta, que o motor de execução real do API TestFlow "
        "funciona: ele faz uma chamada HTTP de verdade e grava o resultado genuíno.",
        endpoint="https://httpbin.org/anything",
        metodo_http="POST",
        headers="Content-Type: application/json",
        body='{"mensagem": "Teste real do API TestFlow", "documento": "00000000000"}',
        auth_type="bearer_token",
        auth_token="demo-token-sandbox-publica",
    )
    consulta_credito_ps = _teste(
        ps_credito.id,
        "Consulta Crédito",
        "Consulta de crédito do cliente.",
        endpoint="/credito/v1/analise",
        metodo_http="GET",
        query_params="documento=00000000000&produto=emprestimo",
    )
    validacao_score = _teste(
        ps_credito.id,
        "Validação Score",
        "Valida o score de crédito retornado.",
        endpoint="/credito/v1/score/{documento}",
        metodo_http="GET",
        path_params="documento=00000000000",
        auth_type="bearer_token",
        auth_token="demo-token-nao-usar-em-producao",
    )
    consulta_credito_vivo = _teste(
        vivo_credito.id,
        "Consulta Crédito",
        "Consulta de crédito do cliente.",
        endpoint="/credito/v1/analise",
        metodo_http="POST",
        headers="Content-Type: application/json",
        body='{"documento": "00000000000"}',
        auth_type="bearer_token",
        auth_token="demo-token-nao-usar-em-producao",
    )
    validacao_limite = _teste(
        vivo_credito.id,
        "Validação Limite",
        "Valida o limite de crédito aprovado.",
        endpoint="/credito/v1/limite",
        metodo_http="GET",
        query_params="documento=00000000000",
    )
    consulta_cadastro_vivo = _teste(
        vivo_consulta_cliente.id,
        "Consulta Cadastro",
        "Consulta os dados cadastrais do cliente.",
        endpoint="/cliente/v1/cadastro",
        metodo_http="GET",
        query_params="documento=00000000000",
    )
    validacao_cadastro_vivo = _teste(
        vivo_consulta_cliente.id,
        "Validação Cadastro",
        "Valida se o cadastro do cliente está completo.",
        endpoint="/cliente/v1/cadastro/validar",
        metodo_http="POST",
        headers="Content-Type: application/json",
        body='{"documento": "00000000000"}',
    )
    consulta_cadastro_carrefour = _teste(
        carrefour_consulta_cliente.id,
        "Consulta Cadastro",
        "Consulta os dados cadastrais do cliente Carrefour.",
        endpoint="/cliente/v1/cadastro",
        metodo_http="GET",
        query_params="documento=00000000000",
    )
    consulta_credito_carrefour = _teste(
        carrefour_credito.id,
        "Consulta Crédito",
        "Consulta de crédito do cliente Carrefour.",
        endpoint="/credito/v1/analise",
        metodo_http="POST",
        headers="Content-Type: application/json",
        body='{"documento": "00000000000"}',
        auth_type="bearer_token",
        auth_token="demo-token-nao-usar-em-producao",
    )
    consulta_credito_itau = _teste(
        itau_credito.id,
        "Consulta Crédito",
        "Consulta de crédito pessoal Itaú.",
        endpoint="/credito/v1/analise",
        metodo_http="POST",
        headers="Content-Type: application/json",
        body='{"documento": "00000000000"}',
        auth_type="bearer_token",
        auth_token="demo-token-nao-usar-em-producao",
    )
    consulta_saldo_itau = _teste(
        itau_conta.id,
        "Consulta Saldo",
        "Consulta o saldo disponível da conta.",
        endpoint="/conta/v1/saldo",
        metodo_http="GET",
        query_params="conta=00012345",
    )

    todos_os_testes = [
        consulta_proposta,
        validacao_proposta,
        analise_fraude,
        teste_execucao_real,
        consulta_credito_ps,
        validacao_score,
        consulta_credito_vivo,
        validacao_limite,
        consulta_cadastro_vivo,
        validacao_cadastro_vivo,
        consulta_cadastro_carrefour,
        consulta_credito_carrefour,
        consulta_credito_itau,
        consulta_saldo_itau,
    ]
    db.add_all(todos_os_testes)
    db.flush()

    # ---------------------------------------------------------- MASSA OFICIAL
    # Importa o modelo oficial de verdade (mesma rotina usada pelo upload real),
    # com os 20 caso_id / 440 linhas completos — nenhum recorte.
    caminho_modelo = massa_service.caminho_modelo()
    with open(caminho_modelo, "rb") as arquivo:
        linhas = massa_service._ler_planilha(arquivo)
    caso_ids = list(dict.fromkeys(linha["caso_id"] for linha in linhas))
    massa_service.massa_repository.substituir(
        db, consulta_proposta.id, "modelo_atualizacao_request.xlsx", linhas
    )
    massa_criada = massa_service.massa_repository.obter_por_teste(db, consulta_proposta.id)
    linhas_por_caso: dict[str, list] = {}
    for linha_orm in massa_criada.linhas:
        linhas_por_caso.setdefault(linha_orm.caso_id, []).append(linha_orm)

    # --------------------------------------- REGRAS DE VALIDAÇÃO DE NEGÓCIO
    # Estruturadas a partir da coluna 'observacao' de cada caso_id — a massa
    # define a REQUEST (entrada); estas regras definem o que se espera da
    # RESPONSE (saída), que são conceitos diferentes.
    regras_por_caso: dict[str, list[RegraValidacao]] = {}
    ordem = 0
    for caso_id in caso_ids:
        regras_do_caso = []
        for campo, operador, valor_esperado, descricao in _regras_do_caso(caso_id):
            regra = RegraValidacao(
                api_test_id=consulta_proposta.id,
                caso_id=caso_id,
                ordem=ordem,
                campo=campo,
                operador=operador,
                valor_esperado=valor_esperado,
                descricao=descricao,
            )
            db.add(regra)
            regras_do_caso.append(regra)
            ordem += 1
        regras_por_caso[caso_id] = regras_do_caso
    db.flush()

    # -------------------------------------------- EXECUÇÃO DE DEMONSTRAÇÃO
    # Dados persistidos no banco, claramente marcados como 'demonstracao': a
    # request de cada caso é construída de verdade a partir da massa (mesmo
    # motor usado na execução real); a response é fabricada (nenhuma API foi
    # chamada aqui), mas o PASS/FAIL é decidido pelo MESMO motor determinístico
    # de regras usado na execução real — nunca escolhido manualmente.
    referencia_demo = date.today()
    execucao = Execucao(api_test_id=consulta_proposta.id, tipo="demonstracao", total_casos=0, total_pass=0, total_fail=0)
    db.add(execucao)
    db.flush()

    total_pass = 0
    for caso_id in caso_ids:
        request_montado = aplicar_massa(BODY_BASE_PROPOSTA, linhas_por_caso[caso_id])
        response_fabricada = _response_demo_do_caso(caso_id, referencia_demo)
        avaliacoes, passou = avaliar_regras(regras_por_caso[caso_id], response_fabricada, referencia_demo)
        if passou:
            total_pass += 1

        resultado_linha = ResultadoLinha(
            execucao_id=execucao.id,
            caso_id=caso_id,
            resultado="PASS" if passou else "FAIL",
            status_http=200,
            tempo_ms=280 + (hash(caso_id) % 220),
            request_enviado=json.dumps(request_montado, ensure_ascii=False),
            response_recebido=json.dumps(response_fabricada, ensure_ascii=False),
            motivo_falha=None
            if passou
            else "; ".join(a["detalhe"] for a in avaliacoes if not a["passou"] and a["detalhe"]),
        )
        resultado_linha.validacoes = [
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
        ]
        db.add(resultado_linha)

    execucao.total_casos = len(caso_ids)
    execucao.total_pass = total_pass
    execucao.total_fail = len(caso_ids) - total_pass

    db.commit()

    print(
        f"  {4} clientes, {8} projetos, {len(todos_os_testes)} testes, "
        f"1 massa ({len(linhas)} linhas / {len(caso_ids)} casos), "
        f"{ordem} regras de validação e 1 execução de demonstração "
        f"({total_pass} PASS / {len(caso_ids) - total_pass} FAIL)."
    )


def main() -> None:
    reset = "--reset" in sys.argv

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if reset:
            print("Removendo todas as tabelas e recriando o schema...")
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)
        elif db.query(Cliente).count() > 0:
            print("Já existem clientes no banco — seed não executado (use --reset para recomeçar).")
            return

        _seed(db)
        print("Seed de desenvolvimento aplicado com sucesso.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
