import { Component, Input } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';
import { IconComponent } from '../icon/icon.component';
import { ApiTestFormGroup } from '../../forms/api-test-form';

@Component({
  selector: 'app-api-test-form-fields',
  standalone: true,
  imports: [ReactiveFormsModule, IconComponent],
  templateUrl: './api-test-form-fields.component.html',
  styleUrl: './api-test-form-fields.component.scss'
})
export class ApiTestFormFieldsComponent {
  @Input({ required: true }) form!: ApiTestFormGroup;
  /** Quando true, indica que já existe um token salvo (nunca exibido) — o campo
   * fica em branco e só é enviado ao backend se o usuário digitar um novo valor. */
  @Input() possuiTokenConfigurado = false;
}
