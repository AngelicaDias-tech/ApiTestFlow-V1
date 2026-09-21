from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.validacao import RegraValidacao
from app.repositories import api_test_repository, validacao_repository
from app.schemas.validacao import RegraValidacaoCreate, RegraValidacaoUpdate
from app.services.regra_engine import OPERADORES_VALIDOS


def _garantir_teste_existe(db: Session, api_test_id: int) -> None:
    if api_test_repository.obter(db, api_test_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Teste não encontrado.")


def _validar_operador(operador: str) -> None:
    if operador.strip().upper() not in OPERADORES_VALIDOS:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Operador inválido. Use um de: {', '.join(OPERADORES_VALIDOS)}.",
        )


def listar_por_teste(db: Session, api_test_id: int) -> list[RegraValidacao]:
    _garantir_teste_existe(db, api_test_id)
    return validacao_repository.listar_por_teste(db, api_test_id)


def criar(db: Session, api_test_id: int, dados: RegraValidacaoCreate) -> RegraValidacao:
    _garantir_teste_existe(db, api_test_id)
    _validar_operador(dados.operador)
    dados.operador = dados.operador.strip().upper()
    return validacao_repository.criar(db, api_test_id, dados)


def atualizar(db: Session, api_test_id: int, regra_id: int, dados: RegraValidacaoUpdate) -> RegraValidacao:
    _garantir_teste_existe(db, api_test_id)
    _validar_operador(dados.operador)
    dados.operador = dados.operador.strip().upper()
    regra = validacao_repository.obter_do_teste(db, api_test_id, regra_id)
    if regra is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Regra de validação não encontrada para este teste.")
    return validacao_repository.atualizar(db, regra, dados)


def excluir(db: Session, api_test_id: int, regra_id: int) -> None:
    _garantir_teste_existe(db, api_test_id)
    regra = validacao_repository.obter_do_teste(db, api_test_id, regra_id)
    if regra is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Regra de validação não encontrada para este teste.")
    validacao_repository.excluir(db, regra)
