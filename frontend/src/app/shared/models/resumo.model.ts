/** Resumo agregado a partir de dados reais (projetos, clientes e — futuramente — execuções). */
export interface ResumoGeral {
  periodoLabel: string;
  percentualSucesso: number;
  totalSucesso: number;
  totalFalhas: number;
  totalExecucoes: number;
  totalTestesApi: number;
  totalClientesAtivos: number;
}
