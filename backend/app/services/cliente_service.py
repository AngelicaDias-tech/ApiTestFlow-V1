from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.repositories import cliente_repository
from app.schemas.cliente import ClienteCreate, ClienteUpdate


def listar(db: Session) -> list[Cliente]:
    return cliente_repository.listar(db)


def obter(db: Session, cliente_id: int) -> Cliente:
    cliente = cliente_repository.obter(db, cliente_id)
    if cliente is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado.")
    return cliente


def criar(db: Session, dados: ClienteCreate) -> Cliente:
    return cliente_repository.criar(db, dados)


def atualizar(db: Session, cliente_id: int, dados: ClienteUpdate) -> Cliente:
    cliente = obter(db, cliente_id)
    return cliente_repository.atualizar(db, cliente, dados)


def deletar(db: Session, cliente_id: int) -> None:
    cliente = obter(db, cliente_id)
    cliente_repository.deletar(db, cliente)
