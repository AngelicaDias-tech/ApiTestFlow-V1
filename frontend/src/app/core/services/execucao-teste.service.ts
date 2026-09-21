import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../config/api.config';
import { ExecucaoTeste } from '../../shared/models/execucao-teste.model';

@Injectable({ providedIn: 'root' })
export class ExecucaoTesteService {
  private readonly baseUrl = `${API_BASE_URL}/testes`;

  constructor(private readonly http: HttpClient) {}

  listarPorTeste(testeId: number): Observable<ExecucaoTeste[]> {
    return this.http.get<ExecucaoTeste[]>(`${this.baseUrl}/${testeId}/execucoes`);
  }

  obter(testeId: number, execucaoId: number): Observable<ExecucaoTeste> {
    return this.http.get<ExecucaoTeste>(`${this.baseUrl}/${testeId}/execucoes/${execucaoId}`);
  }

  executar(testeId: number): Observable<ExecucaoTeste> {
    return this.http.post<ExecucaoTeste>(`${this.baseUrl}/${testeId}/executar`, {});
  }
}
