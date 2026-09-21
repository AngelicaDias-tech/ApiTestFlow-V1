import { Component, EventEmitter, HostBinding, Input, Output } from '@angular/core';

export type ButtonVariant = 'primary' | 'outline';

@Component({
  selector: 'app-button',
  standalone: true,
  templateUrl: './button.component.html',
  styleUrl: './button.component.scss'
})
export class ButtonComponent {
  @Input() variant: ButtonVariant = 'primary';
  @Input() type: 'button' | 'submit' = 'button';
  @Input() disabled = false;
  @Output() buttonClick = new EventEmitter<void>();

  @HostBinding('class') get hostClass(): string {
    return `variant-${this.variant}`;
  }
}
