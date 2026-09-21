from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteUpdate


def listar(db: Session) -> list[Cliente]:
    return db.query(Cliente).order_by(Cliente.nome).all()


def obter(db: Session, cliente_id: int) -> Optional[Cliente]:
    return db.get(Cliente, cliente_id)


def criar(db: Session, dados: ClienteCreate) -> Cliente:
    cliente = Cliente(**dados.model_dump())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


def atualizar(db: Session, cliente: Cliente, dados: ClienteUpdate) -> Cliente:
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(cliente, campo, valor)
    cliente.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(cliente)
    return cliente


def deletar(db: Session, cliente: Cliente) -> None:
    db.delete(cliente)
    db.commit()
