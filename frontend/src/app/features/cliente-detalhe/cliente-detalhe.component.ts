import { Component, OnInit, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ButtonComponent } from '../../shared/ui/button/button.component';
import { IconComponent } from '../../shared/ui/icon/icon.component';
import { ProjectCardComponent } from '../../shared/ui/project-card/project-card.component';
import { ClienteService } from '../../core/services/cliente.service';
import { ProjetoService } from '../../core/services/projeto.service';
import { Cliente } from '../../shared/models/cliente.model';
import { Projeto } from '../../shared/models/projeto.model';

@Component({
  selector: 'app-cliente-detalhe',
  standalone: true,
  imports: [RouterLink, FormsModule, ButtonComponent, IconComponent, ProjectCardComponent],
  templateUrl: './cliente-detalhe.component.html',
  styleUrl: './cliente-detalhe.component.scss'
})
export class ClienteDetalheComponent implements OnInit {
  protected readonly cliente = signal<Cliente | null>(null);
  protected readonly projetos = signal<Projeto[]>([]);
  protected readonly carregando = signal(true);
  protected readonly erro = signal<string | null>(null);
  protected readonly termoBusca = signal('');

  private clienteId!: number;

  constructor(
    private readonly route: ActivatedRoute,
    private readonly clienteService: ClienteService,
    private readonly projetoService: ProjetoService
  ) {}

  ngOnInit(): void {
    this.clienteId = Number(this.route.snapshot.paramMap.get('clientId'));
    this.carregar();
  }

  protected get projetosFiltrados(): Projeto[] {
    const termo = this.termoBusca().trim().toLowerCase();
    if (!termo) {
      return this.projetos();
    }
    return this.projetos().filter((projeto) => projeto.nome.toLowerCase().includes(termo));
  }

  private carregar(): void {
    this.carregando.set(true);
    this.erro.set(null);

    this.clienteService.obter(this.clienteId).subscribe({
      next: (cliente) => {
        this.cliente.set(cliente);
        this.projetoService.listarPorCliente(this.clienteId).subscribe({
          next: (projetos) => {
            this.projetos.set(projetos);
            this.carregando.set(false);
          },
          error: () => {
            this.erro.set('Não foi possível carregar os projetos deste cliente.');
            this.carregando.set(false);
          }
        });
      },
      error: () => {
        this.erro.set('Cliente não encontrado.');
        this.carregando.set(false);
      }
    });
  }
}
