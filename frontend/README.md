# API TestFlow — Frontend

SPA em **Angular 19** (standalone components, sem `NgModule`) que consome a API REST do
[backend](../backend) para cadastrar clientes, projetos e testes de API, importar massa de
dados e acompanhar execuções. Veja o [README raiz](../README.md) para a visão geral do produto
e o modelo de domínio.

## Estrutura

```
src/app/
├── core/
│   ├── config/api.config.ts       # URL base da API (http://localhost:8000/api)
│   ├── layout/                    # shell, header e sidebar da aplicação
│   └── services/                  # clientes HTTP (cliente, projeto, api-test, massa,
│                                   # execucao-teste, regra-validacao)
├── features/                      # uma pasta por tela, com componente standalone próprio
│   ├── home/                      # dashboard (resumo, gráfico, execuções recentes)
│   ├── clientes/                  # listagem de clientes
│   ├── cadastrar-cliente/         # formulário de novo cliente
│   ├── cliente-detalhe/           # projetos de um cliente
│   ├── cadastrar-projeto/         # formulário de novo projeto
│   ├── projeto-detalhe/           # testes de um projeto
│   ├── novo-teste/                # formulário de novo teste de API
│   └── teste-detalhe/             # detalhe do teste: massa, regras e execuções
└── shared/
    ├── models/                    # interfaces TypeScript espelhando os schemas da API
    ├── forms/                     # helpers de formulário reativo (api-test-form.ts)
    └── ui/                        # componentes de apresentação reutilizáveis
        # (button, icon, client-card, project-card, api-test-form-fields)
```

## Como rodar

Pré-requisitos: **Node.js 18+** e **npm**. O [backend](../backend) precisa estar rodando em
`http://localhost:8000` para a aplicação funcionar.

```bash
cd frontend
npm install
npm start        # equivalente a `ng serve`
```

A aplicação sobe em `http://localhost:4200` e recarrega automaticamente a cada alteração.

Para apontar para uma API em outro host/porta, altere `API_BASE_URL` em
`src/app/core/config/api.config.ts`.

## Build de produção

```bash
npm run build
```

Os artefatos ficam em `dist/frontend/` (pasta ignorada pelo git).

## Testes

```bash
npm test          # testes unitários com Karma/Jasmine
```

## Navegação (rotas principais)

| Rota | Tela |
|---|---|
| `/` | Dashboard |
| `/clientes` | Lista de clientes |
| `/clientes/novo` | Cadastrar cliente |
| `/clientes/:clientId` | Detalhe do cliente (projetos) |
| `/clientes/:clientId/projetos/novo` | Cadastrar projeto |
| `/clientes/:clientId/projetos/:projectId` | Detalhe do projeto (testes) |
| `/clientes/:clientId/projetos/:projectId/novo-teste` | Cadastrar teste de API |
| `/clientes/:clientId/projetos/:projectId/testes/:testId` | Detalhe do teste (massa, regras, execuções) |
