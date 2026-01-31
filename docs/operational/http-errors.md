# HTTP Errors

A Modbus API utiliza **códigos HTTP padronizados** para indicar erros ocorridos **antes**, **durante** ou **após** o processamento de uma requisição. Esses erros permitem que clientes HTTP (Web, Mobile, SCADA, Scripts) identifiquem rapidamente a causa da falha e reajam corretamente.

---

## Visão Geral

Os erros HTTP são utilizados para indicar:

* Falhas de autenticação
* Limites de requisição excedidos
* Erros de validação de parâmetros
* Falhas internas do servidor
* Indisponibilidade de serviços

---

## Estrutura da Resposta de Erro

Todas as respostas de erro seguem o mesmo formato JSON:

```json
{
  "detail": "Descrição do erro"
}
```

---

## Códigos HTTP Utilizados

| Código | Nome | Quando ocorre |
|------|------|---------------|
| `400` | Bad Request | Parâmetros inválidos ou inconsistentes |
| `401` | Unauthorized | API Key ausente ou inválida |
| `403` | Forbidden | Acesso não permitido |
| `404` | Not Found | Endpoint inexistente |
| `422` | Unprocessable Entity | Erro de validação de payload |
| `429` | Too Many Requests | Rate limit excedido |
| `500` | Internal Server Error | Erro inesperado no servidor |
| `503` | Service Unavailable | Serviço Modbus indisponível |

---

## Erros de Autenticação

`401 – Unauthorized`

Ocorre quando:

* O header X-API-Key não é enviado
* A API Key enviada é inválida

Exemplo de resposta:

```json
{
  "detail": "Unauthorized"
}
```

---

## Erros de Rate Limit

`429 – Too Many Requests`

Ocorre quando o cliente excede o número permitido de requisições na janela de tempo configurada.

Exemplo de resposta:

```json
{
  "detail": "Rate limit exceeded"
}
```

---

## Erros de Validação

`400 – Bad Request`

Ocorre quando:

* Parâmetros obrigatórios não são informados
* Valores estão fora do intervalo permitido
* Combinação de parâmetros é inválida

Exemplo:

```json
{
  "detail": "Invalid address or count"
}
```

---

## 
