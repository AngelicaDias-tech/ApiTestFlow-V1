import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ButtonComponent } from '../../shared/ui/button/button.component';
import { IconComponent } from '../../shared/ui/icon/icon.component';
import { ApiTestFormFieldsComponent } from '../../shared/ui/api-test-form-fields/api-test-form-fields.component';
import { buildApiTestForm } from '../../shared/forms/api-test-form';
import { ProjetoService } from '../../core/services/projeto.service';
import { ApiTestService } from '../../core/services/api-test.service';
import { Projeto } from '../../shared/models/projeto.model';

@Component({
  selector: 'app-novo-teste',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink, ButtonComponent, IconComponent, ApiTestFormFieldsComponent],
  templateUrl: './novo-teste.component.html',
  styleUrl: './novo-teste.component.scss'
})
export class NovoTesteComponent implements OnInit {
  protected readonly projeto = signal<Projeto | null>(null);
  protected readonly carregando = signal(true);
  protected readonly salvando = signal(false);
  protected readonly erro = signal<string | null>(null);

  private readonly fb = inject(FormBuilder);
  protected readonly form = buildApiTestForm(this.fb);

  private projetoId!: number;
  protected clienteId!: number;

  constructor(
    private readonly route: ActivatedRoute,
    private readonly router: Router,
    private readonly projetoService: ProjetoService,
    private readonly apiTestService: ApiTestService
  ) {}

  ngOnInit(): void {
    this.clienteId = Number(this.route.snapshot.paramMap.get('clientId'));
    this.projetoId = Number(this.route.snapshot.paramMap.get('projectId'));
    this.carregando.set(true);
    this.projetoService.obter(this.projetoId).subscribe({
      next: (projeto) => {
        this.projeto.set(projeto);
        this.form.patchValue({ ambiente: projeto.ambiente });
        this.carregando.set(false);
      },
      error: () => {
        this.erro.set('Projeto não encontrado.');
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

    this.apiTestService
      .criar(this.projetoId, {
        nome: valor.nome,
        descricao: valor.descricao || null,
        endpoint: valor.endpoint,
        metodo_http: valor.metodo_http,
        ambiente: valor.ambiente || null,
        headers: valor.headers || null,
        query_params: valor.query_params || null,
        path_params: valor.path_params || null,
        body: valor.body || null,
        auth_type: valor.auth_type,
        auth_token: valor.auth_token || null
      })
      .subscribe({
        next: (teste) => {
          this.router.navigate(['/clientes', this.clienteId, 'projetos', this.projetoId, 'testes', teste.id]);
        },
        error: () => {
          this.erro.set('Não foi possível salvar o teste. Tente novamente.');
          this.salvando.set(false);
        }
      });
  }
}
