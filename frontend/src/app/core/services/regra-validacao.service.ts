import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../config/api.config';
import { RegraValidacao, RegraValidacaoPayload } from '../../shared/models/regra-validacao.model';

@Injectable({ providedIn: 'root' })
export class RegraValidacaoService {
  private readonly baseUrl = `${API_BASE_URL}/testes`;

  constructor(private readonly http: HttpClient) {}

  listarPorTeste(testeId: number): Observable<RegraValidacao[]> {
    return this.http.get<RegraValidacao[]>(`${this.baseUrl}/${testeId}/regras`);
  }

  criar(testeId: number, dados: RegraValidacaoPayload): Observable<RegraValidacao> {
    return this.http.post<RegraValidacao>(`${this.baseUrl}/${testeId}/regras`, dados);
  }

  atualizar(testeId: number, regraId: number, dados: RegraValidacaoPayload): Observable<RegraValidacao> {
    return this.http.put<RegraValidacao>(`${this.baseUrl}/${testeId}/regras/${regraId}`, dados);
  }

  excluir(testeId: number, regraId: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${testeId}/regras/${regraId}`);
  }
}
