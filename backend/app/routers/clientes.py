from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.cliente import ClienteCreate, ClienteRead, ClienteUpdate
from app.schemas.projeto import ProjetoBase, ProjetoRead
from app.services import cliente_service, projeto_service

router = APIRouter(prefix="/api/clientes", tags=["clientes"])


@router.get("", response_model=list[ClienteRead])
def listar_clientes(db: Session = Depends(get_db)):
    return cliente_service.listar(db)


@router.get("/{cliente_id}", response_model=ClienteRead)
def obter_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return cliente_service.obter(db, cliente_id)


@router.post("", response_model=ClienteRead, status_code=status.HTTP_201_CREATED)
def criar_cliente(dados: ClienteCreate, db: Session = Depends(get_db)):
    return cliente_service.criar(db, dados)


@router.put("/{cliente_id}", response_model=ClienteRead)
def atualizar_cliente(cliente_id: int, dados: ClienteUpdate, db: Session = Depends(get_db)):
    return cliente_service.atualizar(db, cliente_id, dados)


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente_service.deletar(db, cliente_id)


@router.get("/{cliente_id}/projetos", response_model=list[ProjetoRead])
def listar_projetos_do_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return projeto_service.listar_por_cliente(db, cliente_id)


@router.post("/{cliente_id}/projetos", response_model=ProjetoRead, status_code=status.HTTP_201_CREATED)
def criar_projeto_do_cliente(cliente_id: int, dados: ProjetoBase, db: Session = Depends(get_db)):
    return projeto_service.criar_para_cliente(db, cliente_id, dados)
