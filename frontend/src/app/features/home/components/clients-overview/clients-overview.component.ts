import { Component, Input } from '@angular/core';
import { RouterLink } from '@angular/router';
import { IconComponent } from '../../../../shared/ui/icon/icon.component';
import { ClientCardComponent } from '../../../../shared/ui/client-card/client-card.component';
import { Cliente } from '../../../../shared/models/cliente.model';

@Component({
  selector: 'app-clients-overview',
  standalone: true,
  imports: [RouterLink, IconComponent, ClientCardComponent],
  templateUrl: './clients-overview.component.html',
  styleUrl: './clients-overview.component.scss'
})
export class ClientsOverviewComponent {
  @Input({ required: true }) clientes: Cliente[] = [];
  @Input() carregando = false;
}
