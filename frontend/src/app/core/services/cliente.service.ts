import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../config/api.config';
import { Cliente, ClienteCreate, ClienteUpdate } from '../../shared/models/cliente.model';

@Injectable({ providedIn: 'root' })
export class ClienteService {
  private readonly baseUrl = `${API_BASE_URL}/clientes`;

  constructor(private readonly http: HttpClient) {}

  listar(): Observable<Cliente[]> {
    return this.http.get<Cliente[]>(this.baseUrl);
  }

  obter(id: number): Observable<Cliente> {
    return this.http.get<Cliente>(`${this.baseUrl}/${id}`);
  }

  criar(dados: ClienteCreate): Observable<Cliente> {
    return this.http.post<Cliente>(this.baseUrl, dados);
  }

  atualizar(id: number, dados: ClienteUpdate): Observable<Cliente> {
    return this.http.put<Cliente>(`${this.baseUrl}/${id}`, dados);
  }

  remover(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }
}
