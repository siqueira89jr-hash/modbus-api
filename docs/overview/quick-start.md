# Quick Start

Este guia apresenta o **caminho mais rápido** para começar a usar a **Modbus API** com segurança, desde a verificação de saúde até a primeira leitura e escrita.

O objetivo é permitir que você valide a API em **minutos**, sem precisar ler toda a documentação inicialmente.

---

## Pré-requisitos

- API em execução (`uvicorn main:app` ou serviço equivalente)
- Servidor Modbus TCP configurado e acessível
- (Opcional) API Key para operações de escrita

---

## 1️⃣ Verifique a saúde da API e do Modbus

Antes de qualquer operação funcional, valide o estado do sistema.

```bash
curl -X GET http://127.0.0.1:8000/health/modbus
```

Resposta esperada:

```json
{
  "ok": true,
  "connected": true
}
```

✔️ Se `connected = true`, a API está pronta para operar.

---

## 2️⃣ Leia um Discrete Input (entrada digital)

Discrete Inputs são **somente leitura** e ideais para o primeiro teste.

```bash
curl -X GET "http://127.0.0.1:8000/modbus/discrete-inputs?addr=0&count=1"
```

Resposta típica:

```json
{
  "addr": 0,
  "count": 1,
  "values": [true]
}
```

---

## 3️⃣ Leia uma Coil (saída digital)

```bash
curl -X GET "http://127.0.0.1:8000/modbus/coils?addr=0&count=1"
```

---

## 4️⃣ Escreva uma Coil (requer API Key)

⚠️ Escrita altera o estado do processo.

```bash
curl -X PUT "http://127.0.0.1:8000/modbus/coil?addr=0" \
  -H "X-API-Key: SUA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"value": true}'
```

Resposta:

```json
{
  "ok": true
}
```

---

## 5️⃣ Leia um valor tipado (Input Register)

Leitura de um valor analógico interpretado automaticamente.

```bash
curl -X GET "http://127.0.0.1:8000/modbus/registers/typed?table=input&addr=10&dtype=float32&endian=be"
```

Resposta:

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

## 6️⃣ Escreva um valor tipado (Holding Register)

⚠️ Use apenas para parâmetros documentados do CLP.

```bash
curl -X PUT "http://127.0.0.1:8000/modbus/holding-registers/typed?addr=20&dtype=float32&endian=be" \
  -H "X-API-Key: SUA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"value": 75.0}'
```

---

## Boas Práticas Essenciais

- Sempre consulte o **Health Check** antes de escritas
- Evite polling agressivo
- Separe leitura e escrita no cliente
- Use Typed Registers para evitar erros de endianness
- Nunca escreva em Input Registers

---

## Próximos Passos

- Leia **Conceitos Modbus** para entender endereçamento e tipos
- Consulte a **API Reference** para detalhes completos
- Veja **Examples** para fluxos mais elaborados
- Em produção, utilize HTTPS e controle de acesso

---

> Este Quick Start é intencionalmente curto.  
> Ele não substitui a documentação completa, apenas acelera o primeiro contato.
