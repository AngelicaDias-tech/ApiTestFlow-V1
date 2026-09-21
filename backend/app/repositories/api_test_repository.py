from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.api_test import ApiTest
from app.schemas.api_test import ApiTestCreate, ApiTestUpdate


def listar_por_projeto(db: Session, project_id: int) -> list[ApiTest]:
    return (
        db.query(ApiTest)
        .filter(ApiTest.project_id == project_id)
        .order_by(ApiTest.id.desc())
        .all()
    )


def obter(db: Session, teste_id: int) -> Optional[ApiTest]:
    return db.get(ApiTest, teste_id)


def obter_do_projeto(db: Session, project_id: int, teste_id: int) -> Optional[ApiTest]:
    return (
        db.query(ApiTest)
        .filter(ApiTest.id == teste_id, ApiTest.project_id == project_id)
        .first()
    )


def criar(db: Session, project_id: int, dados: ApiTestCreate) -> ApiTest:
    teste = ApiTest(project_id=project_id, **dados.model_dump())
    db.add(teste)
    db.commit()
    db.refresh(teste)
    return teste


def atualizar(db: Session, teste: ApiTest, dados: ApiTestUpdate) -> ApiTest:
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(teste, campo, valor)
    teste.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(teste)
    return teste
