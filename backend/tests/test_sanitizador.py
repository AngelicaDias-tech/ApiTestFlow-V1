from app.services.sanitizador import sanitizar_texto


def test_mascara_ocorrencia_literal_do_segredo():
    texto = '{"token": "abc-super-secreto-123"}'
    resultado = sanitizar_texto(texto, ["abc-super-secreto-123"])
    assert "abc-super-secreto-123" not in resultado
    assert "MASCARADO" in resultado


def test_mascara_chaves_sensiveis_mesmo_sem_bater_com_segredo_conhecido():
    texto = '{"access_token": "novo-token-emitido-pela-api", "usuario": "joao"}'
    resultado = sanitizar_texto(texto, [])
    assert "novo-token-emitido-pela-api" not in resultado
    assert "joao" in resultado  # campo não sensível permanece intacto


def test_nao_altera_texto_sem_segredo_nem_chave_sensivel():
    texto = '{"decisao": "Aprovado", "score": 700}'
    resultado = sanitizar_texto(texto, ["algum-token-nao-presente"])
    assert resultado == texto


def test_texto_nao_json_ainda_mascara_por_valor():
    texto = "Falha ao chamar a API real: header Authorization: Bearer abc123 rejeitado"
    resultado = sanitizar_texto(texto, ["abc123"])
    assert "abc123" not in resultado


def test_texto_none_retorna_none():
    assert sanitizar_texto(None, ["x"]) is None
