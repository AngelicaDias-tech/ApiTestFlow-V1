from app.models.execucao import Execucao, ResultadoLinha, ResultadoValidacao


def _criar_projeto_e_teste(client, cliente_id):
    projeto = client.post("/api/projetos", json={"nome": "Proposta", "cliente_id": cliente_id}).json()
    teste = client.post(
        f"/api/projetos/{projeto['id']}/testes",
        json={"nome": "Consulta Proposta", "endpoint": "/proposta/v1/consulta", "metodo_http": "POST"},
    ).json()
    return teste


def test_listar_execucoes_sem_execucao_retorna_lista_vazia(client, cliente_padrao):
    teste = _criar_projeto_e_teste(client, cliente_padrao["id"])

    resposta = client.get(f"/api/testes/{teste['id']}/execucoes")

    assert resposta.status_code == 200
    assert resposta.json() == []


def test_listar_execucoes_de_teste_inexistente_retorna_404(client):
    resposta = client.get("/api/testes/9999/execucoes")

    assert resposta.status_code == 404


def test_execucao_de_demonstracao_com_resultados_por_linha(client, cliente_padrao):
    teste = _criar_projeto_e_teste(client, cliente_padrao["id"])

    db = client.testing_session_local()
    try:
        execucao = Execucao(api_test_id=teste["id"], tipo="demonstracao", total_casos=2, total_pass=1, total_fail=1)
        db.add(execucao)
        db.flush()
        linha_pass = ResultadoLinha(
            execucao_id=execucao.id,
            caso_id="TC-DEMO-01",
            resultado="PASS",
            status_http=200,
        )
        linha_pass.validacoes = [
            ResultadoValidacao(
                campo="status", operador="EQUALS", valor_esperado="APROVADO", valor_obtido="APROVADO", passou=True
            )
        ]
        linha_fail = ResultadoLinha(
            execucao_id=execucao.id,
            caso_id="TC-DEMO-02",
            resultado="FAIL",
            status_http=200,
            motivo_falha="Esperado APROVADO, recebido PENDENTE.",
        )
        linha_fail.validacoes = [
            ResultadoValidacao(
                campo="status",
                operador="EQUALS",
                valor_esperado="APROVADO",
                valor_obtido="PENDENTE",
                passou=False,
                detalhe="obtido='PENDENTE', esperado (EQUALS) 'APROVADO'",
            )
        ]
        db.add_all([linha_pass, linha_fail])
        db.commit()
        execucao_id = execucao.id
    finally:
        db.close()

    resposta_lista = client.get(f"/api/testes/{teste['id']}/execucoes")
    assert resposta_lista.status_code == 200
    assert len(resposta_lista.json()) == 1
    assert resposta_lista.json()[0]["tipo"] == "demonstracao"

    resposta_detalhe = client.get(f"/api/testes/{teste['id']}/execucoes/{execucao_id}")
    assert resposta_detalhe.status_code == 200
    corpo = resposta_detalhe.json()
    assert len(corpo["resultados"]) == 2
    falha = next(r for r in corpo["resultados"] if r["resultado"] == "FAIL")
    assert falha["motivo_falha"] == "Esperado APROVADO, recebido PENDENTE."


def test_obter_execucao_de_outro_teste_retorna_404(client, cliente_padrao):
    teste_a = _criar_projeto_e_teste(client, cliente_padrao["id"])
    projeto_b = client.post("/api/projetos", json={"nome": "Crédito", "cliente_id": cliente_padrao["id"]}).json()
    teste_b = client.post(
        f"/api/projetos/{projeto_b['id']}/testes",
        json={"nome": "Consulta Crédito", "endpoint": "/credito"},
    ).json()

    db = client.testing_session_local()
    try:
        execucao = Execucao(api_test_id=teste_a["id"], tipo="demonstracao", total_casos=0, total_pass=0, total_fail=0)
        db.add(execucao)
        db.commit()
        execucao_id = execucao.id
    finally:
        db.close()

    resposta = client.get(f"/api/testes/{teste_b['id']}/execucoes/{execucao_id}")

    assert resposta.status_code == 404
