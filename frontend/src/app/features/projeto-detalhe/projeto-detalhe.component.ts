import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ButtonComponent } from '../../shared/ui/button/button.component';
import { IconComponent } from '../../shared/ui/icon/icon.component';
import { ProjetoService } from '../../core/services/projeto.service';
import { ApiTestService } from '../../core/services/api-test.service';
import { Projeto } from '../../shared/models/projeto.model';
import { ApiTest } from '../../shared/models/api-test.model';

@Component({
  selector: 'app-projeto-detalhe',
  standalone: true,
  imports: [RouterLink, FormsModule, ButtonComponent, IconComponent],
  templateUrl: './projeto-detalhe.component.html',
  styleUrl: './projeto-detalhe.component.scss'
})
export class ProjetoDetalheComponent implements OnInit {
  protected readonly projeto = signal<Projeto | null>(null);
  protected readonly testes = signal<ApiTest[]>([]);
  protected readonly carregando = signal(true);
  protected readonly erro = signal<string | null>(null);
  protected readonly termoBusca = signal('');

  private projetoId!: number;

  constructor(
    private readonly route: ActivatedRoute,
    private readonly projetoService: ProjetoService,
    private readonly apiTestService: ApiTestService
  ) {}

  ngOnInit(): void {
    this.projetoId = Number(this.route.snapshot.paramMap.get('projectId'));
    this.carregar();
  }

  protected get testesFiltrados(): ApiTest[] {
    const termo = this.termoBusca().trim().toLowerCase();
    if (!termo) {
      return this.testes();
    }
    return this.testes().filter(
      (teste) =>
        teste.nome.toLowerCase().includes(termo) ||
        (teste.descricao ?? '').toLowerCase().includes(termo) ||
        teste.endpoint.toLowerCase().includes(termo)
    );
  }

  private carregar(): void {
    this.carregando.set(true);
    this.erro.set(null);

    this.projetoService.obter(this.projetoId).subscribe({
      next: (projeto) => {
        this.projeto.set(projeto);
        this.apiTestService.listarPorProjeto(this.projetoId).subscribe({
          next: (testes) => {
            this.testes.set(testes);
            this.carregando.set(false);
          },
          error: () => {
            this.erro.set('Não foi possível carregar os testes deste projeto.');
            this.carregando.set(false);
          }
        });
      },
      error: () => {
        this.erro.set('Projeto não encontrado.');
        this.carregando.set(false);
      }
    });
  }
}
