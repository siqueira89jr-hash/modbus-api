# Typed Holding Registers

Os **Typed Holding Registers** permitem a **leitura e escrita** de **Holding Registers Modbus** interpretando os valores conforme o **tipo de dado** especificado, abstraindo completamente a conversão manual de registradores.

Esses registradores são normalmente utilizados para **setpoints**, **parâmetros**, **configurações** e **comandos numéricos**.

!!! warning "Atenção" 
    **Escrita em Holding Registers impacta diretamente o processo industrial.**

---

## Características

| Característica | Descrição |
|---------------|-----------|
| Tipo Modbus | Holding Registers |
| Acesso | Leitura e Escrita |
| Endereçamento | 0-based |
| Tipos suportados | uint16, int16, uint32, int32, uint64, int64, float32, float64 |
| Endianness | Configurável para tipos 32/64 bits |
| Autenticação | Obrigatória para escrita (`X-API-Key`) |

---

## Endpoints

### Leitura de Holding Registers Tipados

```
GET /modbus/registers/typed
```

---

### Escrita de Holding Registers Tipados

```
PUT /modbus/holding-registers/typed
```

---

## Parâmetros — Leitura

| Parâmetro | Tipo | Obrigatório | Descrição |
|---------|------|------------|-----------|
| `table` | string | ✅ | Deve ser `holding` |
| `addr` | integer | ✅ | Endereço inicial (0-based) |
| `dtype` | string | ✅ | Tipo de dado |
| `endian` | string | ❌ | Ordem de bytes/words (default = BE) |

---

## Parâmetros — Escrita

| Parâmetro | Tipo | Obrigatório | Descrição |
|---------|------|------------|-----------|
| `addr` | integer | ✅ | Endereço inicial (0-based) |
| `dtype` | string | ✅ | Tipo de dado |
| `endian` | string | ❌ | Ordem de bytes/words (default = BE) |
| `X-API-Key` | header | ✅ | Chave de autenticação |

### Body (Escrita)

```json
{
  "value": 42.5
}
```

---

## Tipos de Dados (`dtype`)

| Tipo | Registradores | Descrição |
|----|---------------|-----------|
| `uint16` | 1 | Inteiro sem sinal |
| `int16` | 1 | Inteiro com sinal |
| `uint32` | 2 | Inteiro sem sinal |
| `int32` | 2 | Inteiro com sinal |
| `uint64` | 4 | Inteiro sem sinal |
| `int64` | 4 | Inteiro com sinal |
| `float32` | 2 | Ponto flutuante |
| `float64` | 4 | Ponto flutuante |

---

## Faixa de Valores por Tipo (Range)

A tabela abaixo descreve a **faixa válida de valores** para cada tipo de dado suportado nos **Typed Holding Registers**.

Valores fora desses limites resultam em **erro HTTP 422 (Unprocessable Entity)**.

| Tipo | Bits | Registradores | Faixa de Valores |
|----|----|----|----|
| `uint16` | 16 | 1 | 0 … 65 535 |
| `int16` | 16 | 1 | −32 768 … 32 767 |
| `uint32` | 32 | 2 | 0 … 4 294 967 295 |
| `int32` | 32 | 2 | −2 147 483 648 … 2 147 483 647 |
| `uint64` | 64 | 4 | 0 … 18 446 744 073 709 551 615 |
| `int64` | 64 | 4 | −9 223 372 036 854 775 808 … 9 223 372 036 854 775 807 |
| `float32` | 32 | 2 | IEEE-754 (≈ ±3.4 × 10³⁸) |
| `float64` | 64 | 4 | IEEE-754 (≈ ±1.8 × 10³⁰⁸) |

!!! warning "Observações Importantes"
    - Para tipos `float32` e `float64`, valores **NaN** e **Infinity** não são permitidos  
    - Tipos de **16 bits** ignoram o parâmetro `endian`  
    - Tipos de **32 e 64 bits** exigem definição explícita de `endian`

---

## Endianness

O parâmetro `endian` define a ordem de **words e bytes** para tipos de 32 e 64 bits.

| Valor | Descrição |
|-----|-----------|
| `be` | Big-endian |
| `le` | Little-endian |
| `be_swap` | Big-endian com swap de words |
| `le_swap` | Little-endian com swap de words |

> Para tipos de 16 bits (`uint16`, `int16`), o parâmetro `endian` é ignorado.

---

## Resposta bem-sucedida — Leitura

```json
{
  "table": "holding",
  "addr": 20,
  "dtype": "float32",
  "endian": "be",
  "value": 75.0
}
```

---

## Resposta bem-sucedida — Escrita

```json
{
  "ok": true
}
```

---

## Segurança

- Leitura não exige autenticação
- Escrita exige API Key válida
- Validação rigorosa de tipos e limites
- Escrita de valores inválidos é rejeitada

---

## Erros Comuns

| Situação | Código HTTP |
|--------|-------------|
| API Key ausente ou inválida | 401 |
| Valor fora do intervalo | 422 |
| Tipo incompatível | 422 |
| Servidor Modbus indisponível | 503 |

---

## Boas Práticas

- Validar valores antes da escrita
- Evitar escrita cíclica desnecessária
- Consultar o Health antes de comandos críticos
- Usar Typed Holding apenas para parâmetros documentados

---

## Exemplos

### INT16 (Signed, 16-bits)

#### Leitura

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=holding&addr=0&dtype=int16"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "holding",
        "addr": 0,
        "dtype": "int16"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

#### Escrita

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/holding-registers/typed?addr=0&dtype=int16" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"value": -1234}'
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/holding-registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    headers = {
        "X-API-Key": "SUA_API_KEY"
    }

    params = {
        "addr": 0,
        "dtype": "int16"
    }

    payload = {
        "value": -1234
    }

    r = requests.put(url, params=params, json=payload, headers=headers)

    print(r.status_code)
    print(r.json())
    ```

---

### UINT16 (Unsigned, 16-bits)

#### Leitura

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=holding&addr=0&dtype=uint16"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "holding",
        "addr": 0,
        "dtype": "uint16"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

#### Escrita

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/holding-registers/typed?addr=0&dtype=uint16" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"value": 1234}'
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/holding-registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    headers = {
        "X-API-Key": "SUA_API_KEY"
    }

    params = {
        "addr": 0,
        "dtype": "uint16"
    }

    payload = {
        "value": 1234
    }

    r = requests.put(url, params=params, json=payload, headers=headers)

    print(r.status_code)
    print(r.json())
    ```

---

!!! info "Observações"
    - Para tipos **16 bits**, o parâmetro `endian` é ignorado  
    - Valores fora do range resultam em **HTTP 422**  
    - Escritas exigem autenticação via `X-API-Key`

### INT32 (Signed, 32-bits)

#### INT32 – Big Endian

##### Leitura

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=holding&addr=0&dtype=int32&endian=be"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "holding",
        "addr": 0,
        "dtype": "int32",
        "endian": "be"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

##### Escrita

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/holding-registers/typed?addr=0&dtype=int32&endian=be" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"value": -123456}'
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/holding-registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    headers = {
        "X-API-Key": "SUA_API_KEY"
    }

    params = {
        "addr": 0,
        "dtype": "int32",
        "endian": "be"
    }

    payload = {
        "value": -123456
    }

    r = requests.put(url, params=params, json=payload, headers=headers)

    print(r.status_code)
    print(r.json())
    ```

---

#### INT32 – Little Endian

##### Leitura

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=holding&addr=0&dtype=int32&endian=le"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "holding",
        "addr": 0,
        "dtype": "int32",
        "endian": "le"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

##### Escrita

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/holding-registers/typed?addr=0&dtype=int32&endian=le" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"value": -123456}'
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/holding-registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    headers = {
        "X-API-Key": "SUA_API_KEY"
    }

    params = {
        "addr": 0,
        "dtype": "int32",
        "endian": "le"
    }

    payload = {
        "value": -123456
    }

    r = requests.put(url, params=params, json=payload, headers=headers)

    print(r.status_code)
    print(r.json())
    ```

---

#### INT32 – Big Endian, Word Swap

##### Leitura

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=holding&addr=0&dtype=int32&endian=be_swap"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "holding",
        "addr": 0,
        "dtype": "int32",
        "endian": "be_swap"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

##### Escrita

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/holding-registers/typed?addr=0&dtype=int32&endian=be_swap" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"value": -123456}'
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/holding-registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    headers = {
        "X-API-Key": "SUA_API_KEY"
    }

    params = {
        "addr": 0,
        "dtype": "int32",
        "endian": "be_swap"
    }

    payload = {
        "value": -123456
    }

    r = requests.put(url, params=params, json=payload, headers=headers)

    print(r.status_code)
    print(r.json())
    ```

---

#### INT32 – Little Endian, Word Swap

##### Leitura

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=holding&addr=0&dtype=int32&endian=le_swap"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "holding",
        "addr": 0,
        "dtype": "int32",
        "endian": "le_swap"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

##### Escrita

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/holding-registers/typed?addr=0&dtype=int32&endian=le_swap" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"value": -123456}'
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/holding-registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    headers = {
        "X-API-Key": "SUA_API_KEY"
    }

    params = {
        "addr": 0,
        "dtype": "int32",
        "endian": "le_swap"
    }

    payload = {
        "value": -123456
    }

    r = requests.put(url, params=params, json=payload, headers=headers)

    print(r.status_code)
    print(r.json())
    ```

---

!!! info "Observações"
    - `INT32` utiliza **2 Holding Registers**
    - O parâmetro `endian` é **obrigatório** para tipos de 32 bits
    - Escritas exigem autenticação via `X-API-Key`
    - Valores fora do range resultam em **HTTP 422**

### UINT32 (Unsigned, 32-bits)

#### UINT32 – Big Endian

##### Leitura

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=holding&addr=0&dtype=uint32&endian=be"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "holding",
        "addr": 0,
        "dtype": "uint32",
        "endian": "be"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

##### Escrita

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/holding-registers/typed?addr=0&dtype=uint32&endian=be" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"value": 123456}'
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/holding-registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    headers = {
        "X-API-Key": "SUA_API_KEY"
    }

    params = {
        "addr": 0,
        "dtype": "uint32",
        "endian": "be"
    }

    payload = {
        "value": 123456
    }

    r = requests.put(url, params=params, json=payload, headers=headers)

    print(r.status_code)
    print(r.json())
    ```

---

#### UINT32 – Little Endian

##### Leitura

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=holding&addr=0&dtype=uint32&endian=le"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "holding",
        "addr": 0,
        "dtype": "uint32",
        "endian": "le"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

##### Escrita

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/holding-registers/typed?addr=0&dtype=uint32&endian=le" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"value": 123456}'
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/holding-registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    headers = {
        "X-API-Key": "SUA_API_KEY"
    }

    params = {
        "addr": 0,
        "dtype": "uint32",
        "endian": "le"
    }

    payload = {
        "value": 123456
    }

    r = requests.put(url, params=params, json=payload, headers=headers)

    print(r.status_code)
    print(r.json())
    ```

---

#### UINT32 – Big Endian, Word Swap

##### Leitura

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=holding&addr=0&dtype=uint32&endian=be_swap"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "holding",
        "addr": 0,
        "dtype": "uint32",
        "endian": "be_swap"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

##### Escrita

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/holding-registers/typed?addr=0&dtype=uint32&endian=be_swap" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"value": 123456}'
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/holding-registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    headers = {
        "X-API-Key": "SUA_API_KEY"
    }

    params = {
        "addr": 0,
        "dtype": "uint32",
        "endian": "be_swap"
    }

    payload = {
        "value": 123456
    }

    r = requests.put(url, params=params, json=payload, headers=headers)

    print(r.status_code)
    print(r.json())
    ```

---

#### UINT32 – Little Endian, Word Swap

##### Leitura

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=holding&addr=0&dtype=uint32&endian=le_swap"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "holding",
        "addr": 0,
        "dtype": "uint32",
        "endian": "le_swap"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

##### Escrita

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/holding-registers/typed?addr=0&dtype=uint32&endian=le_swap" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"value": 123456}'
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/holding-registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    headers = {
        "X-API-Key": "SUA_API_KEY"
    }

    params = {
        "addr": 0,
        "dtype": "uint32",
        "endian": "le_swap"
    }

    payload = {
        "value": 123456
    }

    r = requests.put(url, params=params, json=payload, headers=headers)

    print(r.status_code)
    print(r.json())
    ```

---

!!! info "Observações"
    - `UINT32` utiliza **2 Holding Registers**
    - O parâmetro `endian` é **obrigatório** para tipos de 32 bits
    - Escritas exigem autenticação via `X-API-Key`
    - Valores fora do range resultam em **HTTP 422**

### INT64 (Signed, 64-bits)

#### INT64 – Big Endian

##### Leitura

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=holding&addr=0&dtype=int64&endian=be"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "holding",
        "addr": 0,
        "dtype": "int64",
        "endian": "be"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

##### Escrita

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/holding-registers/typed?addr=0&dtype=int64&endian=be" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"value": -1234567890123}'
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/holding-registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    headers = {
        "X-API-Key": "SUA_API_KEY"
    }

    params = {
        "addr": 0,
        "dtype": "int64",
        "endian": "be"
    }

    payload = {
        "value": -1234567890123
    }

    r = requests.put(url, params=params, json=payload, headers=headers)

    print(r.status_code)
    print(r.json())
    ```

---

#### INT64 – Little Endian

##### Leitura

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=holding&addr=0&dtype=int64&endian=le"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "holding",
        "addr": 0,
        "dtype": "int64",
        "endian": "le"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

##### Escrita

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/holding-registers/typed?addr=0&dtype=int64&endian=le" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"value": -1234567890123}'
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/holding-registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    headers = {
        "X-API-Key": "SUA_API_KEY"
    }

    params = {
        "addr": 0,
        "dtype": "int64",
        "endian": "le"
    }

    payload = {
        "value": -1234567890123
    }

    r = requests.put(url, params=params, json=payload, headers=headers)

    print(r.status_code)
    print(r.json())
    ```

---

#### INT64 – Big Endian, Word Swap

##### Leitura

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=holding&addr=0&dtype=int64&endian=be_swap"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "holding",
        "addr": 0,
        "dtype": "int64",
        "endian": "be_swap"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

##### Escrita

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/holding-registers/typed?addr=0&dtype=int64&endian=be_swap" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"value": -1234567890123}'
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/holding-registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    headers = {
        "X-API-Key": "SUA_API_KEY"
    }

    params = {
        "addr": 0,
        "dtype": "int64",
        "endian": "be_swap"
    }

    payload = {
        "value": -1234567890123
    }

    r = requests.put(url, params=params, json=payload, headers=headers)

    print(r.status_code)
    print(r.json())
    ```

---

#### INT64 – Little Endian, Word Swap

##### Leitura

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=holding&addr=0&dtype=int64&endian=le_swap"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "holding",
        "addr": 0,
        "dtype": "int64",
        "endian": "le_swap"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

##### Escrita

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/holding-registers/typed?addr=0&dtype=int64&endian=le_swap" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"value": -1234567890123}'
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/holding-registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    headers = {
        "X-API-Key": "SUA_API_KEY"
    }

    params = {
        "addr": 0,
        "dtype": "int64",
        "endian": "le_swap"
    }

    payload = {
        "value": -1234567890123
    }

    r = requests.put(url, params=params, json=payload, headers=headers)

    print(r.status_code)
    print(r.json())
    ```

---

!!! info "Observações"
    - `INT64` utiliza **4 Holding Registers**
    - O parâmetro `endian` é **obrigatório** para tipos de 64 bits
    - Escritas exigem autenticação via `X-API-Key`
    - Valores fora do range resultam em **HTTP 422**

### UINT64 (Unsigned, 64-bits)

#### UINT64 – Big Endian

##### Leitura

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=holding&addr=0&dtype=uint64&endian=be"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "holding",
        "addr": 0,
        "dtype": "uint64",
        "endian": "be"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

##### Escrita

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/holding-registers/typed?addr=0&dtype=uint64&endian=be" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"value": 123456789012345}'
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/holding-registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    headers = {
        "X-API-Key": "SUA_API_KEY"
    }

    params = {
        "addr": 0,
        "dtype": "uint64",
        "endian": "be"
    }

    payload = {
        "value": 123456789012345
    }

    r = requests.put(url, params=params, json=payload, headers=headers)

    print(r.status_code)
    print(r.json())
    ```

---

#### UINT64 – Little Endian

##### Leitura

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=holding&addr=0&dtype=uint64&endian=le"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "holding",
        "addr": 0,
        "dtype": "uint64",
        "endian": "le"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

##### Escrita

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/holding-registers/typed?addr=0&dtype=uint64&endian=le" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"value": 123456789012345}'
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/holding-registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    headers = {
        "X-API-Key": "SUA_API_KEY"
    }

    params = {
        "addr": 0,
        "dtype": "uint64",
        "endian": "le"
    }

    payload = {
        "value": 123456789012345
    }

    r = requests.put(url, params=params, json=payload, headers=headers)

    print(r.status_code)
    print(r.json())
    ```

---

#### UINT64 – Big Endian, Word Swap

##### Leitura

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=holding&addr=0&dtype=uint64&endian=be_swap"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "holding",
        "addr": 0,
        "dtype": "uint64",
        "endian": "be_swap"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

##### Escrita

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/holding-registers/typed?addr=0&dtype=uint64&endian=be_swap" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"value": 123456789012345}'
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/holding-registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    headers = {
        "X-API-Key": "SUA_API_KEY"
    }

    params = {
        "addr": 0,
        "dtype": "uint64",
        "endian": "be_swap"
    }

    payload = {
        "value": 123456789012345
    }

    r = requests.put(url, params=params, json=payload, headers=headers)

    print(r.status_code)
    print(r.json())
    ```

---

#### UINT64 – Little Endian, Word Swap

##### Leitura

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=holding&addr=0&dtype=uint64&endian=le_swap"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "holding",
        "addr": 0,
        "dtype": "uint64",
        "endian": "le_swap"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

##### Escrita

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/holding-registers/typed?addr=0&dtype=uint64&endian=le_swap" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"value": 123456789012345}'
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/holding-registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    headers = {
        "X-API-Key": "SUA_API_KEY"
    }

    params = {
        "addr": 0,
        "dtype": "uint64",
        "endian": "le_swap"
    }

    payload = {
        "value": 123456789012345
    }

    r = requests.put(url, params=params, json=payload, headers=headers)

    print(r.status_code)
    print(r.json())
    ```

---

!!! info "Observações"
    - `UINT64` utiliza **4 Holding Registers**
    - O parâmetro `endian` é **obrigatório** para tipos de 64 bits
    - Escritas exigem autenticação via `X-API-Key`
    - Valores fora do range resultam em **HTTP 422**

### FLOAT32 (IEEE-754, 32-bits)

#### FLOAT32 – Big Endian

##### Leitura

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=holding&addr=0&dtype=float32&endian=be"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "holding",
        "addr": 0,
        "dtype": "float32",
        "endian": "be"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

##### Escrita

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/holding-registers/typed?addr=0&dtype=float32&endian=be" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"value": 12.34}'
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/holding-registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    headers = {
        "X-API-Key": "SUA_API_KEY"
    }

    params = {
        "addr": 0,
        "dtype": "float32",
        "endian": "be"
    }

    payload = {
        "value": 12.34
    }

    r = requests.put(url, params=params, json=payload, headers=headers)

    print(r.status_code)
    print(r.json())
    ```

---

#### FLOAT32 – Little Endian

##### Leitura

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=holding&addr=0&dtype=float32&endian=le"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "holding",
        "addr": 0,
        "dtype": "float32",
        "endian": "le"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

##### Escrita

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/holding-registers/typed?addr=0&dtype=float32&endian=le" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"value": 12.34}'
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/holding-registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    headers = {
        "X-API-Key": "SUA_API_KEY"
    }

    params = {
        "addr": 0,
        "dtype": "float32",
        "endian": "le"
    }

    payload = {
        "value": 12.34
    }

    r = requests.put(url, params=params, json=payload, headers=headers)

    print(r.status_code)
    print(r.json())
    ```

---

#### FLOAT32 – Big Endian, Word Swap

##### Leitura

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=holding&addr=0&dtype=float32&endian=be_swap"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "holding",
        "addr": 0,
        "dtype": "float32",
        "endian": "be_swap"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

##### Escrita

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/holding-registers/typed?addr=0&dtype=float32&endian=be_swap" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"value": 12.34}'
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/holding-registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    headers = {
        "X-API-Key": "SUA_API_KEY"
    }

    params = {
        "addr": 0,
        "dtype": "float32",
        "endian": "be_swap"
    }

    payload = {
        "value": 12.34
    }

    r = requests.put(url, params=params, json=payload, headers=headers)

    print(r.status_code)
    print(r.json())
    ```

---

#### FLOAT32 – Little Endian, Word Swap

##### Leitura

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=holding&addr=0&dtype=float32&endian=le_swap"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "holding",
        "addr": 0,
        "dtype": "float32",
        "endian": "le_swap"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

##### Escrita

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/holding-registers/typed?addr=0&dtype=float32&endian=le_swap" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"value": 12.34}'
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/holding-registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    headers = {
        "X-API-Key": "SUA_API_KEY"
    }

    params = {
        "addr": 0,
        "dtype": "float32",
        "endian": "le_swap"
    }

    payload = {
        "value": 12.34
    }

    r = requests.put(url, params=params, json=payload, headers=headers)

    print(r.status_code)
    print(r.json())
    ```

---

!!! info "Observações"
    - `FLOAT32` utiliza **2 Holding Registers**
    - O parâmetro `endian` é **obrigatório** para tipos de 32 bits
    - Valores **NaN** e **Infinity** não são permitidos
    - Escritas exigem autenticação via `X-API-Key`

### FLOAT64 (IEEE-754, 64-bits)

Os exemplos abaixo demonstram **leitura e escrita** de **FLOAT64** em **Holding Registers**, cobrindo **todas as variações de endianness** suportadas pela API.

---

#### FLOAT64 – Big Endian

##### Leitura

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=holding&addr=0&dtype=float64&endian=be"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "holding",
        "addr": 0,
        "dtype": "float64",
        "endian": "be"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

##### Escrita

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/holding-registers/typed?addr=0&dtype=float64&endian=be" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"value": 1234.5678}'
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/holding-registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    headers = {
        "X-API-Key": "SUA_API_KEY"
    }

    params = {
        "addr": 0,
        "dtype": "float64",
        "endian": "be"
    }

    payload = {
        "value": 1234.5678
    }

    r = requests.put(url, params=params, json=payload, headers=headers)

    print(r.status_code)
    print(r.json())
    ```

---

#### FLOAT64 – Little Endian

##### Leitura

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=holding&addr=0&dtype=float64&endian=le"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "holding",
        "addr": 0,
        "dtype": "float64",
        "endian": "le"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

##### Escrita

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/holding-registers/typed?addr=0&dtype=float64&endian=le" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"value": 1234.5678}'
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/holding-registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    headers = {
        "X-API-Key": "SUA_API_KEY"
    }

    params = {
        "addr": 0,
        "dtype": "float64",
        "endian": "le"
    }

    payload = {
        "value": 1234.5678
    }

    r = requests.put(url, params=params, json=payload, headers=headers)

    print(r.status_code)
    print(r.json())
    ```

---

#### FLOAT64 – Big Endian, Word Swap

##### Leitura

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=holding&addr=0&dtype=float64&endian=be_swap"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "holding",
        "addr": 0,
        "dtype": "float64",
        "endian": "be_swap"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

##### Escrita

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/holding-registers/typed?addr=0&dtype=float64&endian=be_swap" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"value": 1234.5678}'
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/holding-registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    headers = {
        "X-API-Key": "SUA_API_KEY"
    }

    params = {
        "addr": 0,
        "dtype": "float64",
        "endian": "be_swap"
    }

    payload = {
        "value": 1234.5678
    }

    r = requests.put(url, params=params, json=payload, headers=headers)

    print(r.status_code)
    print(r.json())
    ```

---

#### FLOAT64 – Little Endian, Word Swap

##### Leitura

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=holding&addr=0&dtype=float64&endian=le_swap"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "holding",
        "addr": 0,
        "dtype": "float64",
        "endian": "le_swap"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

##### Escrita

=== "cURL"

    ```bash
    curl -X PUT "http://127.0.0.1:8000/modbus/holding-registers/typed?addr=0&dtype=float64&endian=le_swap" \
      -H "X-API-Key: SUA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"value": 1234.5678}'
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/holding-registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    headers = {
        "X-API-Key": "SUA_API_KEY"
    }

    params = {
        "addr": 0,
        "dtype": "float64",
        "endian": "le_swap"
    }

    payload = {
        "value": 1234.5678
    }

    r = requests.put(url, params=params, json=payload, headers=headers)

    print(r.status_code)
    print(r.json())
    ```

---

!!! info "Observações"
    - `FLOAT64` utiliza **4 Holding Registers**
    - O parâmetro `endian` é **obrigatório** para tipos de 64 bits
    - Valores **NaN** e **Infinity** não são permitidos
    - Escritas exigem autenticação via `X-API-Key`
