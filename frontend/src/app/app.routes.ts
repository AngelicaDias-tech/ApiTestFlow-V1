import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./core/layout/shell/shell.component').then((m) => m.ShellComponent),
    children: [
      {
        path: '',
        loadComponent: () =>
          import('./features/home/home.component').then((m) => m.HomeComponent)
      },
      {
        path: 'clientes',
        loadComponent: () =>
          import('./features/clientes/clientes.component').then((m) => m.ClientesComponent)
      },
      {
        path: 'clientes/novo',
        loadComponent: () =>
          import('./features/cadastrar-cliente/cadastrar-cliente.component').then(
            (m) => m.CadastrarClienteComponent
          )
      },
      {
        path: 'clientes/:clientId',
        loadComponent: () =>
          import('./features/cliente-detalhe/cliente-detalhe.component').then(
            (m) => m.ClienteDetalheComponent
          )
      },
      {
        path: 'clientes/:clientId/projetos/novo',
        loadComponent: () =>
          import('./features/cadastrar-projeto/cadastrar-projeto.component').then(
            (m) => m.CadastrarProjetoComponent
          )
      },
      {
        path: 'clientes/:clientId/projetos/:projectId',
        loadComponent: () =>
          import('./features/projeto-detalhe/projeto-detalhe.component').then(
            (m) => m.ProjetoDetalheComponent
          )
      },
      {
        path: 'clientes/:clientId/projetos/:projectId/novo-teste',
        loadComponent: () =>
          import('./features/novo-teste/novo-teste.component').then((m) => m.NovoTesteComponent)
      },
      {
        path: 'clientes/:clientId/projetos/:projectId/testes/:testId',
        loadComponent: () =>
          import('./features/teste-detalhe/teste-detalhe.component').then(
            (m) => m.TesteDetalheComponent
          )
      }
      // Próxima tela (Configurações) entra aqui como rota filha do mesmo shell.
    ]
  }
];
