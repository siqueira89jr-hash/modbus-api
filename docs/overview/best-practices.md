# Limitações e Boas Práticas

Esta página descreve **limitações técnicas** e **boas práticas recomendadas** para o uso seguro e previsível da **Modbus API** em ambientes industriais.

Seguir estas orientações é essencial para proteger o **CLP**, o **barramento Modbus** e o **processo físico**.

---

## Princípio Fundamental

> **O CLP nunca deve pagar o preço de um cliente mal comportado.**

Toda decisão de uso da API deve priorizar:
- Estabilidade do processo
- Previsibilidade operacional
- Segurança elétrica, mecânica e lógica

---

## Limitações Técnicas

### Limites de Leitura

| Recurso | Limite |
|------|--------|
| Coils | até 2000 bits por requisição |
| Discrete Inputs | até 2000 bits por requisição |
| Holding Registers | limites típicos Modbus (≈125 regs por leitura) |
| Input Registers | limites típicos Modbus (≈125 regs por leitura) |

Leituras acima desses valores são rejeitadas para evitar:
- Timeouts
- Fragmentação excessiva
- Sobrecarga do CLP

---

### Limites de Escrita

- Escrita em coils e holding registers é **explicitamente limitada**
- Escritas em massa devem ser evitadas
- Escrita cíclica (polling com PUT) **não é permitida**

---

### Rate Limit

- Todos os endpoints são protegidos por rate limit
- O limite atua **antes** de qualquer acesso ao Modbus
- Requisições excedentes não chegam ao CLP

Consulte a página **Rate Limit** para detalhes.

---

## Boas Práticas de Leitura

### Prefira leituras agregadas

Ao invés de múltiplas leituras pequenas:

```text
GET coil 0
GET coil 1
GET coil 2
```

```text
GET coils addr=0 count=3
```

---

### Evite polling agressivo

- Leituras contínuas devem ter intervalo controlado
- Intervalos muito curtos causam:
  - Sobrecarga de CPU no CLP
  - Latência
  - Perda de pacotes

Em geral, **100–500 ms** é suficiente para supervisão.

---

## Boas Práticas de Escrita

### Escrita não é supervisão

- Escrita deve ser **evento**, não loop
- Nunca use escrita como mecanismo de controle contínuo

---

### Sempre valide antes de escrever

Antes de qualquer escrita:
1. Consulte o **Health Check**
2. Valide limites de valor
3. Confirme se o registrador é documentado

---

### Use Typed Registers

Evite escrita manual de múltiplos registers.

```text
Escrever words manualmente
```

```text
PUT /modbus/holding-registers/typed
```

Typed Registers:
- Evitam erros de endianness
- Garantem faixa válida de valores
- Reduzem risco operacional

---

## Separação de Responsabilidades

### Leitura ≠ Escrita

- Leitura é aberta por padrão
- Escrita exige autenticação (`X-API-Key`)
- Clientes devem separar claramente essas responsabilidades

---

### Nunca escreva em Input Registers

- Input Registers são **somente leitura**
- Escrita neles é conceitualmente incorreta
- A API bloqueia esse tipo de operação

---

## Uso do Health Check

- Sempre consulte o Health antes de comandos críticos
- Health **não executa escrita nem leitura funcional**
- Health indica apenas conectividade básica

---

## Tratamento de Falhas

### Nunca assuma sucesso

- Se a API retornar erro (`4xx` / `5xx`), **assuma falha**
- Nunca continue o fluxo como se a escrita tivesse ocorrido

---

### Trate `503 Service Unavailable`

Esse erro indica:
- CLP offline
- Timeout
- Falha de comunicação

O cliente deve:
- Aguardar
- Tentar novamente após intervalo
- Alertar operador, se necessário

---

## Segurança

- Nunca exponha a API Key no frontend
- Use HTTPS em produção
- Restrinja CORS ao mínimo necessário
- Registre e monitore escritas
