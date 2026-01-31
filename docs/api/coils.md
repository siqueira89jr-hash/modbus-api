# Coils

Os **Coils** representam **saídas digitais (bits)** no protocolo Modbus.  
Cada coil armazena um valor booleano (`true` / `false`) e pode ser **lido ou escrito**.

Na **Modbus API**, os coils são expostos via endpoints HTTP REST, abstraindo completamente o protocolo Modbus TCP.

---

## Características

| Característica | Descrição |
|---------------|-----------|
| Tipo de dado | Boolean (`true` / `false`) |
| Tamanho | 1 bit |
| Endereçamento | 0-based |
| Acesso | Leitura e Escrita |
| Quantidade máxima | 2000 coils por requisição |

---

## Endpoints

### Leitura de Coils

```
GET /modbus/coils
```

#### Parâmetros

| Parâmetro | Tipo | Obrigatório | Descrição |
|----------|------|------------|-----------|
| `addr` | integer | ✅ | Endereço inicial (0-based) |
| `count` | integer | ❌ | Quantidade de coils (default = 1, máx = 2000) |

#### Resposta bem-sucedida

```json
{
  "addr": 0,
  "count": 3,
  "values": [true, false, true]
}
```

---

#### Exemplo

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/coils?addr=0&count=3"
    ```

=== "Python"

    ```python
    import requests

    url = "http://127.0.0.1:8000/modbus/coils"
    params = {
        "addr": 0,
        "count": 3
    }

    r = requests.get(url, params=params)
    print(r.json())
    ```

---

### Escrita em uma Única Coil

```
PUT /modbus/coil
```

!!! warning "Atenção" 
    Requer autenticação via `X-API-Key`

#### Parâmetros

| Parâmetro | Tipo | Obrigatório |
|----------|------|------------|
| `addr` | integer | ✅ |
| `X-API-Key` | header | ✅ |

#### Body

```json
{
  "value": true
}
```

#### Resposta bem-sucedida

```json
{
  "ok": true
}
```

#### Exemplo 

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/coil?addr=0" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"value": false}'
    ```

=== "Python"

    ```python
    import requests

    url = "http://127.0.0.1:8000/modbus/coil"
    headers = {"X-API-Key": "SUA_API_KEY"}
    params = {"addr": 0}
    payload = {"value": False}

    r = requests.put(url, params=params, json=payload, headers=headers)
    print(r.json())
    ```

---

### Escrita de Múltiplas Coils

```
PUT /modbus/coils
```

!!! warning "Atenção" 
    Requer autenticação via `X-API-Key`

#### Parâmetros

| Parâmetro | Tipo | Obrigatório |
|----------|------|------------|
| `addr` | integer | ✅ |
| `X-API-Key` | header | ✅ |

#### Body

```json
{
  "values": [true, true, false]
}
```

!!! info
    O número de coils escritas é determinado pelo tamanho do array `values`.

#### Resposta bem-sucedida

```json
{
  "ok": true
}
```

#### Exemplo

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/coils?addr=0&count=3" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"values": [true, false, true]}'
    ```

=== "Python"

    ```python
    import requests

    url = "http://127.0.0.1:8000/modbus/coils"
    headers = {"X-API-Key": "SUA_API_KEY"}
    params = {"addr": 0, "count": 3}
    payload = {"values": [True, False, True]}

    r = requests.put(url, params=params, json=payload, headers=headers)
    print(r.json())
    ```
---

## Modelos de Dados

| Modelo | Descrição |
|------|-----------|
| `ReadBitsResponse` | Retorno da leitura de coils |
| `WriteSingleCoilRequest` | Escrita de uma única coil |
| `WriteMultipleCoilsRequest` | Escrita de múltiplas coils |

---

## Segurança

- Operações de **leitura** não exigem autenticação
- Operações de **escrita** exigem o header `X-API-Key`

```http
X-API-Key: SUA_API_KEY
```

---

## Erros Comuns

| Situação | Resultado |
|--------|-----------|
| Endereço inválido | Erro Modbus |
| Quantidade acima do limite | HTTP 400 |
| CLP/Servidor offline | HTTP 503 |
| API Key ausente ou inválida | HTTP 401 |