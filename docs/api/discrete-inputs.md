# Discrete Inputs

As **Discrete Inputs** representam **entradas digitais (bits somente de leitura)** no protocolo Modbus. Eles refletem o estado de sensores, botões ou contatos físicos e **não podem ser escritos**. Na **Modbus API**, os discrete inputs são expostos via endpoint HTTP REST, abstraindo completamente o protocolo Modbus TCP.

---

## Características

| Característica | Descrição |
|---------------|-----------|
| Tipo de dado | Boolean (`true` / `false`) |
| Tamanho | 1 bit |
| Endereçamento | 0-based |
| Acesso | Somente leitura |
| Quantidade máxima | 2000 inputs por requisição |

---

## Endpoint

### Leitura de Discrete Inputs

```
GET /modbus/discrete-inputs

```

#### Parâmetros

| Parâmetro | Tipo | Obrigatório | Descrição |
|----------|------|------------|-----------|
| `addr` | integer | ✅ | Endereço inicial (0-based) |
| `count` | integer | ❌ | Quantidade de entradas (default = 1, máx = 2000) |


#### Resposta bem-sucedida

```json
{
  "addr": 0,
  "count": 3,
  "values": [true, false, true]
}
```

#### Exemplo

=== "cURL"

    ```bash
    curl -X GET "http://127.0.0.1:8000/modbus/discrete-inputs?addr=0&count=3"
    ```

=== "Python"

    ```python
    import requests

    url = "http://127.0.0.1:8000/modbus/discrete-inputs"
    params = {
        "addr": 0,
        "count": 3
    }

    r = requests.get(url, params=params)
    print(r.json())
    ```

---

## Modelos de Dados

| Modelo | Descrição |
|------|-----------|
| `ReadBitsResponse` | Retorno da leitura de discrete inputs |

---

## Segurança

* Operações de leitura não exigem autenticação
* Escrita não é suportada para discrete inputs

## Erros Comuns

| Situação | Resultado |
|--------|-----------|
| Endereço inválido | Erro Modbus |
| Quantidade acima do limite | HTTP 400 |
| CLP/Servidor offline | HTTP 503 |