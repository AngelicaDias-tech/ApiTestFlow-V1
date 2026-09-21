export type ResultadoExecucao = 'sucesso' | 'falhou';

/**
 * Execução de um teste de API. Ainda não há entidade/endpoint de execução no backend
 * (a execução real via pytest é uma etapa futura) — este tipo já fica pronto para quando
 * existir, mas por enquanto a lista real estará sempre vazia.
 */
export interface ExecucaoRecente {
  id: number;
  testeNome: string;
  clienteNome: string;
  dataHora: string;
  resultado: ResultadoExecucao;
  casos: number;
}
