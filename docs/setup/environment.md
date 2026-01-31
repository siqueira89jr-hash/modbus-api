# Environment Variables (.env)

A **Modbus API** é configurada exclusivamente por **variáveis de ambiente**, seguindo boas práticas de segurança, portabilidade e operação em ambientes industriais (OT/IT).

O uso de um arquivo `.env` é **fortemente recomendado**, especialmente em ambientes de desenvolvimento, testes e produção controlada.

!!! warning "Importante"
    O arquivo `.env` **não deve ser versionado** em repositórios públicos ou privados.  
    Utilize `.gitignore` para garantir que ele não seja incluído no controle de versão.

---

## Visão Geral

As variáveis de ambiente permitem configurar:

- Autenticação da API (API Key)
- Conexão Modbus TCP
- Parâmetros de timeout e teste de conectividade
- Comportamento de logging

A API carrega essas variáveis automaticamente no startup.

---

## Exemplo Completo de Arquivo `.env`

```env
# ==========================================
# Modbus API - Environment Configuration
# ==========================================

# ------------------------------------------
# API Security
# ------------------------------------------
# Chave usada para autenticar operações de escrita
MODBUS_API_KEY=CHANGE_ME_SUPER_SECRET_KEY

# ------------------------------------------
# Modbus TCP Connection
# ------------------------------------------
# Endereço IP ou hostname do servidor Modbus
MODBUS_HOST=192.168.0.10

# Porta TCP do servidor Modbus (default: 502)
MODBUS_PORT=502

# Unit Identifier (Slave ID)
MODBUS_UNIT_ID=1

# Timeout de comunicação Modbus (segundos)
MODBUS_TIMEOUT=3.0

# Endereço utilizado para teste de conectividade
MODBUS_PING_ADDR=1

# Quantidade de tentativas de ping no startup
MODBUS_PING_COUNT=1

# ------------------------------------------
# API Logging
# ------------------------------------------
# Arquivo de log da API
API_LOG_FILE=api.log

# Nível de log (INFO, WARNING, ERROR)
API_LOG_LEVEL=INFO

# ------------------------------------------
# Modbus Client Logging (Opcional)
# ------------------------------------------
# Arquivo de log do cliente Modbus
MODBUS_LOG_FILE=modbus.log

# Habilita log no console (0 = desabilitado, 1 = habilitado)
MODBUS_CONSOLE_LOG=0
```

---

## Variáveis de Ambiente Disponíveis

### Segurança

| Variável | Obrigatória | Descrição |
|--------|-------------|-----------|
| `MODBUS_API_KEY` | ✅ | Chave usada para autenticar endpoints de **escrita** |

---

### 🔌 Conexão Modbus TCP

| Variável | Obrigatória | Descrição |
|--------|-------------|-----------|
| `MODBUS_HOST` | ✅ | Endereço IP ou hostname do servidor Modbus |
| `MODBUS_PORT` | ❌ | Porta TCP do Modbus (default: `502`) |
| `MODBUS_UNIT_ID` | ❌ | Unit Identifier (Slave ID) |
| `MODBUS_TIMEOUT` | ❌ | Timeout de comunicação em segundos |
| `MODBUS_PING_ADDR` | ❌ | Endereço usado para teste de conectividade |
| `MODBUS_PING_COUNT` | ❌ | Número de tentativas de ping no startup |

---

### Logging

| Variável | Obrigatória | Descrição |
|--------|-------------|-----------|
| `API_LOG_FILE` | ❌ | Caminho do arquivo de log da API |
| `API_LOG_LEVEL` | ❌ | Nível de log (`INFO`, `WARNING`, `ERROR`) |
| `MODBUS_LOG_FILE` | ❌ | Arquivo de log do cliente Modbus |
| `MODBUS_CONSOLE_LOG` | ❌ | Habilita log Modbus no console (`0` ou `1`) |

---

## API Key e Rotação

A **Modbus API não gera, não gerencia e não rotaciona API Keys dinamicamente**.

A API apenas **valida** a chave configurada no ambiente.

### Como realizar a rotação da API Key

A rotação da API Key é uma **operação administrativa**, realizada fora da API:

1. Gere uma nova chave segura
2. Atualize o valor da variável `MODBUS_API_KEY`
3. Reinicie o serviço da API

Exemplo em ambiente Linux:

```bash
export MODBUS_API_KEY="NOVA_CHAVE_SUPER_SEGURA"
systemctl restart modbus-api
```

!!! info "Modelo de Segurança"
    Esse modelo é intencional e adequado para ambientes industriais, pois evita a criação de superfícies de ataque adicionais via endpoints HTTP.

---

## Boas Práticas

- Nunca versionar o arquivo `.env`
- Utilizar permissões restritas no arquivo (`chmod 600`)
- Armazenar segredos fora do código
- Utilizar HTTPS em produção
- Rotacionar a API Key periodicamente
- Reiniciar a API após qualquer alteração de ambiente

---

## Observações Operacionais

- As variáveis de ambiente são carregadas **no startup**
- Alterações no `.env` exigem **reinício da API**
- Em ambientes Docker ou systemd, recomenda-se definir as variáveis diretamente no serviço

---

## Conclusão

O uso correto das variáveis de ambiente garante que a **Modbus API** seja:

- Segura
- Portável
- Fácil de operar
- Adequada para ambientes industriais críticos

A configuração via `.env` é a base para uma operação previsível e controlada da API.
