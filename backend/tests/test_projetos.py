def test_criar_projeto_associado_a_cliente(client, cliente_padrao):
    resposta = client.post(
        "/api/projetos",
        json={
            "nome": "Análise de Crédito",
            "descricao": "Validação das regras de crédito do cliente.",
            "ambiente": "homologacao",
            "cliente_id": cliente_padrao["id"],
        },
    )

    assert resposta.status_code == 201
    projeto = resposta.json()
    assert projeto["nome"] == "Análise de Crédito"
    assert projeto["cliente"]["id"] == cliente_padrao["id"]
    assert projeto["cliente"]["nome"] == cliente_padrao["nome"]
    assert projeto["total_testes"] == 0


def test_criar_projeto_com_cliente_inexistente_retorna_404(client):
    resposta = client.post(
        "/api/projetos",
        json={"nome": "Projeto X", "cliente_id": 9999},
    )

    assert resposta.status_code == 404


def test_listar_projetos(client, cliente_padrao):
    client.post("/api/projetos", json={"nome": "Análise de Crédito", "cliente_id": cliente_padrao["id"]})
    client.post("/api/projetos", json={"nome": "Proposta", "cliente_id": cliente_padrao["id"]})

    resposta = client.get("/api/projetos")

    assert resposta.status_code == 200
    assert len(resposta.json()) == 2


def test_obter_projeto_por_id(client, cliente_padrao):
    criado = client.post(
        "/api/projetos", json={"nome": "Análise de Crédito", "cliente_id": cliente_padrao["id"]}
    ).json()

    resposta = client.get(f"/api/projetos/{criado['id']}")

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Análise de Crédito"


def test_obter_projeto_inexistente_retorna_404(client):
    resposta = client.get("/api/projetos/9999")

    assert resposta.status_code == 404


def test_atualizar_projeto(client, cliente_padrao):
    criado = client.post(
        "/api/projetos", json={"nome": "Proposta", "cliente_id": cliente_padrao["id"]}
    ).json()

    resposta = client.put(f"/api/projetos/{criado['id']}", json={"status": "inativo"})

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "inativo"


def test_deletar_projeto(client, cliente_padrao):
    criado = client.post(
        "/api/projetos", json={"nome": "Proposta", "cliente_id": cliente_padrao["id"]}
    ).json()

    resposta = client.delete(f"/api/projetos/{criado['id']}")
    assert resposta.status_code == 204

    resposta_get = client.get(f"/api/projetos/{criado['id']}")
    assert resposta_get.status_code == 404


def test_listar_projetos_por_cliente(client, cliente_padrao):
    outro_cliente = client.post("/api/clientes", json={"nome": "Vivo"}).json()

    client.post("/api/projetos", json={"nome": "Proposta", "cliente_id": cliente_padrao["id"]})
    client.post("/api/projetos", json={"nome": "Crédito", "cliente_id": cliente_padrao["id"]})
    client.post("/api/projetos", json={"nome": "Crédito", "cliente_id": outro_cliente["id"]})

    resposta = client.get(f"/api/clientes/{cliente_padrao['id']}/projetos")

    assert resposta.status_code == 200
    projetos = resposta.json()
    assert len(projetos) == 2
    assert all(p["cliente_id"] == cliente_padrao["id"] for p in projetos)


def test_listar_projetos_de_cliente_inexistente_retorna_404(client):
    resposta = client.get("/api/clientes/9999/projetos")

    assert resposta.status_code == 404


def test_criar_projeto_para_cliente(client, cliente_padrao):
    resposta = client.post(
        f"/api/clientes/{cliente_padrao['id']}/projetos",
        json={"nome": "Proposta", "descricao": "Testes de proposta."},
    )

    assert resposta.status_code == 201
    projeto = resposta.json()
    assert projeto["cliente_id"] == cliente_padrao["id"]
    assert projeto["nome"] == "Proposta"
