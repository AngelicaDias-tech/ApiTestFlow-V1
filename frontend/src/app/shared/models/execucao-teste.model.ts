export type TipoExecucao = 'demonstracao' | 'real';
export type ResultadoCaso = 'PASS' | 'FAIL';

/** Espelha o schema ResultadoValidacaoRead da API. */
export interface ResultadoValidacao {
  id: number;
  campo: string;
  operador: string;
  valor_esperado: string | null;
  valor_obtido: string | null;
  passou: boolean;
  descricao: string | null;
  detalhe: string | null;
}

/** Espelha o schema ResultadoLinhaRead da API. */
export interface ResultadoLinha {
  id: number;
  execucao_id: number;
  caso_id: string;
  resultado: ResultadoCaso;
  status_http: number | null;
  tempo_ms: number | null;
  request_enviado: string | null;
  response_recebido: string | null;
  motivo_falha: string | null;
  validacoes: ResultadoValidacao[];
}

/** Espelha o schema ExecucaoRead da API. */
export interface ExecucaoTeste {
  id: number;
  api_test_id: number;
  tipo: TipoExecucao;
  executado_em: string;
  total_casos: number;
  total_pass: number;
  total_fail: number;
  resultados: ResultadoLinha[];
}
