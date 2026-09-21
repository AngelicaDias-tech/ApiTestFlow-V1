import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../config/api.config';
import { MassaImportacao } from '../../shared/models/massa.model';

@Injectable({ providedIn: 'root' })
export class MassaService {
  private readonly baseUrl = `${API_BASE_URL}/testes`;

  constructor(private readonly http: HttpClient) {}

  obterPorTeste(testeId: number): Observable<MassaImportacao | null> {
    return this.http.get<MassaImportacao | null>(`${this.baseUrl}/${testeId}/massa`);
  }

  importar(testeId: number, arquivo: File): Observable<MassaImportacao> {
    const formData = new FormData();
    formData.append('arquivo', arquivo);
    return this.http.post<MassaImportacao>(`${this.baseUrl}/${testeId}/massa`, formData);
  }

  urlModeloOficial(): string {
    return `${this.baseUrl}/massa/modelo`;
  }
}
