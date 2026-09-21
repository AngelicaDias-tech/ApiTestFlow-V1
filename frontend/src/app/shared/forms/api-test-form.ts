import { FormBuilder, Validators } from '@angular/forms';
import { MetodoHttp, TipoAutenticacao } from '../models/api-test.model';

export function buildApiTestForm(fb: FormBuilder) {
  return fb.group({
    nome: fb.control('', { nonNullable: true, validators: [Validators.required, Validators.maxLength(150)] }),
    descricao: fb.control(''),
    endpoint: fb.control('', {
      nonNullable: true,
      validators: [Validators.required, Validators.maxLength(500)]
    }),
    metodo_http: fb.control<MetodoHttp>('GET', { nonNullable: true }),
    ambiente: fb.control(''),
    headers: fb.control(''),
    query_params: fb.control(''),
    path_params: fb.control(''),
    body: fb.control(''),
    auth_type: fb.control<TipoAutenticacao>('nenhuma', { nonNullable: true }),
    auth_token: fb.control('')
  });
}

export type ApiTestFormGroup = ReturnType<typeof buildApiTestForm>;
