from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models.execucao import Execucao


def listar_por_teste(db: Session, api_test_id: int) -> list[Execucao]:
    return (
        db.query(Execucao)
        .filter(Execucao.api_test_id == api_test_id)
        .order_by(Execucao.executado_em.desc())
        .all()
    )


def obter_do_teste(db: Session, api_test_id: int, execucao_id: int) -> Optional[Execucao]:
    return (
        db.query(Execucao)
        .options(joinedload(Execucao.resultados))
        .filter(Execucao.id == execucao_id, Execucao.api_test_id == api_test_id)
        .first()
    )
