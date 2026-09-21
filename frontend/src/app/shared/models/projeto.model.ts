import { Cliente } from './cliente.model';

export type AmbienteProjeto = 'desenvolvimento' | 'homologacao' | 'producao';
export type StatusProjeto = 'ativo' | 'inativo';

/** Espelha o schema ProjetoRead da API (backend/app/schemas/projeto.py). */
export interface Projeto {
  id: number;
  cliente_id: number;
  cliente: Pick<Cliente, 'id' | 'nome' | 'status'>;
  nome: string;
  descricao: string | null;
  ambiente: AmbienteProjeto;
  status: StatusProjeto;
  total_testes: number;
  created_at: string;
  updated_at: string;
}

export interface ProjetoCreate {
  cliente_id: number;
  nome: string;
  descricao?: string | null;
  ambiente?: AmbienteProjeto;
  status?: StatusProjeto;
}

/** Corpo usado ao criar um projeto a partir da rota de um cliente (cliente_id vem da URL). */
export type ProjetoCreateAninhado = Omit<ProjetoCreate, 'cliente_id'>;

export interface ProjetoUpdate {
  cliente_id?: number;
  nome?: string;
  descricao?: string | null;
  ambiente?: AmbienteProjeto;
  status?: StatusProjeto;
}
