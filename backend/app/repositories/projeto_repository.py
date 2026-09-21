from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models.projeto import Projeto
from app.schemas.projeto import ProjetoCreate, ProjetoUpdate


def listar(db: Session) -> list[Projeto]:
    return (
        db.query(Projeto)
        .options(joinedload(Projeto.cliente))
        .order_by(Projeto.id.desc())
        .all()
    )


def listar_por_cliente(db: Session, cliente_id: int) -> list[Projeto]:
    return (
        db.query(Projeto)
        .options(joinedload(Projeto.cliente))
        .filter(Projeto.cliente_id == cliente_id)
        .order_by(Projeto.id.desc())
        .all()
    )


def obter(db: Session, projeto_id: int) -> Optional[Projeto]:
    return (
        db.query(Projeto)
        .options(joinedload(Projeto.cliente))
        .filter(Projeto.id == projeto_id)
        .first()
    )


def criar(db: Session, dados: ProjetoCreate) -> Projeto:
    projeto = Projeto(**dados.model_dump())
    db.add(projeto)
    db.commit()
    db.refresh(projeto)
    return projeto


def atualizar(db: Session, projeto: Projeto, dados: ProjetoUpdate) -> Projeto:
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(projeto, campo, valor)
    projeto.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(projeto)
    return projeto


def deletar(db: Session, projeto: Projeto) -> None:
    db.delete(projeto)
    db.commit()
