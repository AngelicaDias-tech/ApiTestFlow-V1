/** Espelha o schema MassaLinhaRead da API (linha da aba "Atualizacoes" do modelo oficial). */
export interface MassaLinha {
  id: number;
  caso_id: string;
  path: string;
  acao: string;
  tipo: string | null;
  novo_valor: string | null;
  ativo: boolean;
  observacao: string | null;
}

/** Espelha o schema MassaImportacaoRead da API. */
export interface MassaImportacao {
  id: number;
  api_test_id: number;
  nome_arquivo: string;
  total_casos: number;
  total_linhas: number;
  importado_em: string;
  linhas: MassaLinha[];
}
