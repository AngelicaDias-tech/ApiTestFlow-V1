import { Component } from '@angular/core';
import { IconComponent } from '../../../shared/ui/icon/icon.component';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [IconComponent],
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss'
})
export class HeaderComponent {
  protected readonly notificacoesNaoLidas = 3;
}
