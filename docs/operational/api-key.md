# API Key

A Modbus API utiliza **API Key** como mecanismo principal de autenticação para **operações sensíveis**, como escrita em coils e registradores.

A autenticação é simples, explícita e compatível com qualquer cliente HTTP.

---

## Visão Geral

- A API Key é enviada via **header HTTP**
- O nome do header é **`X-API-Key`**
- Apenas **operações de escrita** exigem autenticação
- Operações de leitura são públicas por padrão

---

## Header de Autenticação

```http
X-API-Key: SUA_API_KEY
```

!!! warning "Obrigatório para escrita"
    Endpoints que realizam **escrita Modbus** exigem autenticação via API Key.

---

## Onde a API Key é exigida

| Endpoint | Método | Autenticação |
|--------|--------|---------------|
| `/modbus/coil` | `PUT` | :material-check: Obrigatória |
| `/modbus/coils` | `PUT` | :material-check: Obrigatória |
| `/modbus/holding-register` | `PUT` | :material-check: Obrigatória |
| `/modbus/holding-registers` | `PUT` | :material-check: Obrigatória |
| `/modbus/coils` | `GET` | :material-close: Não exigida |
| `/modbus/discrete-inputs` | `GET` | :material-close: Não exigida |

---

## Exemplo de Uso

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/coils?addr=0&count=2" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"values": [true, false]}'
    ```

=== "Python"

    ```python
    import requests

    url = "http://127.0.0.1:8000/modbus/coils"
    headers = {"X-API-Key": "SUA_API_KEY"}
    params = {"addr": 0, "count": 2}
    payload = {"values": [True, False]}

    r = requests.put(url, params=params, json=payload, headers=headers)
    print(r.json())
    ```

---

## Erros de Autenticação

| Situação | Código HTTP | Descrição |
|--------|-------------|-----------|
| API Key ausente | `401` | Header não informado |
| API Key inválida | `401` | Chave incorreta |

!!! info "Segurança"
    A validação da API Key utiliza **comparação segura (timing-safe)** para evitar ataques de tempo.

---

## Boas Práticas
* Nunca versionar a API Key no código
* Utilizar variáveis de ambiente
* Rotacionar a chave periodicamente
* Usar HTTPS em produção