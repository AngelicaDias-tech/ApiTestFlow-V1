from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.projeto import Projeto
from app.repositories import cliente_repository, projeto_repository
from app.schemas.projeto import ProjetoBase, ProjetoCreate, ProjetoRead, ProjetoUpdate, ClienteResumo


def _to_read(projeto: Projeto) -> ProjetoRead:
    return ProjetoRead(
        id=projeto.id,
        cliente_id=projeto.cliente_id,
        nome=projeto.nome,
        descricao=projeto.descricao,
        ambiente=projeto.ambiente,
        status=projeto.status,
        cliente=ClienteResumo.model_validate(projeto.cliente),
        total_testes=len(projeto.testes),
        created_at=projeto.created_at,
        updated_at=projeto.updated_at,
    )


def listar(db: Session) -> list[ProjetoRead]:
    return [_to_read(projeto) for projeto in projeto_repository.listar(db)]


def listar_por_cliente(db: Session, cliente_id: int) -> list[ProjetoRead]:
    if cliente_repository.obter(db, cliente_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado.")
    return [_to_read(projeto) for projeto in projeto_repository.listar_por_cliente(db, cliente_id)]


def obter(db: Session, projeto_id: int) -> ProjetoRead:
    projeto = projeto_repository.obter(db, projeto_id)
    if projeto is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Projeto não encontrado.")
    return _to_read(projeto)


def _obter_ou_404(db: Session, projeto_id: int) -> Projeto:
    projeto = projeto_repository.obter(db, projeto_id)
    if projeto is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Projeto não encontrado.")
    return projeto


def criar(db: Session, dados: ProjetoCreate) -> ProjetoRead:
    cliente = cliente_repository.obter(db, dados.cliente_id)
    if cliente is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Cliente informado não existe.")
    projeto = projeto_repository.criar(db, dados)
    return obter(db, projeto.id)


def criar_para_cliente(db: Session, cliente_id: int, dados: ProjetoBase) -> ProjetoRead:
    """Cria o projeto associado ao cliente da rota — o cliente nunca vem do corpo da requisição."""
    if cliente_repository.obter(db, cliente_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado.")
    projeto = projeto_repository.criar(db, ProjetoCreate(cliente_id=cliente_id, **dados.model_dump()))
    return obter(db, projeto.id)


def atualizar(db: Session, projeto_id: int, dados: ProjetoUpdate) -> ProjetoRead:
    projeto = _obter_ou_404(db, projeto_id)
    if dados.cliente_id is not None and cliente_repository.obter(db, dados.cliente_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Cliente informado não existe.")
    projeto_repository.atualizar(db, projeto, dados)
    return obter(db, projeto_id)


def deletar(db: Session, projeto_id: int) -> None:
    projeto = _obter_ou_404(db, projeto_id)
    projeto_repository.deletar(db, projeto)
