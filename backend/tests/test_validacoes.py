import json

import httpx

from app.services import execucao_service


def _criar_teste(client, cliente_id, **kwargs):
    projeto = client.post("/api/projetos", json={"nome": "Proposta", "cliente_id": cliente_id}).json()
    dados = {
        "nome": "Consulta Proposta",
        "endpoint": "https://api.exemplo.interno/proposta/v1/consulta",
        "metodo_http": "POST",
        "body": json.dumps({"proposta": {"pessoa": [{"documento": "0"}]}}),
    }
    dados.update(kwargs)
    teste = client.post(f"/api/projetos/{projeto['id']}/testes", json=dados).json()
    return teste


def test_cria_lista_atualiza_e_exclui_regra(client, cliente_padrao):
    teste = _criar_teste(client, cliente_padrao["id"])

    resposta_criacao = client.post(
        f"/api/testes/{teste['id']}/regras",
        json={"campo": "decisao", "operador": "equals", "valor_esperado": "Aprovado"},
    )
    assert resposta_criacao.status_code == 200
    regra = resposta_criacao.json()
    assert regra["operador"] == "EQUALS"  # normalizado para maiúsculas

    resposta_lista = client.get(f"/api/testes/{teste['id']}/regras")
    assert resposta_lista.status_code == 200
    assert len(resposta_lista.json()) == 1

    resposta_update = client.put(
        f"/api/testes/{teste['id']}/regras/{regra['id']}",
        json={"campo": "decisao", "operador": "EQUALS", "valor_esperado": "Recusado"},
    )
    assert resposta_update.status_code == 200
    assert resposta_update.json()["valor_esperado"] == "Recusado"

    resposta_delete = client.delete(f"/api/testes/{teste['id']}/regras/{regra['id']}")
    assert resposta_delete.status_code == 204
    assert client.get(f"/api/testes/{teste['id']}/regras").json() == []


def test_operador_invalido_retorna_422(client, cliente_padrao):
    teste = _criar_teste(client, cliente_padrao["id"])

    resposta = client.post(
        f"/api/testes/{teste['id']}/regras",
        json={"campo": "decisao", "operador": "COMECA_COM", "valor_esperado": "A"},
    )

    assert resposta.status_code == 422


def test_regras_isoladas_entre_testes(client, cliente_padrao):
    teste_a = _criar_teste(client, cliente_padrao["id"])
    projeto_b = client.post("/api/projetos", json={"nome": "Crédito", "cliente_id": cliente_padrao["id"]}).json()
    teste_b = client.post(
        f"/api/projetos/{projeto_b['id']}/testes", json={"nome": "Consulta Crédito", "endpoint": "/credito"}
    ).json()

    client.post(f"/api/testes/{teste_a['id']}/regras", json={"campo": "decisao", "operador": "EXISTS"})

    assert client.get(f"/api/testes/{teste_a['id']}/regras").json() != []
    assert client.get(f"/api/testes/{teste_b['id']}/regras").json() == []


class _RespostaFalsa:
    def __init__(self, status_code: int, corpo: dict):
        self.status_code = status_code
        self._corpo = corpo
        self.text = json.dumps(corpo, ensure_ascii=False)

    def json(self):
        return self._corpo


def test_execucao_real_agrupa_por_caso_id_e_aplica_regras(client, cliente_padrao, monkeypatch):
    teste = _criar_teste(
        client,
        cliente_padrao["id"],
        body=json.dumps({"proposta": {"pessoa": [{"documento": "0"}]}}),
    )
    teste_id = teste["id"]

    db = client.testing_session_local()
    try:
        from app.models.massa import MassaImportacao, MassaLinha

        massa = MassaImportacao(api_test_id=teste_id, nome_arquivo="teste.xlsx", total_casos=2, total_linhas=4)
        massa.linhas = [
            MassaLinha(caso_id="TC-01", path="proposta.pessoa[0].documento", acao="set", tipo="string", novo_valor="111", ativo=True),
            MassaLinha(caso_id="TC-01", path="proposta.pessoa[0].telefone", acao="set", tipo="string", novo_valor="999", ativo=False),
            MassaLinha(caso_id="TC-02", path="proposta.pessoa[0].documento", acao="set", tipo="string", novo_valor="222", ativo=True),
        ]
        db.add(massa)
        db.commit()
    finally:
        db.close()

    client.post(f"/api/testes/{teste_id}/regras", json={"campo": "decisao", "operador": "EQUALS", "valor_esperado": "Aprovado"})

    respostas_por_documento = {
        "111": _RespostaFalsa(200, {"decisao": "Aprovado"}),
        "222": _RespostaFalsa(200, {"decisao": "Recusado"}),
    }

    def _request_falso(self, metodo, url, headers=None, params=None, json=None, auth=None):
        documento = json["proposta"]["pessoa"][0]["documento"]
        return respostas_por_documento[documento]

    monkeypatch.setattr(httpx.Client, "request", _request_falso)

    db = client.testing_session_local()
    try:
        execucao = execucao_service.executar(db, teste_id)

        assert execucao.total_casos == 2
        assert execucao.total_pass == 1
        assert execucao.total_fail == 1

        por_caso = {r.caso_id: r for r in execucao.resultados}
        assert por_caso["TC-01"].resultado == "PASS"
        assert por_caso["TC-02"].resultado == "FAIL"

        # a linha inativa (telefone) não deve ter sido aplicada
        request_tc01 = json.loads(por_caso["TC-01"].request_enviado)
        assert "telefone" not in request_tc01["proposta"]["pessoa"][0]

        # a regra de negócio (não o status HTTP) decidiu o resultado
        assert por_caso["TC-01"].validacoes[0].campo == "decisao"
        assert por_caso["TC-01"].validacoes[0].passou is True
        assert por_caso["TC-02"].validacoes[0].passou is False
    finally:
        db.close()
