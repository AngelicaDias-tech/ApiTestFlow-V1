import { Component, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ButtonComponent } from '../../shared/ui/button/button.component';
import { IconComponent } from '../../shared/ui/icon/icon.component';
import { ClientCardComponent } from '../../shared/ui/client-card/client-card.component';
import { ClienteService } from '../../core/services/cliente.service';
import { Cliente } from '../../shared/models/cliente.model';

@Component({
  selector: 'app-clientes',
  standalone: true,
  imports: [RouterLink, FormsModule, ButtonComponent, IconComponent, ClientCardComponent],
  templateUrl: './clientes.component.html',
  styleUrl: './clientes.component.scss'
})
export class ClientesComponent implements OnInit {
  protected readonly clientes = signal<Cliente[]>([]);
  protected readonly carregando = signal(true);
  protected readonly erro = signal<string | null>(null);
  protected readonly termoBusca = signal('');

  constructor(private readonly clienteService: ClienteService) {}

  ngOnInit(): void {
    this.carregando.set(true);
    this.erro.set(null);
    this.clienteService.listar().subscribe({
      next: (clientes) => {
        this.clientes.set(clientes);
        this.carregando.set(false);
      },
      error: () => {
        this.erro.set('Não foi possível carregar os clientes. Verifique se o backend está em execução.');
        this.carregando.set(false);
      }
    });
  }

  protected get clientesFiltrados(): Cliente[] {
    const termo = this.termoBusca().trim().toLowerCase();
    if (!termo) {
      return this.clientes();
    }
    return this.clientes().filter((cliente) => cliente.nome.toLowerCase().includes(termo));
  }
}
