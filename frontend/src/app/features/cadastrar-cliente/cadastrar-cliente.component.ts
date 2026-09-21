import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ButtonComponent } from '../../shared/ui/button/button.component';
import { ClienteService } from '../../core/services/cliente.service';

@Component({
  selector: 'app-cadastrar-cliente',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink, ButtonComponent],
  templateUrl: './cadastrar-cliente.component.html',
  styleUrl: './cadastrar-cliente.component.scss'
})
export class CadastrarClienteComponent {
  protected readonly salvando = signal(false);
  protected readonly erro = signal<string | null>(null);

  private readonly fb = inject(FormBuilder);

  protected readonly form = this.fb.group({
    nome: this.fb.control('', { nonNullable: true, validators: [Validators.required, Validators.maxLength(150)] }),
    status: this.fb.control<'ativo' | 'inativo'>('ativo', { nonNullable: true })
  });

  constructor(
    private readonly clienteService: ClienteService,
    private readonly router: Router
  ) {}

  protected salvar(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.salvando.set(true);
    this.erro.set(null);

    this.clienteService.criar(this.form.getRawValue()).subscribe({
      next: (cliente) => {
        this.router.navigate(['/clientes', cliente.id]);
      },
      error: () => {
        this.erro.set('Não foi possível salvar o cliente. Tente novamente.');
        this.salvando.set(false);
      }
    });
  }
}
