# Modbus Connection (Operational)

Este documento descreve os **endpoints operacionais** relacionados ao **gerenciamento da conexão Modbus TCP** mantida pela API.

Esses endpoints **não realizam leitura nem escrita de dados de processo**.  
Eles existem para **operação, manutenção e recuperação controlada** do estado interno da conexão Modbus.

---

## Visão Geral

| Endpoint | Método | Função |
|--------|--------|-------|
| `/modbus/close` | POST | Fecha explicitamente a conexão Modbus |
| `/modbus/reconnect` | POST | Fecha e força nova conexão Modbus |

---

## Segurança

!!! warning "Autenticação obrigatória"
    Todos os endpoints deste documento exigem o header `X-API-Key`.

```http
X-API-Key: SUA_API_KEY
```

---

## POST /modbus/close

Fecha explicitamente a conexão Modbus TCP ativa mantida pela API.

### Quando usar

- Manutenção programada
- Reset de estado interno do client Modbus
- Liberação explícita de recursos
- Diagnóstico de falhas de comunicação

### Quando **não** usar

- Em polling automático
- Em ciclos normais de leitura/escrita
- Como alternativa a retry automático

---

### Requisição

```
POST /modbus/close
```

#### Headers

| Header | Obrigatório |
|------|------------|
| `X-API-Key` | ✅ |

---

### Resposta de Sucesso

```json
{
  "ok": true
}
```

---

### Comportamento

- Fecha a conexão Modbus ativa (se existir)
- Operação idempotente
- Não remove o client da memória
- Não abre nova conexão automaticamente

---

### Erros Possíveis

| Código HTTP | Motivo |
|-----------|-------|
| 401 | API Key ausente ou inválida |
| 429 | Rate limit excedido |
| 500 | Falha ao fechar conexão |

---

### Exemplo

#### cURL

```bash
curl -X POST "http://127.0.0.1:8000/modbus/close" \
  -H "X-API-Key: SUA_API_KEY"
```

#### Python

```python
import requests

url = "http://127.0.0.1:8000/modbus/close"
headers = {"X-API-Key": "SUA_API_KEY"}

r = requests.post(url, headers=headers)
print(r.json())
```

---

## POST /modbus/reconnect

Força a **reconexão completa** com o servidor Modbus TCP.

Este endpoint:
1. Fecha a conexão atual (se existir)
2. Tenta estabelecer uma nova conexão
3. Retorna o estado atualizado da conectividade

---

### Requisição

```
POST /modbus/reconnect
```

#### Headers

| Header | Obrigatório |
|------|------------|
| `X-API-Key` | ✅ |

---

### Resposta de Sucesso

```json
{
  "ok": true,
  "connected": true,
  "host": "127.0.0.1",
  "port": 502,
  "unit_id": 1,
  "failure_count": 0,
  "current_retry_delay": 0.0
}
```

---

### Campos da Resposta

| Campo | Tipo | Descrição |
|-----|-----|-----------|
| `ok` | boolean | Status da requisição |
| `connected` | boolean | Estado atual da conexão Modbus |
| `host` | string | Host configurado |
| `port` | integer | Porta Modbus |
| `unit_id` | integer | Unit ID |
| `failure_count` | integer | Número de falhas consecutivas |
| `current_retry_delay` | number | Delay atual de retry (segundos) |

---

### Comportamento

- Fecha conexão existente antes de reconectar
- Não bloqueia a API se o servidor estiver offline
- Não executa leitura nem escrita de processo
- Seguro para uso manual e administrativo

---

### Erros Possíveis

| Código HTTP | Motivo |
|-----------|-------|
| 401 | API Key ausente ou inválida |
| 429 | Rate limit excedido |
| 503 | Servidor Modbus indisponível |

---

### Exemplo

#### cURL

```bash
curl -X POST "http://127.0.0.1:8000/modbus/reconnect" \
  -H "X-API-Key: SUA_API_KEY"
```

#### Python

```python
import requests

url = "http://127.0.0.1:8000/modbus/reconnect"
headers = {"X-API-Key": "SUA_API_KEY"}

r = requests.post(url, headers=headers)
print(r.json())
```

---

## Observações Operacionais

!!! info "Boas práticas"
    - Use estes endpoints apenas para **operação e manutenção**
    - Evite automação agressiva
    - Prefira retry automático interno para falhas transitórias
    - Estes endpoints não impactam diretamente o processo industrial
