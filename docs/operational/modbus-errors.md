# Modbus Errors (Operational)

Este documento descreve **erros específicos relacionados ao protocolo Modbus TCP** e como a API os traduz para **erros HTTP previsíveis**.

O objetivo é permitir que clientes:
- entendam a causa real da falha
- reajam corretamente (retry, fallback, alarme)
- não assumam sucesso quando o estado Modbus é indefinido

---

## Conceito Importante

!!! warning "Erro Modbus ≠ Erro HTTP"
    O protocolo Modbus **não possui semântica HTTP**.  
    A API atua como **adaptador**, convertendo falhas Modbus em códigos HTTP padronizados.

---

## Categorias de Erro Modbus

### Falhas de Comunicação

Incluem:
- servidor Modbus offline
- timeout de resposta
- conexão TCP quebrada
- falha de reconexão

**Comportamento da API**
- Retorna `503 Service Unavailable`
- Nenhuma escrita é assumida como concluída
- Estado interno permanece consistente

```json
{
  "detail": "Falha de comunicação com servidor Modbus"
}
```

---

### Endereço ou Quantidade Inválida

Incluem:
- endereço fora da faixa do dispositivo
- leitura/escrita além do limite permitido
- contagem excessiva de coils/registers

**Comportamento da API**
- Retorna `422 Unprocessable Entity`
- Operação Modbus não é executada

```json
{
  "detail": "Endereço ou quantidade inválida"
}
```

---

### Operação Não Permitida

Incluem:
- tentativa de escrita em `Discrete Inputs`
- escrita sem autenticação
- acesso a endpoint restrito

**Comportamento da API**
- Retorna `401 Unauthorized` ou `403 Forbidden`
- Tentativa é logada como WARNING

```json
{
  "detail": "Operação não permitida"
}
```

---

### Erros de Escrita

Incluem:
- falha ao escrever coil/register
- retorno Modbus indefinido (`None`)
- erro interno do client Modbus

**Comportamento da API**
- Retorna `503 Service Unavailable`
- Escrita nunca é assumida como sucesso

```json
{
  "detail": "Falha ao escrever dados Modbus"
}
```

---

### Erros de Tipo de Dado (Typed Registers)

Incluem:
- overflow de inteiro
- tipo incompatível
- `NaN` ou `Infinity` em float
- endian inválido

**Comportamento da API**
- Retorna `422 Unprocessable Entity`
- Nenhuma operação Modbus é executada

```json
{
  "detail": "Tipo de dado inválido ou fora do range"
}
```

---

## Mapeamento Resumido

| Situação | Código HTTP |
|--------|-------------|
| Falha de comunicação | `503` |
| Timeout | `503` |
| Endereço inválido | `422` |
| Quantidade inválida | `422` |
| Escrita não autorizada | `401 / 403` |
| Tipo de dado inválido | `422` |
| Erro interno inesperado | `500` |

---

## Boas Práticas para Clientes

!!! info "Recomendações"
    - Trate `503` como erro **transitório**
    - Use retry com backoff exponencial
    - Nunca assuma escrita bem-sucedida sem `200 OK`
    - Não faça polling agressivo após falhas
    - Gere alarmes após falhas repetidas

---

## Relação com Outros Documentos

- Consulte **HTTP Errors** para semântica HTTP geral
- Consulte **Rate Limit** para erros de limitação
- Consulte **Modbus Connection** para recuperação manual

