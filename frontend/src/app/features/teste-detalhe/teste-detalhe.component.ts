import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ButtonComponent } from '../../shared/ui/button/button.component';
import { IconComponent } from '../../shared/ui/icon/icon.component';
import { ApiTestFormFieldsComponent } from '../../shared/ui/api-test-form-fields/api-test-form-fields.component';
import { buildApiTestForm } from '../../shared/forms/api-test-form';
import { ProjetoService } from '../../core/services/projeto.service';
import { ApiTestService } from '../../core/services/api-test.service';
import { MassaService } from '../../core/services/massa.service';
import { ExecucaoTesteService } from '../../core/services/execucao-teste.service';
import { RegraValidacaoService } from '../../core/services/regra-validacao.service';
import { Projeto } from '../../shared/models/projeto.model';
import { ApiTest } from '../../shared/models/api-test.model';
import { MassaImportacao, MassaLinha } from '../../shared/models/massa.model';
import { ExecucaoTeste } from '../../shared/models/execucao-teste.model';
import { OPERADORES_VALIDACAO, RegraValidacao } from '../../shared/models/regra-validacao.model';

interface RegrasAgrupadas {
  casoId: string | null;
  rotulo: string;
  regras: RegraValidacao[];
}

interface CasoAgrupado {
  casoId: string;
  linhas: MassaLinha[];
}

@Component({
  selector: 'app-teste-detalhe',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink, ButtonComponent, IconComponent, ApiTestFormFieldsComponent],
  templateUrl: './teste-detalhe.component.html',
  styleUrl: './teste-detalhe.component.scss'
})
export class TesteDetalheComponent implements OnInit {
  protected readonly projeto = signal<Projeto | null>(null);
  protected readonly teste = signal<ApiTest | null>(null);
  protected readonly carregando = signal(true);
  protected readonly salvando = signal(false);
  protected readonly salvoComSucesso = signal(false);
  protected readonly erro = signal<string | null>(null);
  protected readonly configExpandida = signal(false);

  protected readonly massa = signal<MassaImportacao | null>(null);
  protected readonly importandoMassa = signal(false);
  protected readonly erroMassa = signal<string | null>(null);
  protected readonly casoExpandidoId = signal<string | null>(null);
  protected readonly arrastandoMassa = signal(false);

  protected readonly execucoes = signal<ExecucaoTeste[]>([]);
  protected readonly execucaoExpandidaId = signal<number | null>(null);
  protected readonly linhaExpandidaId = signal<number | null>(null);
  protected readonly executando = signal(false);
  protected readonly erroExecucao = signal<string | null>(null);

  protected readonly regras = signal<RegraValidacao[]>([]);
  protected readonly salvandoRegra = signal(false);
  protected readonly erroRegra = signal<string | null>(null);
  protected readonly operadoresValidacao = OPERADORES_VALIDACAO;

  protected readonly regrasAgrupadas = computed<RegrasAgrupadas[]>(() => {
    const porCaso = new Map<string | null, RegraValidacao[]>();
    for (const regra of this.regras()) {
      const lista = porCaso.get(regra.caso_id) ?? [];
      lista.push(regra);
      porCaso.set(regra.caso_id, lista);
    }
    return Array.from(porCaso.entries()).map(([casoId, regras]) => ({
      casoId,
      rotulo: casoId ?? 'Todos os casos',
      regras
    }));
  });

  protected readonly casosAgrupados = computed<CasoAgrupado[]>(() => {
    const massa = this.massa();
    if (!massa) {
      return [];
    }
    const porCaso = new Map<string, MassaLinha[]>();
    for (const linha of massa.linhas) {
      const lista = porCaso.get(linha.caso_id) ?? [];
      lista.push(linha);
      porCaso.set(linha.caso_id, lista);
    }
    return Array.from(porCaso.entries()).map(([casoId, linhas]) => ({ casoId, linhas }));
  });

  private readonly fb = inject(FormBuilder);
  protected readonly form = buildApiTestForm(this.fb);
  protected readonly formRegra = this.fb.nonNullable.group({
    caso_id: [''],
    campo: ['', Validators.required],
    operador: ['EQUALS', Validators.required],
    valor_esperado: [''],
    descricao: ['']
  });

  protected clienteId!: number;
  private projetoId!: number;
  private testeId!: number;

  constructor(
    private readonly route: ActivatedRoute,
    private readonly projetoService: ProjetoService,
    private readonly apiTestService: ApiTestService,
    private readonly massaService: MassaService,
    private readonly execucaoTesteService: ExecucaoTesteService,
    private readonly regraValidacaoService: RegraValidacaoService
  ) {}

  ngOnInit(): void {
    this.clienteId = Number(this.route.snapshot.paramMap.get('clientId'));
    this.projetoId = Number(this.route.snapshot.paramMap.get('projectId'));
    this.testeId = Number(this.route.snapshot.paramMap.get('testId'));
    this.carregar();
  }

  protected get urlModeloMassa(): string {
    return this.massaService.urlModeloOficial();
  }

  protected salvar(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const valor = this.form.getRawValue();
    this.salvando.set(true);
    this.erro.set(null);
    this.salvoComSucesso.set(false);

    this.apiTestService
      .atualizar(this.projetoId, this.testeId, {
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
        // Campo em branco = manter o token atual (nunca é reenviado pelo backend
        // para prefilar o formulário); só inclui a chave quando o usuário digita
        // um valor novo, para não sobrescrever o token existente com vazio.
        ...(valor.auth_token ? { auth_token: valor.auth_token } : {})
      })
      .subscribe({
        next: (teste) => {
          this.teste.set(teste);
          this.salvando.set(false);
          this.salvoComSucesso.set(true);
        },
        error: () => {
          this.erro.set('Não foi possível salvar as alterações. Tente novamente.');
          this.salvando.set(false);
        }
      });
  }

  protected onArquivoSelecionado(evento: Event): void {
    const input = evento.target as HTMLInputElement;
    const arquivo = input.files?.[0];
    if (arquivo) {
      this.importarArquivo(arquivo);
    }
    input.value = '';
  }

  protected onDragOverMassa(evento: DragEvent): void {
    evento.preventDefault();
    this.arrastandoMassa.set(true);
  }

  protected onDragLeaveMassa(): void {
    this.arrastandoMassa.set(false);
  }

  protected onDropMassa(evento: DragEvent): void {
    evento.preventDefault();
    this.arrastandoMassa.set(false);
    const arquivo = evento.dataTransfer?.files?.[0];
    if (arquivo) {
      this.importarArquivo(arquivo);
    }
  }

  private importarArquivo(arquivo: File): void {
    this.importandoMassa.set(true);
    this.erroMassa.set(null);

    this.massaService.importar(this.testeId, arquivo).subscribe({
      next: (massa) => {
        this.massa.set(massa);
        this.importandoMassa.set(false);
      },
      error: (resposta) => {
        this.erroMassa.set(resposta?.error?.detail || 'Não foi possível importar a massa. Verifique o arquivo.');
        this.importandoMassa.set(false);
      }
    });
  }

  protected linhasDoCaso(casoId: string): MassaLinha[] {
    return this.massa()?.linhas.filter((linha) => linha.caso_id === casoId) ?? [];
  }

  protected descricaoDoCaso(casoId: string): string {
    const observacao = this.linhasDoCaso(casoId).find((linha) => linha.observacao)?.observacao;
    if (!observacao) {
      return '—';
    }
    // A planilha oficial usa o padrão "Categoria | Descrição curta | Resultado esperado: ...".
    const partes = observacao.split('|').map((parte) => parte.trim());
    return partes.length >= 2 ? partes[1] : observacao;
  }

  protected alternarCaso(casoId: string): void {
    this.casoExpandidoId.update((atual) => (atual === casoId ? null : casoId));
  }

  protected alternarExecucao(execucaoId: number): void {
    this.execucaoExpandidaId.update((atual) => (atual === execucaoId ? null : execucaoId));
    this.linhaExpandidaId.set(null);
  }

  protected alternarLinha(linhaId: number): void {
    this.linhaExpandidaId.update((atual) => (atual === linhaId ? null : linhaId));
  }

  protected executarTeste(): void {
    this.executando.set(true);
    this.erroExecucao.set(null);

    this.execucaoTesteService.executar(this.testeId).subscribe({
      next: (execucao) => {
        this.execucoes.update((atual) => [execucao, ...atual]);
        this.execucaoExpandidaId.set(execucao.id);
        this.executando.set(false);
      },
      error: () => {
        this.erroExecucao.set('Não foi possível executar o teste agora. Tente novamente.');
        this.executando.set(false);
      }
    });
  }

  protected adicionarRegra(): void {
    if (this.formRegra.invalid) {
      this.formRegra.markAllAsTouched();
      return;
    }

    const valor = this.formRegra.getRawValue();
    this.salvandoRegra.set(true);
    this.erroRegra.set(null);

    this.regraValidacaoService
      .criar(this.testeId, {
        caso_id: valor.caso_id || null,
        campo: valor.campo,
        operador: valor.operador,
        valor_esperado: valor.valor_esperado || null,
        grupo: null,
        descricao: valor.descricao || null
      })
      .subscribe({
        next: (regra) => {
          this.regras.update((atual) => [...atual, regra]);
          this.formRegra.reset({ caso_id: '', campo: '', operador: 'EQUALS', valor_esperado: '', descricao: '' });
          this.salvandoRegra.set(false);
        },
        error: (resposta) => {
          this.erroRegra.set(resposta?.error?.detail || 'Não foi possível salvar a regra. Tente novamente.');
          this.salvandoRegra.set(false);
        }
      });
  }

  protected excluirRegra(regraId: number): void {
    this.regraValidacaoService.excluir(this.testeId, regraId).subscribe({
      next: () => this.regras.update((atual) => atual.filter((r) => r.id !== regraId)),
      error: () => this.erroRegra.set('Não foi possível excluir a regra. Tente novamente.')
    });
  }

  protected formatarData(iso: string): string {
    return new Date(iso).toLocaleString('pt-BR');
  }

  private carregar(): void {
    this.carregando.set(true);
    this.projetoService.obter(this.projetoId).subscribe({
      next: (projeto) => {
        this.projeto.set(projeto);
        this.apiTestService.obter(this.projetoId, this.testeId).subscribe({
          next: (teste) => {
            this.teste.set(teste);
            this.form.patchValue({
              nome: teste.nome,
              descricao: teste.descricao ?? '',
              endpoint: teste.endpoint,
              metodo_http: teste.metodo_http,
              ambiente: teste.ambiente ?? '',
              headers: teste.headers ?? '',
              query_params: teste.query_params ?? '',
              path_params: teste.path_params ?? '',
              body: teste.body ?? '',
              auth_type: teste.auth_type
              // auth_token nunca vem do backend — o campo fica em branco de propósito.
            });
            this.carregarMassaEExecucoes();
          },
          error: () => {
            this.erro.set('Teste não encontrado neste projeto.');
            this.carregando.set(false);
          }
        });
      },
      error: () => {
        this.erro.set('Projeto não encontrado.');
        this.carregando.set(false);
      }
    });
  }

  private carregarMassaEExecucoes(): void {
    this.massaService.obterPorTeste(this.testeId).subscribe({
      next: (massa) => this.massa.set(massa),
      error: () => this.massa.set(null)
    });

    this.regraValidacaoService.listarPorTeste(this.testeId).subscribe({
      next: (regras) => this.regras.set(regras),
      error: () => this.regras.set([])
    });

    this.execucaoTesteService.listarPorTeste(this.testeId).subscribe({
      next: (execucoes) => {
        this.execucoes.set(execucoes);
        this.carregando.set(false);
      },
      error: () => {
        this.carregando.set(false);
      }
    });
  }
}
