# API TestFlow — Backend

API REST em **FastAPI + SQLAlchemy** que persiste Clientes, Projetos e Testes de API em banco
real (SQLite em desenvolvimento; troque `DATABASE_URL` para usar Postgres sem alterar código).

## Hierarquia de negócio

```
Cliente -> Projeto -> Teste de API (ApiTest) -> Massa / Regras de Validação / Execuções
```

Um teste sempre pertence a um projeto; um projeto sempre pertence a um cliente. Não existem
testes globais nem testes vinculados diretamente a um cliente. Veja o
[README raiz](../README.md#visão-geral-do-domínio) para o modelo de domínio completo.

## Estrutura

```
app/
├── main.py            # criação do app FastAPI, CORS, criação das tabelas
├── core/config.py     # DATABASE_URL e CORS_ORIGINS via variáveis de ambiente
├── db/                 # engine, sessão e Base declarativa
├── models/             # Cliente, Projeto, ApiTest, MassaImportacao/MassaLinha,
│                       # Execucao/ResultadoLinha/ResultadoValidacao, RegraValidacao
├── schemas/            # Pydantic (request/response)
├── repositories/       # acesso a dados (queries)
├── services/           # regras de negócio: validações, engine de regras (regra_engine.py),
│                       # importação de massa (massa_service.py), execução de testes
│                       # (execucao_service.py) e sanitização (sanitizador.py)
└── routers/             # endpoints REST (clientes, projetos, testes)
tests/                    # pytest + TestClient, banco SQLite em memória por teste
```

## Como rodar

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

A API sobe em `http://localhost:8000`. Documentação interativa em `http://localhost:8000/docs`.

## Testes automatizados

```bash
cd backend
pytest -v
```

## Endpoints

| Método | Rota                          | Descrição                                   |
|--------|-------------------------------|----------------------------------------------|
| GET    | `/api/clientes`                | Lista clientes                                |
| POST   | `/api/clientes`                | Cria cliente                                  |
| GET    | `/api/projetos`                | Lista projetos (com cliente e total de testes)|
| GET    | `/api/projetos/{id}`           | Detalhe de um projeto                         |
| POST   | `/api/projetos`                | Cria projeto (exige `cliente_id` válido)      |
| PUT    | `/api/projetos/{id}`           | Atualiza projeto                              |
| DELETE | `/api/projetos/{id}`           | Remove projeto                                |
| GET    | `/api/projetos/{id}/testes`    | Lista testes **daquele** projeto (isolado)    |
| POST   | `/api/projetos/{id}/testes`    | Cria teste vinculado ao projeto               |
| GET    | `/api/testes/massa/modelo`     | Baixa o modelo oficial de massa (`.xlsx`)     |
| GET    | `/api/testes/{id}/massa`       | Consulta a massa importada para o teste       |
| POST   | `/api/testes/{id}/massa`       | Importa/substitui a massa do teste (upload de planilha) |
| GET    | `/api/testes/{id}/regras`      | Lista as regras de validação do teste         |
| POST   | `/api/testes/{id}/regras`      | Cria uma regra de validação                   |
| PUT    | `/api/testes/{id}/regras/{regra_id}` | Atualiza uma regra de validação         |
| DELETE | `/api/testes/{id}/regras/{regra_id}` | Remove uma regra de validação           |
| POST   | `/api/testes/{id}/executar`    | Dispara uma execução real (chamada HTTP de verdade) |
| GET    | `/api/testes/{id}/execucoes`   | Lista o histórico de execuções do teste       |
| GET    | `/api/testes/{id}/execucoes/{execucao_id}` | Detalhe de uma execução (PASS/FAIL por caso) |

A lista completa e interativa, com os schemas de request/response, está sempre disponível em
`http://localhost:8000/docs` (Swagger UI) com o servidor rodando.

## Dados de desenvolvimento

Não há seed automático de clientes/projetos fictícios. Para começar a usar o sistema, cadastre
um cliente real via `POST /api/clientes` (a tela de "Cadastrar Projeto" no frontend já oferece
essa opção) e depois um projeto vinculado a ele.

## Próximos passos (fora do escopo desta etapa)

Execução real via pytest, autenticação/SSO, fila/worker e secrets vault serão adicionados
posteriormente. O modelo `ApiTest` já guarda endpoint/método/headers para suportar isso sem
migração estrutural.
