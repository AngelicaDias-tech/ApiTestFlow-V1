import { Component, Input } from '@angular/core';
import { RouterLink } from '@angular/router';
import { IconComponent } from '../icon/icon.component';
import { Cliente } from '../../models/cliente.model';

const PALETA_DESTAQUE = ['#6c3fb0', '#1f5fbf', '#1c7fd6', '#cc1f3b', '#0e8f6b', '#b5590c'];

@Component({
  selector: 'app-client-card',
  standalone: true,
  imports: [RouterLink, IconComponent],
  templateUrl: './client-card.component.html',
  styleUrl: './client-card.component.scss'
})
export class ClientCardComponent {
  @Input({ required: true }) cliente!: Cliente;

  protected get iniciais(): string {
    return this.cliente.nome.trim().charAt(0).toUpperCase() || '?';
  }

  protected get corDestaque(): string {
    return PALETA_DESTAQUE[this.cliente.id % PALETA_DESTAQUE.length];
  }
}
