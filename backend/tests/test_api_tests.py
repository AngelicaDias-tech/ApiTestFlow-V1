def _criar_projeto(client, cliente_id, nome):
    return client.post("/api/projetos", json={"nome": nome, "cliente_id": cliente_id}).json()


def test_criar_teste_associado_a_projeto(client, cliente_padrao):
    projeto = _criar_projeto(client, cliente_padrao["id"], "Análise de Crédito")

    resposta = client.post(
        f"/api/projetos/{projeto['id']}/testes",
        json={
            "nome": "Consulta de crédito",
            "descricao": "Consulta de crédito do cliente.",
            "endpoint": "/credito/v1/analise",
            "metodo_http": "POST",
        },
    )

    assert resposta.status_code == 201
    teste = resposta.json()
    assert teste["project_id"] == projeto["id"]
    assert teste["nome"] == "Consulta de crédito"


def test_criar_teste_em_projeto_inexistente_retorna_404(client):
    resposta = client.post(
        "/api/projetos/9999/testes",
        json={"nome": "Teste", "endpoint": "/x"},
    )

    assert resposta.status_code == 404


def test_listar_testes_de_projeto_inexistente_retorna_404(client):
    resposta = client.get("/api/projetos/9999/testes")

    assert resposta.status_code == 404


def test_projeto_sem_testes_retorna_lista_vazia(client, cliente_padrao):
    projeto = _criar_projeto(client, cliente_padrao["id"], "Proposta")

    resposta = client.get(f"/api/projetos/{projeto['id']}/testes")

    assert resposta.status_code == 200
    assert resposta.json() == []


def test_isolamento_de_testes_entre_projetos(client, cliente_padrao):
    projeto_credito = _criar_projeto(client, cliente_padrao["id"], "Análise de Crédito")
    projeto_proposta = _criar_projeto(client, cliente_padrao["id"], "Proposta")

    client.post(
        f"/api/projetos/{projeto_credito['id']}/testes",
        json={"nome": "Consulta de crédito", "endpoint": "/credito", "metodo_http": "POST"},
    )
    client.post(
        f"/api/projetos/{projeto_credito['id']}/testes",
        json={"nome": "Validação de score", "endpoint": "/score", "metodo_http": "GET"},
    )
    client.post(
        f"/api/projetos/{projeto_proposta['id']}/testes",
        json={"nome": "Consulta proposta", "endpoint": "/proposta", "metodo_http": "GET"},
    )

    testes_credito = client.get(f"/api/projetos/{projeto_credito['id']}/testes").json()
    testes_proposta = client.get(f"/api/projetos/{projeto_proposta['id']}/testes").json()

    assert len(testes_credito) == 2
    assert len(testes_proposta) == 1
    assert {t["nome"] for t in testes_credito} == {"Consulta de crédito", "Validação de score"}
    assert testes_proposta[0]["nome"] == "Consulta proposta"

    # nenhum teste do projeto "Proposta" pode vazar para o projeto "Análise de Crédito" e vice-versa
    ids_credito = {t["id"] for t in testes_credito}
    ids_proposta = {t["id"] for t in testes_proposta}
    assert ids_credito.isdisjoint(ids_proposta)


def test_total_testes_do_projeto_reflete_quantidade_real(client, cliente_padrao):
    projeto = _criar_projeto(client, cliente_padrao["id"], "Análise de Crédito")
    client.post(
        f"/api/projetos/{projeto['id']}/testes",
        json={"nome": "Consulta de crédito", "endpoint": "/credito"},
    )

    resposta = client.get(f"/api/projetos/{projeto['id']}")

    assert resposta.json()["total_testes"] == 1


def test_obter_teste_especifico_do_projeto(client, cliente_padrao):
    projeto = _criar_projeto(client, cliente_padrao["id"], "Análise de Crédito")
    teste = client.post(
        f"/api/projetos/{projeto['id']}/testes",
        json={
            "nome": "Consulta de crédito",
            "endpoint": "/credito",
            "metodo_http": "POST",
            "auth_type": "bearer_token",
            "auth_token": "abc123",
        },
    ).json()

    resposta = client.get(f"/api/projetos/{projeto['id']}/testes/{teste['id']}")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["nome"] == "Consulta de crédito"
    assert corpo["auth_type"] == "bearer_token"
    assert corpo["possui_token"] is True
    assert "auth_token" not in corpo
    assert "abc123" not in resposta.text


def test_atualizar_teste_sem_enviar_token_preserva_o_existente(client, cliente_padrao):
    projeto = _criar_projeto(client, cliente_padrao["id"], "Análise de Crédito")
    teste = client.post(
        f"/api/projetos/{projeto['id']}/testes",
        json={
            "nome": "Consulta de crédito",
            "endpoint": "/credito",
            "metodo_http": "POST",
            "auth_type": "bearer_token",
            "auth_token": "abc123",
        },
    ).json()

    resposta = client.put(
        f"/api/projetos/{projeto['id']}/testes/{teste['id']}",
        json={"nome": "Consulta de crédito (renomeado)"},
    )

    assert resposta.status_code == 200
    assert resposta.json()["possui_token"] is True

    db = client.testing_session_local()
    try:
        from app.models.api_test import ApiTest

        atualizado = db.get(ApiTest, teste["id"])
        assert atualizado.auth_token == "abc123"
    finally:
        db.close()


def test_obter_teste_inexistente_retorna_404(client, cliente_padrao):
    projeto = _criar_projeto(client, cliente_padrao["id"], "Análise de Crédito")

    resposta = client.get(f"/api/projetos/{projeto['id']}/testes/9999")

    assert resposta.status_code == 404


def test_obter_teste_de_outro_projeto_retorna_404(client, cliente_padrao):
    projeto_credito = _criar_projeto(client, cliente_padrao["id"], "Análise de Crédito")
    projeto_proposta = _criar_projeto(client, cliente_padrao["id"], "Proposta")

    teste_credito = client.post(
        f"/api/projetos/{projeto_credito['id']}/testes",
        json={"nome": "Consulta de crédito", "endpoint": "/credito"},
    ).json()

    # o teste existe, mas pertence ao projeto de crédito — buscá-lo pela URL do projeto
    # "Proposta" não pode expor os dados dele.
    resposta = client.get(f"/api/projetos/{projeto_proposta['id']}/testes/{teste_credito['id']}")

    assert resposta.status_code == 404


def test_atualizar_teste_do_projeto(client, cliente_padrao):
    projeto = _criar_projeto(client, cliente_padrao["id"], "Análise de Crédito")
    teste = client.post(
        f"/api/projetos/{projeto['id']}/testes",
        json={"nome": "Consulta de crédito", "endpoint": "/credito"},
    ).json()

    resposta = client.put(
        f"/api/projetos/{projeto['id']}/testes/{teste['id']}",
        json={"status": "inativo", "body": '{"cpf": "123"}'},
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["status"] == "inativo"
    assert corpo["body"] == '{"cpf": "123"}'
    assert corpo["nome"] == "Consulta de crédito"
