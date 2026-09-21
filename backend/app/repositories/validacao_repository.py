from typing import Optional

from sqlalchemy.orm import Session

from app.models.validacao import RegraValidacao
from app.schemas.validacao import RegraValidacaoCreate, RegraValidacaoUpdate


def listar_por_teste(db: Session, api_test_id: int) -> list[RegraValidacao]:
    return (
        db.query(RegraValidacao)
        .filter(RegraValidacao.api_test_id == api_test_id)
        .order_by(RegraValidacao.ordem, RegraValidacao.id)
        .all()
    )


def obter_do_teste(db: Session, api_test_id: int, regra_id: int) -> Optional[RegraValidacao]:
    return (
        db.query(RegraValidacao)
        .filter(RegraValidacao.api_test_id == api_test_id, RegraValidacao.id == regra_id)
        .first()
    )


def criar(db: Session, api_test_id: int, dados: RegraValidacaoCreate) -> RegraValidacao:
    proxima_ordem = db.query(RegraValidacao).filter(RegraValidacao.api_test_id == api_test_id).count()
    regra = RegraValidacao(api_test_id=api_test_id, ordem=proxima_ordem, **dados.model_dump())
    db.add(regra)
    db.commit()
    db.refresh(regra)
    return regra


def atualizar(db: Session, regra: RegraValidacao, dados: RegraValidacaoUpdate) -> RegraValidacao:
    for campo, valor in dados.model_dump().items():
        setattr(regra, campo, valor)
    db.commit()
    db.refresh(regra)
    return regra


def excluir(db: Session, regra: RegraValidacao) -> None:
    db.delete(regra)
    db.commit()
