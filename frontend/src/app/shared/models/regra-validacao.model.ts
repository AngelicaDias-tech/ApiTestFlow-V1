export const OPERADORES_VALIDACAO = [
  'EQUALS',
  'NOT_EQUALS',
  'GREATER_THAN',
  'GREATER_THAN_OR_EQUAL',
  'LESS_THAN',
  'LESS_THAN_OR_EQUAL',
  'CONTAINS',
  'NOT_CONTAINS',
  'EXISTS',
  'NOT_EXISTS',
  'IS_NULL',
  'IS_NOT_NULL',
  'COUNT',
  'SEQUENCE',
  'RELATIVE_DATE'
] as const;

export type OperadorValidacao = (typeof OPERADORES_VALIDACAO)[number];

/** Espelha o schema RegraValidacaoRead da API. */
export interface RegraValidacao {
  id: number;
  api_test_id: number;
  ordem: number;
  caso_id: string | null;
  campo: string;
  operador: string;
  valor_esperado: string | null;
  grupo: string | null;
  descricao: string | null;
}

export interface RegraValidacaoPayload {
  caso_id: string | null;
  campo: string;
  operador: string;
  valor_esperado: string | null;
  grupo: string | null;
  descricao: string | null;
}
