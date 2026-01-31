# Conceitos Modbus

Esta seção apresenta os conceitos fundamentais do protocolo Modbus e como eles são aplicados na Modbus API, abstraindo detalhes de baixo nível e expondo uma interface HTTP segura, tipada e padronizada.

---

## O que é Modbus

Modbus é um protocolo industrial amplamente utilizado para comunicação entre dispositivos de automação, como:

* CLPs
* IHMs
* Inversores de frequência
* Sensores
* Medidores de energia

!!! info 
    A Modbus API utiliza Modbus TCP, onde a comunicação ocorre sobre TCP/IP, normalmente na porta 502.

---

## Modelo Cliente–Servidor

No contexto do Modbus TCP:

| Papel | Descrição |
|------|----------|
| **Cliente (Master)** | Inicia requisições Modbus |
| **Servidor (Slave)** | Responde às requisições |

Na arquitetura deste projeto:

| Camada | Função |
|--------|--------|
| Modbus API | Cliente Modbus + Servidor HTTP |
| CLP / Dispositivo| Servidor Modbus TCP |

A API atua como um gateway, permitindo que sistemas modernos se comuniquem com dispositivos industriais legados.

---

## Tabelas Modbus (Memória)

O protocolo Modbus define quatro tabelas principais, cada uma com propósito e regras próprias.

| Tabela | Tipo | Acesso | Uso |
|------|------|--------|----|
| **Coils** | Bit | Read/Write | Saídas digitais |
| **Discrete Inputs** | Bit | Only Read | Entradas digitais |
| **Holding Registers** | 16 bits | Read/Write | Registradores gerais |
| **Input Registers** | 16 bits | Only Read | Registradores de leitura |

A Modbus API expõe endpoints REST separados para cada uma dessas tabelas.

---

## Endereçamento (0-based)

Nesta API, todos os endereços são 0-based.

| Endereço Informado | Significado |
|--------------------|-------------|
| addr = 0 | Primeiro registrador ou coil |
| addr = 1 | Segundo registrador ou coil |

!!! warning "Atenção" 
    Alguns fabricantes utilizam documentação 1-based. Ajuste o endereço conforme necessário.

---

## Limites Práticos do Protocolo

Embora o protocolo permita leituras extensas, existem limites práticos para evitar falhas de comunicação.

| Operação | Limite |
|--------|--------|
| Leitura de Coils | até 2000 bits |
| Leitura de Registers | até 125 registers |
| Escrita múltipla | até 123 registers |

Esses limites seguem boas práticas industriais e evitam timeouts e sobrecarga do dispositivo.

---

## Tipos de Dados Estendidos (Typed Registers)

O Modbus trabalha nativamente com registradores de 16 bits, mas a Modbus API adiciona uma camada de interpretação tipada.

| Tipo | Bits | Registradores utilizados |
|------|------|----------------------|
| `int16` / `uint16` | 16 | 1 |
| `int32` / `uint32` | 32 | 2 |
| `int64` / `uint64` | 64 | 4 |
| `float32` | 32 | 2 |
| `float64` | 64 | 4 |

Esses tipos são definidos via o enum ModbusDataType e tratados automaticamente pela API.

---

## Endianness (Ordem de Words e Bytes)

Para tipos maiores que 16 bits, a ordem dos dados pode variar entre fabricantes.

A API suporta explicitamente:

| Endian | Descrição |
|------|----------|
| `be` | Big-endian (padrão Modbus) |
| `le` | Little-endian (word swap) |
| `be_swap` | Big-endian com byte swap |
| `le_swap` | Little-endian com byte swap |

!!! info "Boas práticas"
    - Para a maioria dos CLPs, utilize `be`
    - Consulte sempre o manual do fabricante
    - Para tipos de 16 bits (`int16`, `uint16`), o endianness é ignorado

---

## Conversão de Dados

A conversão entre registradores Modbus e valores tipados é feita automaticamente pela camada:

**ModbusTCPResiliente:**

* Combinar registradores
* Aplicar endianness
* Converter para inteiro ou float
* Validar tamanho e tipo

!!! info "Camada central"
    Toda conversão e validação Modbus ocorre exclusivamente nesta camada.
    Falhas nessa etapa geram erros explícitos, evitando dados inconsistentes.

---

## Tratamento de Erros Modbus

A API diferencia claramente os tipos de erro, permitindo respostas HTTP coerentes.

| Categoria | Exemplo |
|---------|---------|
| **Erro de Conexão** | Timeout, CLP offline |
| **Erro de Protocolo** | Illegal Data Address |
| **Erro de Leitura** | Falha ao ler registradores |
| **Erro de Escrita** | Falha ao escrever |
| **Erro de Conversão** | Tipo ou endianness inválido |

!!! info "Mapeamento HTTP"
    Todos os erros Modbus são convertidos em **códigos HTTP apropriados**  
    (`4xx` para erro de requisição, `5xx` para falhas internas ou de comunicação).

---

## Por que abstrair Modbus com HTTP?

Essa arquitetura permite:

| Benefício | Descrição |
|---------|-----------|
| **Integração moderna** | IA, Web, Mobile, SCADA, Dashboards |
| **Segurança** | API Key + Rate limit |
| **Padronização** | JSON + HTTP |
| **Manutenção** | Sem impacto direto no CLP |
| **Escalabilidade** | Evolução independente |

A Modbus API atua como uma fronteira segura e moderna para sistemas industriais.