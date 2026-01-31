# Rate Limit

A Modbus API utiliza **Rate Limiting** para proteger o serviço contra abuso, uso excessivo e ataques automatizados, garantindo estabilidade e previsibilidade para todos os clientes. O controle de requisições é aplicado **por cliente** e **por janela de tempo**, atuando antes da lógica Modbus.

---

## Visão Geral

* Limita o número de requisições por cliente
* Evita sobrecarga do servidor e do CLP
* Protege contra ataques de força bruta
* Atua antes da lógica Modbus (camada HTTP)

---

## Como Funciona

O Rate Limit é aplicado na **camada HTTP**, antes de qualquer acesso ao barramento Modbus.

Cada cliente pode realizar apenas um número limitado de requisições dentro de um intervalo de tempo definido.

Quando o limite é atingido:

* As requisições excedentes são bloqueadas
* O CLP não é acessado
* O servidor retorna erro HTTP apropriado

---

## Critério de Identificação

O controle de requisições pode ser baseado em:

| Critério | Descrição |
|--------|----------|
| Endereço IP | Limite por origem da requisição |
| API Key | Limite associado à chave |
| IP + API Key | Estratégia combinada (recomendada) |

---

## Endpoints Afetados

O Rate Limit é aplicado a **todos os endpoints** da API.

| Endpoint | Método | Sujeito a Rate Limit |
|--------|--------|----------------------|
| `/modbus/coil` | `GET` / `PUT` | :material-check: |
| `/modbus/coils` | `GET` / `PUT` | :material-check: |
| `/modbus/discrete-inputs` | `GET` | :material-check: |
| `/modbus/holding-registers` | `GET` / `PUT` | :material-check: |

---

## Resposta ao Exceder o Limite

Quando o cliente ultrapassa o limite permitido, a API responde com:

| Item | Valor |
|----|------|
| Código HTTP | `429 Too Many Requests` |
| Corpo | JSON |
| Acesso Modbus | Não executado |

Exemplo de resposta:

```json
{
  "detail": "Rate limit exceeded"
}
```

!!! warning "Impacto Operacional"
    Requisições bloqueadas não chegam ao CLP, evitando sobrecarga e comportamento imprevisível em dispositivos industriais.

---

## Boas Práticas

* Evitar polling agressivo
* Centralizar leituras quando possível
* Utilizar intervalos fixos e controlados
* Tratar respostas 429 no cliente
* Ajustar limites conforme o tipo de aplicação (Web, SCADA, Mobile)

!!! info "Segurança e Estabilidade"
    O Rate Limit protege não apenas a API, mas também o barramento Modbus e o CLP, garantindo operação segura em ambientes industriais.