# Modbus API

Uma **API REST** para comunicação Modbus TCP, projetada para ambientes industriais que exigem robustez, segurança e simplicidade de integração. Esta API atua como uma camada intermediária entre aplicações modernas (Web, Mobile, SCADA, serviços Python) e dispositivos Modbus TCP (CLPs, inversores, sensores), eliminando a necessidade de acesso direto ao protocolo Modbus.

---

## Objetivos

* Facilitar a integração de sistemas modernos com equipamentos Modbus TCP
* Padronizar leitura e escrita de dados industriais via HTTP/JSON
* Garantir confiabilidade mesmo em cenários de falha de comunicação
* Oferecer segurança básica sem complexidade excessiva

---

## Principais Recursos

* Comunicação Modbus TCP Resiliente
* Reconexão automática em caso de falha
* Backoff exponencial configurável
* Detecção ativa de conexão perdida
* Cache de endereços inválidos (evita chamadas repetidas a endereços inexistentes)

---

## Segurança Integrada

* Autenticação via API Key (X-API-Key)
* Comparação segura contra ataques de timing
* Rate limit por API Key ou IP
* CORS configurável

---

## Leitura e Escrita Tipada

### Suporte nativo a tipos de dados industriais

* INT16 / UINT16
* INT32 / UINT32
* INT64 / UINT64
* FLOAT32
* FLOAT64

### Endianness configurável:

* be (Big Endian – padrão Modbus)
* le (Little Endian)
* be_swap (Big Endian com Byte Swap )
* le_swap (Little Endian com Byte Swap )

---

## Operações Modbus

* Escrita / Leitura de Múltiplos Registradores
* Escrita / Leitura de coils
* Leitura de discrete inputs
* Leitura de Holding Registers e Input Registers

---

## Arquitetura

```mermaid
graph LR
    A[Cliente HTTP<br/>Web / App / SCADA] --> B[FastAPI];
    B --> C[ModbusTCPResiliente];
    C --> D[CLP / Dispositivo Modbus TCP];
```

A API abstrai completamente o protocolo Modbus, permitindo que clientes trabalhem apenas com HTTP, JSON e tipos de dados claros.

---

## Quando Usar

* Integração de sistemas web com CLPs
* Dashboards industriais
* Gateways de automação
* APIs industriais internas
* Substituição de acessos diretos Modbus em redes corporativas

---

## Quando NÃO Usar

* Aplicações com requisitos de tempo real estrito
* Ciclos de controle em malha fechada
* Sistemas onde latência HTTP não é aceitável

---

## Documentação Técnica

* Documentação conceitual (MkDocs) → Este site
* Documentação automática da API (Swagger / ReDoc) → Disponível no próprio serviço FastAPI

---

## Tecnologias Utilizadas

1. FastAPI – API REST moderna e performática
2. pyModbusTCPtools – Comunicação Modbus TCP
3. SlowAPI – Rate limit
4. Pydantic – Validação de dados
5. MkDocs + Material – Documentação técnica