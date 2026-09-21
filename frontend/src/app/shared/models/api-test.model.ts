export type MetodoHttp = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
export type StatusApiTest = 'ativo' | 'inativo';
export type TipoAutenticacao = 'nenhuma' | 'bearer_token' | 'api_key' | 'basic';

/** Espelha o schema ApiTestRead da API (backend/app/schemas/api_test.py). */
export interface ApiTest {
  id: number;
  project_id: number;

  // Identificação
  nome: string;
  descricao: string | null;

  // Request
  endpoint: string;
  metodo_http: MetodoHttp;
  headers: string | null;
  query_params: string | null;
  path_params: string | null;
  body: string | null;

  // Autenticação. O backend NUNCA devolve auth_token em texto pleno neste
  // schema — `possui_token` só informa se um token está configurado.
  auth_type: TipoAutenticacao;
  possui_token: boolean;

  ambiente: string | null;
  status: StatusApiTest;
  created_at: string;
  updated_at: string;
}

export interface ApiTestCreate {
  nome: string;
  descricao?: string | null;
  endpoint: string;
  metodo_http?: MetodoHttp;
  headers?: string | null;
  query_params?: string | null;
  path_params?: string | null;
  body?: string | null;
  auth_type?: TipoAutenticacao;
  auth_token?: string | null;
  ambiente?: string | null;
  status?: StatusApiTest;
}

export type ApiTestUpdate = Partial<ApiTestCreate>;
