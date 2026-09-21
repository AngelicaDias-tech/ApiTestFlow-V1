from datetime import date, timedelta
from types import SimpleNamespace

from app.services import regra_engine


def _regra(campo, operador, valor_esperado=None, caso_id=None, grupo=None, id=1, descricao=None):
    return SimpleNamespace(
        id=id, campo=campo, operador=operador, valor_esperado=valor_esperado, caso_id=caso_id, grupo=grupo,
        descricao=descricao,
    )


def test_equals_passa_quando_valor_bate():
    resultado = regra_engine.avaliar_regra({"decisao": "Aprovado"}, "decisao", "EQUALS", "Aprovado", date.today())
    assert resultado["passou"] is True
    assert resultado["valor_obtido"] == "Aprovado"


def test_equals_falha_quando_campo_ausente():
    resultado = regra_engine.avaliar_regra({}, "decisao", "EQUALS", "Aprovado", date.today())
    assert resultado["passou"] is False


def test_exists_e_not_exists():
    response = {"carencia": {"dt_pag_1": "2026-01-01"}}
    assert regra_engine.avaliar_regra(response, "carencia", "EXISTS", None, date.today())["passou"] is True
    assert regra_engine.avaliar_regra(response, "carencia.dt_pag_2", "NOT_EXISTS", None, date.today())["passou"] is True


def test_is_null_considera_ausente_nulo_e_vazio():
    for response in ({}, {"carencia": None}, {"carencia": ""}):
        assert regra_engine.avaliar_regra(response, "carencia", "IS_NULL", None, date.today())["passou"] is True
    assert regra_engine.avaliar_regra({"carencia": {}}, "carencia", "IS_NULL", None, date.today())["passou"] is False


def test_greater_than_numerico():
    resultado = regra_engine.avaliar_regra({"limite": 4500}, "limite", "GREATER_THAN", "5000", date.today())
    assert resultado["passou"] is False
    resultado2 = regra_engine.avaliar_regra({"limite": 5500}, "limite", "GREATER_THAN", "5000", date.today())
    assert resultado2["passou"] is True


def test_count_com_range_de_campos():
    response = {"carencia": {f"dt_pag_{i}": f"2026-01-{i:02d}" for i in range(1, 17)}}
    resultado = regra_engine.avaliar_regra(response, "carencia.dt_pag_{1-16}", "COUNT", "16", date.today())
    assert resultado["passou"] is True

    resultado_falho = regra_engine.avaliar_regra(response, "carencia.dt_pag_{1-20}", "COUNT", "20", date.today())
    assert resultado_falho["passou"] is False


def test_sequence_datas_diarias_consecutivas():
    referencia = date(2026, 1, 1)
    response = {
        "carencia": {
            f"dt_pag_{i}": (referencia + timedelta(days=9 + i)).isoformat() for i in range(1, 17)
        }
    }
    resultado = regra_engine.avaliar_regra(
        response, "carencia.dt_pag_{1-16}", "SEQUENCE", "D+10..D+25", referencia
    )
    assert resultado["passou"] is True


def test_sequence_falha_quando_uma_data_diverge():
    referencia = date(2026, 1, 1)
    datas = {f"dt_pag_{i}": (referencia + timedelta(days=9 + i)).isoformat() for i in range(1, 17)}
    datas["dt_pag_16"] = (referencia + timedelta(days=26)).isoformat()  # deveria ser D+25
    resultado = regra_engine.avaliar_regra(
        {"carencia": datas}, "carencia.dt_pag_{1-16}", "SEQUENCE", "D+10..D+25", referencia
    )
    assert resultado["passou"] is False
    assert "dt_pag_16" in resultado["detalhe"]


def test_relative_date():
    referencia = date(2026, 1, 1)
    esperado = (referencia + timedelta(days=10)).isoformat()
    resultado = regra_engine.avaliar_regra({"dt": esperado}, "dt", "RELATIVE_DATE", "D+10", referencia)
    assert resultado["passou"] is True


def test_avaliar_regras_and_entre_regras_sem_grupo():
    regras = [_regra("decisao", "EQUALS", "Aprovado", id=1), _regra("carencia", "EXISTS", id=2)]
    avaliacoes, passou = regra_engine.avaliar_regras(regras, {"decisao": "Aprovado"}, date.today())
    assert passou is False  # carencia não existe na response
    assert len(avaliacoes) == 2


def test_avaliar_regras_or_dentro_do_mesmo_grupo():
    regras = [
        _regra("motivo", "EQUALS", "A", id=1, grupo="motivo_ok"),
        _regra("motivo", "EQUALS", "B", id=2, grupo="motivo_ok"),
    ]
    avaliacoes, passou = regra_engine.avaliar_regras(regras, {"motivo": "B"}, date.today())
    assert passou is True
