from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models.massa import MassaImportacao, MassaLinha


def obter_por_teste(db: Session, api_test_id: int) -> Optional[MassaImportacao]:
    return (
        db.query(MassaImportacao)
        .options(joinedload(MassaImportacao.linhas))
        .filter(MassaImportacao.api_test_id == api_test_id)
        .first()
    )


def substituir(
    db: Session, api_test_id: int, nome_arquivo: str, linhas: list[dict]
) -> MassaImportacao:
    existente = obter_por_teste(db, api_test_id)
    if existente is not None:
        db.delete(existente)
        db.flush()

    casos_distintos = {linha["caso_id"] for linha in linhas}
    massa = MassaImportacao(
        api_test_id=api_test_id,
        nome_arquivo=nome_arquivo,
        total_casos=len(casos_distintos),
        total_linhas=len(linhas),
    )
    massa.linhas = [MassaLinha(**linha) for linha in linhas]

    db.add(massa)
    db.commit()
    db.refresh(massa)
    return massa
