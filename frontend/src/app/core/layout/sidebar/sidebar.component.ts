import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { IconComponent, IconName } from '../../../shared/ui/icon/icon.component';

interface NavItem {
  label: string;
  icon: IconName;
  route?: string;
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [IconComponent, RouterLink, RouterLinkActive],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.scss'
})
export class SidebarComponent {
  protected readonly navItems: NavItem[] = [
    { label: 'Início', icon: 'home', route: '/' },
    { label: 'Clientes', icon: 'users', route: '/clientes' },
    { label: 'Configurações', icon: 'settings' }
  ];

  protected readonly usuario = {
    iniciais: 'JS',
    nome: 'João Silva',
    empresa: 'Serasa Experian'
  };
}
