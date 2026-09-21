def test_criar_cliente(client):
    resposta = client.post("/api/clientes", json={"nome": "Porto Seguro"})

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["nome"] == "Porto Seguro"
    assert corpo["status"] == "ativo"
    assert "id" in corpo


def test_listar_clientes(client):
    client.post("/api/clientes", json={"nome": "Porto Seguro"})
    client.post("/api/clientes", json={"nome": "Vivo"})

    resposta = client.get("/api/clientes")

    assert resposta.status_code == 200
    nomes = [c["nome"] for c in resposta.json()]
    assert nomes == ["Porto Seguro", "Vivo"]


def test_criar_cliente_sem_nome_retorna_erro_de_validacao(client):
    resposta = client.post("/api/clientes", json={"nome": ""})

    assert resposta.status_code == 422


def test_obter_cliente_por_id(client, cliente_padrao):
    resposta = client.get(f"/api/clientes/{cliente_padrao['id']}")

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Porto Seguro"


def test_obter_cliente_inexistente_retorna_404(client):
    resposta = client.get("/api/clientes/9999")

    assert resposta.status_code == 404


def test_atualizar_cliente(client, cliente_padrao):
    resposta = client.put(f"/api/clientes/{cliente_padrao['id']}", json={"status": "inativo"})

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "inativo"
    assert resposta.json()["nome"] == "Porto Seguro"


def test_deletar_cliente(client, cliente_padrao):
    resposta = client.delete(f"/api/clientes/{cliente_padrao['id']}")
    assert resposta.status_code == 204

    resposta_get = client.get(f"/api/clientes/{cliente_padrao['id']}")
    assert resposta_get.status_code == 404
