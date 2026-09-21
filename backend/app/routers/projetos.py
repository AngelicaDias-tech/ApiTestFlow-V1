from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.api_test import ApiTestCreate, ApiTestRead, ApiTestUpdate
from app.schemas.projeto import ProjetoCreate, ProjetoRead, ProjetoUpdate
from app.services import api_test_service, projeto_service

router = APIRouter(prefix="/api/projetos", tags=["projetos"])


@router.get("", response_model=list[ProjetoRead])
def listar_projetos(db: Session = Depends(get_db)):
    return projeto_service.listar(db)


@router.get("/{projeto_id}", response_model=ProjetoRead)
def obter_projeto(projeto_id: int, db: Session = Depends(get_db)):
    return projeto_service.obter(db, projeto_id)


@router.post("", response_model=ProjetoRead, status_code=status.HTTP_201_CREATED)
def criar_projeto(dados: ProjetoCreate, db: Session = Depends(get_db)):
    return projeto_service.criar(db, dados)


@router.put("/{projeto_id}", response_model=ProjetoRead)
def atualizar_projeto(projeto_id: int, dados: ProjetoUpdate, db: Session = Depends(get_db)):
    return projeto_service.atualizar(db, projeto_id, dados)


@router.delete("/{projeto_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_projeto(projeto_id: int, db: Session = Depends(get_db)):
    projeto_service.deletar(db, projeto_id)


@router.get("/{projeto_id}/testes", response_model=list[ApiTestRead])
def listar_testes_do_projeto(projeto_id: int, db: Session = Depends(get_db)):
    return api_test_service.listar_por_projeto(db, projeto_id)


@router.post("/{projeto_id}/testes", response_model=ApiTestRead, status_code=status.HTTP_201_CREATED)
def criar_teste_do_projeto(projeto_id: int, dados: ApiTestCreate, db: Session = Depends(get_db)):
    return api_test_service.criar(db, projeto_id, dados)


@router.get("/{projeto_id}/testes/{teste_id}", response_model=ApiTestRead)
def obter_teste_do_projeto(projeto_id: int, teste_id: int, db: Session = Depends(get_db)):
    return api_test_service.obter_do_projeto(db, projeto_id, teste_id)


@router.put("/{projeto_id}/testes/{teste_id}", response_model=ApiTestRead)
def atualizar_teste_do_projeto(
    projeto_id: int, teste_id: int, dados: ApiTestUpdate, db: Session = Depends(get_db)
):
    return api_test_service.atualizar(db, projeto_id, teste_id, dados)
