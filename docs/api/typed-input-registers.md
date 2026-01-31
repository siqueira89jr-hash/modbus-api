# Typed Input Registers

Os **Typed Input Registers** permitem a leitura de **Input Registers Modbus** interpretando os valores conforme o **tipo de dado** especificado, abstraindo completamente a conversão manual de registradores. Esses registradores são **somente leitura** e normalmente representam **medições**, **sensores** e **variáveis de processo**.

---

## Características

| Característica | Descrição |
|---------------|-----------|
| Tipo Modbus | Input Registers |
| Acesso | Somente leitura |
| Endereçamento | 0-based |
| Tipos suportados | uint16, int16, uint32, int32, uint64, int64, float32, float64 |
| Endianness | Configurável para tipos 32/64 bits |

---

## Endpoint

### Leitura de Input Registers Tipados

```
GET /modbus/registers/typed
```

---

## Parâmetros

| Parâmetro | Tipo | Obrigatório | Descrição |
|---------|------|------------|-----------|
| `table` | string | ✅ | Deve ser `input` |
| `addr` | integer | ✅ | Endereço inicial (0-based) |
| `dtype` | string | ✅ | Tipo de dado |
| `endian` | string | ❌ | Ordem de bytes/words (default = BE) |

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

A tabela abaixo descreve a **faixa válida de valores** para cada tipo de dado suportado nos **Typed Input Registers**.

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

## Resposta bem-sucedida

```json
{
  "table": "input",
  "addr": 10,
  "dtype": "float32",
  "endian": "be",
  "value": 23.75
}
```

---

## Campos da Resposta

| Campo | Tipo | Descrição |
|-----|-----|-----------|
| `table` | string | Tabela Modbus (`input`) |
| `addr` | integer | Endereço inicial |
| `dtype` | string | Tipo interpretado |
| `endian` | string | Endianness aplicado |
| `value` | number | Valor convertido |

---

## Segurança

- Não requer autenticação
- Escrita não é suportada para Input Registers

---

## Erros Comuns

| Situação | Código HTTP |
|--------|-------------|
| Endereço inválido | 400 |
| Tipo incompatível | 422 |
| Servidor Modbus indisponível | 503 |

---

## Exemplos

### Int16 (Signed, 16-bits)

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=input&addr=0&dtype=int16"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "input",
        "addr": 0,
        "dtype": "int16"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

---

### UINT16 (Unsigned, 16-bits)

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=input&addr=0&dtype=uint16"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "input",
        "addr": 0,
        "dtype": "uint16"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

---

### INT32 (Signed, 32-bits) – Big Endian

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=input&addr=0&dtype=int32&endian=be"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "input",
        "addr": 0,
        "dtype": "int32",
        "endian": "be"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

---

### INT32 (Signed, 32-bits) – Little Endian

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=input&addr=0&dtype=int32&endian=le"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "input",
        "addr": 0,
        "dtype": "int32",
        "endian": "le"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

---

### INT32 (Signed, 32-bits) – Big Endian, Word Swap

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=input&addr=0&dtype=int32&endian=be_swap"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "input",
        "addr": 0,
        "dtype": "int32",
        "endian": "be_swap"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

### INT32 (Signed, 32-bits) – Little Endian, Word Swap

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=input&addr=0&dtype=int32&endian=le_swap"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "input",
        "addr": 0,
        "dtype": "int32",
        "endian": "le_swap"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

### UINT32 (Unsigned, 32-bits) – Big Endian

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=input&addr=0&dtype=uint32&endian=be"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "input",
        "addr": 0,
        "dtype": "uint32",
        "endian": "be"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

### UINT32 (Unsigned, 32-bits) – Little Endian

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=input&addr=0&dtype=uint32&endian=le"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "input",
        "addr": 0,
        "dtype": "uint32",
        "endian": "le"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

### UINT32 (Unsigned, 32-bits) – Big Endian, Word Swap

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=input&addr=0&dtype=uint32&endian=be_swap"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "input",
        "addr": 0,
        "dtype": "uint32",
        "endian": "be_swap"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

### UINT32 (Unsigned, 32-bits) – Little Endian, Word Swap

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=input&addr=0&dtype=uint32&endian=le_swap"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "input",
        "addr": 0,
        "dtype": "uint32",
        "endian": "le_swap"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

### INT64 (Signed, 64-bits) – Big Endian

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=input&addr=0&dtype=int64&endian=be"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "input",
        "addr": 0,
        "dtype": "int64",
        "endian": "be"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

---

### INT64 (Signed, 64-bits) – Little Endian

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=input&addr=0&dtype=int64&endian=le"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "input",
        "addr": 0,
        "dtype": "int64",
        "endian": "le"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

---

### INT64 (Signed, 64-bits) – Big Endian, Word Swap

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=input&addr=0&dtype=int64&endian=be_swap"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "input",
        "addr": 0,
        "dtype": "int64",
        "endian": "be_swap"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

---

### INT64 (Signed, 64-bits) – Little Endian, Word Swap

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=input&addr=0&dtype=int64&endian=le_swap"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "input",
        "addr": 0,
        "dtype": "int64",
        "endian": "le_swap"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

### UINT64 (Unsigned, 64-bits) – Big Endian

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=input&addr=0&dtype=uint64&endian=be"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "input",
        "addr": 0,
        "dtype": "uint64",
        "endian": "be"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

---

### UINT64 (Unsigned, 64-bits) – Little Endian

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=input&addr=0&dtype=uint64&endian=le"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "input",
        "addr": 0,
        "dtype": "uint64",
        "endian": "le"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

---

### UINT64 (Unsigned, 64-bits) – Big Endian, Word Swap

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=input&addr=0&dtype=uint64&endian=be_swap"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "input",
        "addr": 0,
        "dtype": "uint64",
        "endian": "be_swap"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

---

### UINT64 (Unsigned, 64-bits) – Little Endian, Word Swap

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=input&addr=0&dtype=uint64&endian=le_swap"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "input",
        "addr": 0,
        "dtype": "uint64",
        "endian": "le_swap"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

### FLOAT32 (IEEE-754, 32-bits) – Big Endian

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=input&addr=0&dtype=float32&endian=be"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "input",
        "addr": 0,
        "dtype": "float32",
        "endian": "be"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

---

### FLOAT32 (IEEE-754, 32-bits) – Little Endian

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=input&addr=0&dtype=float32&endian=le"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "input",
        "addr": 0,
        "dtype": "float32",
        "endian": "le"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

---

### FLOAT32 (IEEE-754, 32-bits) – Big Endian, Word Swap

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=input&addr=0&dtype=float32&endian=be_swap"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "input",
        "addr": 0,
        "dtype": "float32",
        "endian": "be_swap"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

---

### FLOAT32 (IEEE-754, 32-bits) – Little Endian, Word Swap

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=input&addr=0&dtype=float32&endian=le_swap"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "input",
        "addr": 0,
        "dtype": "float32",
        "endian": "le_swap"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```
### FLOAT64 (IEEE-754, 64-bits) – Big Endian

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=input&addr=0&dtype=float64&endian=be"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "input",
        "addr": 0,
        "dtype": "float64",
        "endian": "be"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

---

### FLOAT64 (IEEE-754, 64-bits) – Little Endian

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=input&addr=0&dtype=float64&endian=le"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "input",
        "addr": 0,
        "dtype": "float64",
        "endian": "le"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

---

### FLOAT64 (IEEE-754, 64-bits) – Big Endian, Word Swap

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=input&addr=0&dtype=float64&endian=be_swap"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "input",
        "addr": 0,
        "dtype": "float64",
        "endian": "be_swap"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```

---

### FLOAT64 (IEEE-754, 64-bits) – Little Endian, Word Swap

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=input&addr=0&dtype=float64&endian=le_swap"
    ```

=== "Python"

    ```python
    import requests

    BASE_URL = "http://127.0.0.1:8000"
    ENDPOINT = "/modbus/registers/typed"

    url = f"{BASE_URL}{ENDPOINT}"

    params = {
        "table": "input",
        "addr": 0,
        "dtype": "float64",
        "endian": "le_swap"
    }

    r = requests.get(url, params=params)

    print(r.status_code)
    print(r.json())
    ```
