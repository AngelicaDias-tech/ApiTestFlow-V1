import io
from pathlib import Path

import openpyxl
import pytest

MODELO_OFICIAL = Path(__file__).resolve().parents[2] / "modelo_atualizacao_request.xlsx"


def _criar_projeto_e_teste(client, cliente_id, nome_projeto="Proposta", nome_teste="Consulta Proposta"):
    projeto = client.post("/api/projetos", json={"nome": nome_projeto, "cliente_id": cliente_id}).json()
    teste = client.post(
        f"/api/projetos/{projeto['id']}/testes",
        json={"nome": nome_teste, "endpoint": "/proposta/v1/consulta", "metodo_http": "POST"},
    ).json()
    return projeto, teste


@pytest.mark.skipif(not MODELO_OFICIAL.exists(), reason="modelo_atualizacao_request.xlsx não está no repositório")
def test_baixar_modelo_oficial(client):
    resposta = client.get("/api/testes/massa/modelo")

    assert resposta.status_code == 200
    assert "spreadsheetml" in resposta.headers["content-type"]


def test_massa_de_teste_sem_massa_retorna_none(client, cliente_padrao):
    _, teste = _criar_projeto_e_teste(client, cliente_padrao["id"])

    resposta = client.get(f"/api/testes/{teste['id']}/massa")

    assert resposta.status_code == 200
    assert resposta.json() is None


def test_massa_de_teste_inexistente_retorna_404(client):
    resposta = client.get("/api/testes/9999/massa")

    assert resposta.status_code == 404


@pytest.mark.skipif(not MODELO_OFICIAL.exists(), reason="modelo_atualizacao_request.xlsx não está no repositório")
def test_importar_massa_a_partir_do_modelo_oficial(client, cliente_padrao):
    _, teste = _criar_projeto_e_teste(client, cliente_padrao["id"])

    with open(MODELO_OFICIAL, "rb") as arquivo:
        resposta = client.post(
            f"/api/testes/{teste['id']}/massa",
            files={
                "arquivo": (
                    "modelo_atualizacao_request.xlsx",
                    arquivo,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
        )

    assert resposta.status_code == 200
    massa = resposta.json()
    assert massa["api_test_id"] == teste["id"]
    assert massa["total_linhas"] > 0
    assert massa["total_casos"] > 0
    assert massa["linhas"][0]["caso_id"]

    resposta_get = client.get(f"/api/testes/{teste['id']}/massa")
    assert resposta_get.status_code == 200
    assert resposta_get.json()["total_linhas"] == massa["total_linhas"]


def test_importar_massa_com_cabecalho_invalido_retorna_422(client, cliente_padrao):
    _, teste = _criar_projeto_e_teste(client, cliente_padrao["id"])

    workbook = openpyxl.Workbook()
    aba = workbook.active
    aba.title = "Atualizacoes"
    aba.append(["coluna_a", "coluna_b"])
    aba.append(["x", "y"])
    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    resposta = client.post(
        f"/api/testes/{teste['id']}/massa",
        files={
            "arquivo": (
                "invalido.xlsx",
                buffer,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )

    assert resposta.status_code == 422


@pytest.mark.skipif(not MODELO_OFICIAL.exists(), reason="modelo_atualizacao_request.xlsx não está no repositório")
def test_massa_isolada_entre_testes(client, cliente_padrao):
    _, teste_a = _criar_projeto_e_teste(client, cliente_padrao["id"], "Proposta", "Consulta Proposta")
    _, teste_b = _criar_projeto_e_teste(client, cliente_padrao["id"], "Crédito", "Consulta Crédito")

    with open(MODELO_OFICIAL, "rb") as arquivo:
        client.post(
            f"/api/testes/{teste_a['id']}/massa",
            files={"arquivo": ("modelo.xlsx", arquivo, "application/octet-stream")},
        )

    resposta_b = client.get(f"/api/testes/{teste_b['id']}/massa")

    assert resposta_b.status_code == 200
    assert resposta_b.json() is None
