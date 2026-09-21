export type StatusCliente = 'ativo' | 'inativo';

/** Espelha o schema ClienteRead da API (backend/app/schemas/cliente.py). */
export interface Cliente {
  id: number;
  nome: string;
  status: StatusCliente;
  created_at: string;
  updated_at: string;
}

export interface ClienteCreate {
  nome: string;
  status?: StatusCliente;
}

export type ClienteUpdate = Partial<ClienteCreate>;
