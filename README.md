# Modbus API (Industrial-Grade)

API HTTP para **leitura, escrita e operação segura de dispositivos Modbus TCP**, projetada para **ambientes industriais**, com foco em:

- previsibilidade operacional  
- fail-safe  
- separação clara entre leitura, escrita e operação  
- compatibilidade com PLCs e dispositivos reais  
- documentação pública e versionada  

---

## Visão Geral

Esta API atua como um **adaptador entre HTTP e Modbus TCP**, permitindo que aplicações web, sistemas supervisórios, ERPs e serviços externos interajam com equipamentos industriais de forma **controlada e segura**.

---

## Documentação

A documentação completa, incluindo Quick Start, Arquitetura, API Reference, Endpoints Operacionais, Erros e Boas Práticas, está disponível via **GitHub Pages**.

```text
https://siqueira89jr-hash.github.io/modbus-api
```

---

## Estrutura do Projeto

```text
.
├── main.py
├── requirements.txt
├── .env.example
├── README.md
├── mkdocs.yml
├── docs/
│   ├── index.md
│   ├── overview/
│   ├── setup/
│   ├── api/
│   └── operational/
└── .gitignore
```

---

## Configuração

Crie um arquivo `.env` baseado no exemplo fornecido:

```env
MODBUS_API_KEY=changeme

MODBUS_HOST=127.0.0.1
MODBUS_PORT=502
MODBUS_UNIT_ID=1
MODBUS_TIMEOUT=3.0

MODBUS_LOG_FILE=modbus.log
MODBUS_CONSOLE_LOG=0

API_LOG_FILE=api.log
API_LOG_LEVEL=INFO
```

**Nunca versionar o `.env` real.**

---

## Executando a API

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Acessos

- API: http://127.0.0.1:8000  
- Swagger UI: http://127.0.0.1:8000/docs  

---

## Health Check

```http
GET /health/modbus
```

Ideal para Docker, Kubernetes e monitoramento.

---

## Segurança

- Escritas exigem autenticação via `X-API-Key`
- Comparação timing-safe
- Rate limit antes do acesso Modbus
- CORS restritivo
- HTTPS recomendado em produção

---

## Endpoints Operacionais

- `POST /modbus/close`
- `POST /modbus/reconnect`

---

## Docker

```bash
docker build -t modbus-api .

docker run -d \
  -p 8000:8000 \
  --env-file .env \
  modbus-api
```

---

## Licença

Este projeto é distribuído sob a licença **MIT**, permitindo uso comercial e industrial sem restrições.

---

**Projeto pensado para chão de fábrica, não apenas para laboratório.**

## Autor

Jocivaldo Siqueira da Silva Júnior