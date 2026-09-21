from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.api_test import ApiTest
from app.repositories import api_test_repository, projeto_repository
from app.schemas.api_test import ApiTestCreate, ApiTestUpdate


def _garantir_projeto_existe(db: Session, project_id: int) -> None:
    if projeto_repository.obter(db, project_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Projeto não encontrado.")


def listar_por_projeto(db: Session, project_id: int) -> list[ApiTest]:
    _garantir_projeto_existe(db, project_id)
    return api_test_repository.listar_por_projeto(db, project_id)


def obter_do_projeto(db: Session, project_id: int, teste_id: int) -> ApiTest:
    _garantir_projeto_existe(db, project_id)
    teste = api_test_repository.obter_do_projeto(db, project_id, teste_id)
    if teste is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Teste não encontrado neste projeto.")
    return teste


def criar(db: Session, project_id: int, dados: ApiTestCreate) -> ApiTest:
    _garantir_projeto_existe(db, project_id)
    return api_test_repository.criar(db, project_id, dados)


def atualizar(db: Session, project_id: int, teste_id: int, dados: ApiTestUpdate) -> ApiTest:
    teste = obter_do_projeto(db, project_id, teste_id)
    return api_test_repository.atualizar(db, teste, dados)
