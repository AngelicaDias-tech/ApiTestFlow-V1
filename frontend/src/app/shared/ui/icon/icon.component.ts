import { Component, Input } from '@angular/core';

export type IconName =
  | 'home'
  | 'users'
  | 'settings'
  | 'logout'
  | 'search'
  | 'bell'
  | 'plus'
  | 'lightning'
  | 'shield'
  | 'bar-chart'
  | 'chevron-right'
  | 'chevron-left'
  | 'chevron-down'
  | 'clock'
  | 'cube'
  | 'check'
  | 'check-circle'
  | 'x'
  | 'x-circle'
  | 'file'
  | 'upload-cloud'
  | 'download'
  | 'play'
  | 'more-vertical'
  | 'trending-up';

@Component({
  selector: 'app-icon',
  standalone: true,
  templateUrl: './icon.component.html',
  styleUrl: './icon.component.scss'
})
export class IconComponent {
  @Input({ required: true }) name!: IconName;
  @Input() size = 20;

  protected readonly gearAngles = [0, 45, 90, 135, 180, 225, 270, 315];
}
