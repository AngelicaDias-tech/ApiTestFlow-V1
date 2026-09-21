import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../config/api.config';
import { Projeto, ProjetoCreate, ProjetoCreateAninhado, ProjetoUpdate } from '../../shared/models/projeto.model';

@Injectable({ providedIn: 'root' })
export class ProjetoService {
  private readonly baseUrl = `${API_BASE_URL}/projetos`;
  private readonly clientesUrl = `${API_BASE_URL}/clientes`;

  constructor(private readonly http: HttpClient) {}

  listar(): Observable<Projeto[]> {
    return this.http.get<Projeto[]>(this.baseUrl);
  }

  listarPorCliente(clienteId: number): Observable<Projeto[]> {
    return this.http.get<Projeto[]>(`${this.clientesUrl}/${clienteId}/projetos`);
  }

  obter(id: number): Observable<Projeto> {
    return this.http.get<Projeto>(`${this.baseUrl}/${id}`);
  }

  criar(dados: ProjetoCreate): Observable<Projeto> {
    return this.http.post<Projeto>(this.baseUrl, dados);
  }

  criarParaCliente(clienteId: number, dados: ProjetoCreateAninhado): Observable<Projeto> {
    return this.http.post<Projeto>(`${this.clientesUrl}/${clienteId}/projetos`, dados);
  }

  atualizar(id: number, dados: ProjetoUpdate): Observable<Projeto> {
    return this.http.put<Projeto>(`${this.baseUrl}/${id}`, dados);
  }

  remover(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }
}
