# Health Check

O **Health Check** permite verificar o estado operacional da **Modbus API** e da **conexão com o servidor Modbus TCP**, sem executar nenhuma operação de leitura ou escrita em registradores ou coils.

Esse endpoint é essencial para:
- Monitoramento
- Orquestradores (Docker, Kubernetes)
- Load balancers
- Diagnóstico rápido de falhas

---

## Endpoint

### Status da Conexão Modbus

```
GET /health/modbus
```

---

## O que este endpoint verifica

| Item | Descrição |
|----|-----------|
| API ativa | O serviço HTTP está respondendo |
| Cliente Modbus | Cliente Modbus inicializado |
| Conectividade | Possibilidade de conexão com o servidor Modbus |
| Parâmetros | Host, porta e Unit ID em uso |
| Estado interno | Contadores de falha e atraso de reconexão |

!!! warning "Atenção" 
    **Nenhuma escrita ou leitura de dados Modbus é realizada.**

---

## Parâmetros

Este endpoint **não recebe parâmetros**.

---

## Resposta bem-sucedida

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

## Campos da resposta

| Campo | Tipo | Descrição |
|----|----|-----------|
| `ok` | boolean | Indica que a API respondeu corretamente |
| `connected` | boolean | Indica se a conexão Modbus está ativa |
| `host` | string | Endereço do servidor Modbus |
| `port` | integer | Porta Modbus TCP |
| `unit_id` | integer | Unit ID configurado |
| `failure_count` | integer | Número de falhas consecutivas de conexão |
| `current_retry_delay` | number | Delay atual aplicado antes de nova tentativa |

---

## Exemplos de uso

### cURL

```bash
curl -X GET http://127.0.0.1:8000/health/modbus
```

### Python

```python
import requests

url = "http://127.0.0.1:8000/health/modbus"
r = requests.get(url)

print(r.json())
```

---

## Interpretação do status

### API e Modbus operacionais

```json
{
  "connected": true
}
```

- A API está pronta para leitura e escrita
- Comunicação Modbus disponível
- Operação segura

---

### API ativa, Modbus indisponível

```json
{
  "connected": false
}
```

- API está rodando
- Servidor Modbus offline ou inacessível
- Escritas e leituras Modbus podem falhar
- Ideal para acionar alertas

---

## Códigos HTTP

| Código | Quando ocorre |
|----|-------------|
| `200` | Health check executado com sucesso |
| `500` | Erro interno ao verificar o estado |

---

## Boas Práticas

- Consultar o Health antes de operações críticas
- Usar este endpoint em monitoramento contínuo
- Integrar com sistemas de alerta
- Não usar Health como substituto de leitura funcional

---

## Observação Importante

> O endpoint de Health **não garante que todas as operações Modbus irão funcionar**, apenas que a conectividade básica está disponível no momento da verificação.
