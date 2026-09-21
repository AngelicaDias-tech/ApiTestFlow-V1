import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ButtonComponent } from '../../shared/ui/button/button.component';
import { ClienteService } from '../../core/services/cliente.service';
import { ProjetoService } from '../../core/services/projeto.service';
import { Cliente } from '../../shared/models/cliente.model';

@Component({
  selector: 'app-cadastrar-projeto',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink, ButtonComponent],
  templateUrl: './cadastrar-projeto.component.html',
  styleUrl: './cadastrar-projeto.component.scss'
})
export class CadastrarProjetoComponent implements OnInit {
  protected readonly cliente = signal<Cliente | null>(null);
  protected readonly carregando = signal(true);
  protected readonly salvando = signal(false);
  protected readonly erro = signal<string | null>(null);

  private readonly fb = inject(FormBuilder);
  private clienteId!: number;

  protected readonly form = this.fb.group({
    nome: this.fb.control('', { nonNullable: true, validators: [Validators.required, Validators.maxLength(150)] }),
    descricao: this.fb.control(''),
    ambiente: this.fb.control<'desenvolvimento' | 'homologacao' | 'producao'>('homologacao', {
      nonNullable: true
    }),
    status: this.fb.control<'ativo' | 'inativo'>('ativo', { nonNullable: true })
  });

  constructor(
    private readonly route: ActivatedRoute,
    private readonly clienteService: ClienteService,
    private readonly projetoService: ProjetoService,
    private readonly router: Router
  ) {}

  ngOnInit(): void {
    this.clienteId = Number(this.route.snapshot.paramMap.get('clientId'));
    this.carregando.set(true);
    this.clienteService.obter(this.clienteId).subscribe({
      next: (cliente) => {
        this.cliente.set(cliente);
        this.carregando.set(false);
      },
      error: () => {
        this.erro.set('Cliente não encontrado.');
        this.carregando.set(false);
      }
    });
  }

  protected salvar(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const valor = this.form.getRawValue();
    this.salvando.set(true);
    this.erro.set(null);

    this.projetoService
      .criarParaCliente(this.clienteId, {
        nome: valor.nome,
        descricao: valor.descricao || null,
        ambiente: valor.ambiente,
        status: valor.status
      })
      .subscribe({
        next: (projeto) => {
          this.router.navigate(['/clientes', this.clienteId, 'projetos', projeto.id]);
        },
        error: () => {
          this.erro.set('Não foi possível salvar o projeto. Tente novamente.');
          this.salvando.set(false);
        }
      });
  }
}
