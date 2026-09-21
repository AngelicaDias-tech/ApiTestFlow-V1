import { Component, EventEmitter, Output } from '@angular/core';
import { ButtonComponent } from '../../../../shared/ui/button/button.component';
import { IconComponent, IconName } from '../../../../shared/ui/icon/icon.component';

interface Destaque {
  icon: IconName;
  titulo: string;
  descricao: string;
}

@Component({
  selector: 'app-hero-banner',
  standalone: true,
  imports: [ButtonComponent, IconComponent],
  templateUrl: './hero-banner.component.html',
  styleUrl: './hero-banner.component.scss'
})
export class HeroBannerComponent {
  @Output() cadastrarCliente = new EventEmitter<void>();

  protected readonly destaques: Destaque[] = [
    { icon: 'lightning', titulo: 'Automatize', descricao: 'testes de forma simples' },
    { icon: 'shield', titulo: 'Mais segurança', descricao: 'para seus dados' },
    { icon: 'bar-chart', titulo: 'Resultados claros', descricao: 'para decisões mais rápidas' }
  ];
}
