import { Component, Input } from '@angular/core';
import { ExecucaoRecente } from '../../../../shared/models/execucao.model';
import { IconComponent } from '../../../../shared/ui/icon/icon.component';

@Component({
  selector: 'app-recent-executions',
  standalone: true,
  imports: [IconComponent],
  templateUrl: './recent-executions.component.html',
  styleUrl: './recent-executions.component.scss'
})
export class RecentExecutionsComponent {
  @Input() execucoes: ExecucaoRecente[] = [];
}
