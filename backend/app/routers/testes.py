from typing import Optional

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.execucao import ExecucaoRead
from app.schemas.massa import MassaImportacaoRead
from app.schemas.validacao import RegraValidacaoCreate, RegraValidacaoRead, RegraValidacaoUpdate
from app.services import execucao_service, massa_service, validacao_service

router = APIRouter(prefix="/api/testes", tags=["testes"])


@router.get("/massa/modelo")
def baixar_modelo_massa():
    """Disponibiliza o modelo oficial de massa (modelo_atualizacao_request.xlsx)."""
    caminho = massa_service.caminho_modelo()
    return FileResponse(
        caminho,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="modelo_atualizacao_request.xlsx",
    )


@router.get("/{teste_id}/massa", response_model=Optional[MassaImportacaoRead])
def obter_massa_do_teste(teste_id: int, db: Session = Depends(get_db)):
    return massa_service.obter_por_teste(db, teste_id)


@router.post("/{teste_id}/massa", response_model=MassaImportacaoRead)
def importar_massa_do_teste(
    teste_id: int, arquivo: UploadFile = File(...), db: Session = Depends(get_db)
):
    return massa_service.importar(db, teste_id, arquivo)


@router.get("/{teste_id}/execucoes", response_model=list[ExecucaoRead])
def listar_execucoes_do_teste(teste_id: int, db: Session = Depends(get_db)):
    return execucao_service.listar_por_teste(db, teste_id)


@router.get("/{teste_id}/execucoes/{execucao_id}", response_model=ExecucaoRead)
def obter_execucao_do_teste(teste_id: int, execucao_id: int, db: Session = Depends(get_db)):
    return execucao_service.obter_do_teste(db, teste_id, execucao_id)


@router.post("/{teste_id}/executar", response_model=ExecucaoRead)
def executar_teste(teste_id: int, db: Session = Depends(get_db)):
    """Dispara uma execução real: chama a API configurada de verdade (HTTP real)
    e persiste o resultado genuíno como Execucao tipo='real'."""
    return execucao_service.executar(db, teste_id)


@router.get("/{teste_id}/regras", response_model=list[RegraValidacaoRead])
def listar_regras_do_teste(teste_id: int, db: Session = Depends(get_db)):
    return validacao_service.listar_por_teste(db, teste_id)


@router.post("/{teste_id}/regras", response_model=RegraValidacaoRead)
def criar_regra_do_teste(teste_id: int, dados: RegraValidacaoCreate, db: Session = Depends(get_db)):
    return validacao_service.criar(db, teste_id, dados)


@router.put("/{teste_id}/regras/{regra_id}", response_model=RegraValidacaoRead)
def atualizar_regra_do_teste(
    teste_id: int, regra_id: int, dados: RegraValidacaoUpdate, db: Session = Depends(get_db)
):
    return validacao_service.atualizar(db, teste_id, regra_id, dados)


@router.delete("/{teste_id}/regras/{regra_id}", status_code=204)
def excluir_regra_do_teste(teste_id: int, regra_id: int, db: Session = Depends(get_db)):
    validacao_service.excluir(db, teste_id, regra_id)
