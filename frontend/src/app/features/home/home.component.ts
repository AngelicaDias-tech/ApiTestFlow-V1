import { Component, OnInit, computed, signal } from '@angular/core';
import { Router } from '@angular/router';
import { forkJoin } from 'rxjs';
import { HeroBannerComponent } from './components/hero-banner/hero-banner.component';
import { ClientsOverviewComponent } from './components/clients-overview/clients-overview.component';
import { RecentExecutionsComponent } from './components/recent-executions/recent-executions.component';
import { SummaryPanelComponent } from './components/summary-panel/summary-panel.component';
import { ProjetoService } from '../../core/services/projeto.service';
import { ClienteService } from '../../core/services/cliente.service';
import { Cliente } from '../../shared/models/cliente.model';
import { ExecucaoRecente } from '../../shared/models/execucao.model';
import { ResumoGeral } from '../../shared/models/resumo.model';

const MAX_CLIENTES_DESTAQUE = 5;

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [HeroBannerComponent, ClientsOverviewComponent, RecentExecutionsComponent, SummaryPanelComponent],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent implements OnInit {
  protected readonly clientes = signal<Cliente[]>([]);
  protected readonly totalTestesApi = signal(0);
  protected readonly carregando = signal(true);

  // A execução real de testes (via pytest) ainda não existe no backend — etapa futura.
  // A lista fica vazia (dado real) em vez de mostrar execuções fictícias.
  protected readonly execucoes = signal<ExecucaoRecente[]>([]);

  protected readonly clientesDestaque = computed(() => this.clientes().slice(0, MAX_CLIENTES_DESTAQUE));

  protected readonly resumo = computed<ResumoGeral>(() => {
    const totalSucesso = this.execucoes().filter((e) => e.resultado === 'sucesso').length;
    const totalFalhas = this.execucoes().filter((e) => e.resultado === 'falhou').length;
    const totalExecucoes = this.execucoes().length;

    return {
      periodoLabel: 'Últimos 30 dias',
      percentualSucesso: totalExecucoes > 0 ? Math.round((totalSucesso / totalExecucoes) * 100) : 0,
      totalSucesso,
      totalFalhas,
      totalExecucoes,
      totalTestesApi: this.totalTestesApi(),
      totalClientesAtivos: this.clientes().filter((cliente) => cliente.status === 'ativo').length
    };
  });

  constructor(
    private readonly projetoService: ProjetoService,
    private readonly clienteService: ClienteService,
    private readonly router: Router
  ) {}

  ngOnInit(): void {
    forkJoin({
      clientes: this.clienteService.listar(),
      projetos: this.projetoService.listar()
    }).subscribe({
      next: ({ clientes, projetos }) => {
        this.clientes.set(clientes);
        this.totalTestesApi.set(projetos.reduce((soma, projeto) => soma + projeto.total_testes, 0));
        this.carregando.set(false);
      },
      error: () => {
        this.carregando.set(false);
      }
    });
  }

  protected onCadastrarCliente(): void {
    this.router.navigate(['/clientes', 'novo']);
  }
}
