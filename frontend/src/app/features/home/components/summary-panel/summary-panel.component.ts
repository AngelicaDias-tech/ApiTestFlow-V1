import { Component, Input } from '@angular/core';
import { ResumoGeral } from '../../../../shared/models/resumo.model';
import { IconComponent } from '../../../../shared/ui/icon/icon.component';
import { DonutChartComponent, DonutSegment } from '../donut-chart/donut-chart.component';

@Component({
  selector: 'app-summary-panel',
  standalone: true,
  imports: [IconComponent, DonutChartComponent],
  templateUrl: './summary-panel.component.html',
  styleUrl: './summary-panel.component.scss'
})
export class SummaryPanelComponent {
  @Input({ required: true }) resumo!: ResumoGeral;

  protected get segments(): DonutSegment[] {
    if (this.resumo.totalExecucoes === 0) {
      return [{ percent: 100, colorVar: 'var(--border)' }];
    }
    return [
      { percent: this.resumo.percentualSucesso, colorVar: 'var(--success)' },
      { percent: 100 - this.resumo.percentualSucesso, colorVar: 'var(--danger)' }
    ];
  }
}
