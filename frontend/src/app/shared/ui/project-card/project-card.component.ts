import { Component, Input } from '@angular/core';
import { RouterLink } from '@angular/router';
import { IconComponent } from '../icon/icon.component';
import { Projeto } from '../../models/projeto.model';

const PALETA_DESTAQUE = ['#6c3fb0', '#1f5fbf', '#1c7fd6', '#cc1f3b', '#0e8f6b', '#b5590c'];

@Component({
  selector: 'app-project-card',
  standalone: true,
  imports: [RouterLink, IconComponent],
  templateUrl: './project-card.component.html',
  styleUrl: './project-card.component.scss'
})
export class ProjectCardComponent {
  @Input({ required: true }) projeto!: Projeto;

  protected get iniciais(): string {
    return this.projeto.nome.trim().charAt(0).toUpperCase() || '?';
  }

  protected get corDestaque(): string {
    return PALETA_DESTAQUE[this.projeto.id % PALETA_DESTAQUE.length];
  }
}
