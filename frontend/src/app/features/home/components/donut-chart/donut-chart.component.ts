import { Component, Input } from '@angular/core';

export interface DonutSegment {
  percent: number;
  colorVar: string;
}

@Component({
  selector: 'app-donut-chart',
  standalone: true,
  templateUrl: './donut-chart.component.html',
  styleUrl: './donut-chart.component.scss'
})
export class DonutChartComponent {
  @Input() segments: DonutSegment[] = [];
  @Input() size = 140;
  @Input() strokeWidth = 16;

  protected get radius(): number {
    return (this.size - this.strokeWidth) / 2;
  }

  protected get center(): number {
    return this.size / 2;
  }

  protected get circumference(): number {
    return 2 * Math.PI * this.radius;
  }

  protected dashArrayFor(segment: DonutSegment): string {
    const comprimento = (segment.percent / 100) * this.circumference;
    return `${comprimento} ${this.circumference - comprimento}`;
  }

  protected offsetFor(index: number): number {
    const anterior = this.segments.slice(0, index).reduce((soma, s) => soma + s.percent, 0);
    return -((anterior / 100) * this.circumference);
  }
}
