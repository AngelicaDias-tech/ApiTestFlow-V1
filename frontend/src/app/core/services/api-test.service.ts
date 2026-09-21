import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../config/api.config';
import { ApiTest, ApiTestCreate, ApiTestUpdate } from '../../shared/models/api-test.model';

@Injectable({ providedIn: 'root' })
export class ApiTestService {
  private readonly baseUrl = `${API_BASE_URL}/projetos`;

  constructor(private readonly http: HttpClient) {}

  listarPorProjeto(projectId: number): Observable<ApiTest[]> {
    return this.http.get<ApiTest[]>(`${this.baseUrl}/${projectId}/testes`);
  }

  obter(projectId: number, testId: number): Observable<ApiTest> {
    return this.http.get<ApiTest>(`${this.baseUrl}/${projectId}/testes/${testId}`);
  }

  criar(projectId: number, dados: ApiTestCreate): Observable<ApiTest> {
    return this.http.post<ApiTest>(`${this.baseUrl}/${projectId}/testes`, dados);
  }

  atualizar(projectId: number, testId: number, dados: ApiTestUpdate): Observable<ApiTest> {
    return this.http.put<ApiTest>(`${this.baseUrl}/${projectId}/testes/${testId}`, dados);
  }
}
