# main.py
import math
import os
from contextlib import asynccontextmanager
from typing import List, Optional, Union, Literal, Annotated

from fastapi import FastAPI, HTTPException, Query, Path, Depends, Header, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from pyModbusTCPtools import ModbusTCPResiliente, Endian, ModbusDataType

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

import hmac

from dotenv import load_dotenv

import logging
from logging.handlers import RotatingFileHandler

load_dotenv()

API_LOG_FILE = os.getenv("API_LOG_FILE", "api.log")
API_LOG_LEVEL = os.getenv("API_LOG_LEVEL", "INFO").upper()
API_LOG_MAX_BYTES = int(os.getenv("API_LOG_MAX_BYTES", 1_000_000))
API_LOG_BACKUP_COUNT = int(os.getenv("API_LOG_BACKUP_COUNT", 3))

api_logger = logging.getLogger("ModbusAPI")
api_logger.setLevel(getattr(logging, API_LOG_LEVEL, logging.INFO))

handler = RotatingFileHandler(
    API_LOG_FILE,
    maxBytes=API_LOG_MAX_BYTES,
    backupCount=API_LOG_BACKUP_COUNT
)

API_KEY = os.getenv("MODBUS_API_KEY")

if not API_KEY:
    raise RuntimeError("MODBUS_API_KEY não configurada no ambiente")


def validate_api_key(
    request: Request,
    x_api_key: str = Header(..., alias="X-API-Key"),
):
    client_ip = request.client.host if request.client else "unknown"

    if not (API_KEY and hmac.compare_digest(x_api_key, API_KEY)):
        api_logger.warning(
            f"AUTH failed invalid API key ip={client_ip} path={request.url.path}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

def rate_limit_key(request: Request):
    api_key = request.headers.get("X-API-Key")
    ip = get_remote_address(request)
    return f"{api_key or 'no-key'}:{ip}"

# Config Modbus
MODBUS_HOST = os.getenv("MODBUS_HOST", "127.0.0.1")
MODBUS_PORT = int(os.getenv("MODBUS_PORT", 502))
MODBUS_UNIT_ID = int(os.getenv("MODBUS_UNIT_ID", 1))
MODBUS_TIMEOUT = float(os.getenv("MODBUS_TIMEOUT", 3.0))
MODBUS_PING_ADDR = int(os.getenv("MODBUS_PING_ADDR", 1))
MODBUS_PING_COUNT = int(os.getenv("MODBUS_PING_COUNT", 1))

# Logging opcional do client Modbus
MODBUS_LOG_FILE = os.getenv("MODBUS_LOG_FILE", "modbus.log")
MODBUS_CONSOLE_LOG = os.getenv("MODBUS_CONSOLE_LOG", "0")


# Criar o limiter global
limiter = Limiter(key_func=rate_limit_key)


class HealthResponse(BaseModel):
    ok: bool
    connected: bool
    host: str
    port: int
    unit_id: int
    failure_count: int
    current_retry_delay: float

class WriteSingleCoilRequest(BaseModel):
    value: bool = Field(..., description="Valor booleano a escrever na coil")

class WriteMultipleCoilsRequest(BaseModel):
    values: List[bool] = Field(..., min_length=1, description="Lista de booleans a escrever a partir do addr")

class ReadBitsResponse(BaseModel):
    addr: int
    count: int
    values: List[bool]

class WriteResponse(BaseModel):
    ok: bool

class ReadRegistersResponse(BaseModel):
    addr: int
    count: int
    values: List[int]  # UINT16 (0..65535)

class WriteSingleRegisterRequest(BaseModel):
    value: int = Field(..., ge=0, le=65535, description="Valor UINT16 (0..65535)")

class WriteMultipleRegistersRequest(BaseModel):
    values: List[int] = Field(..., min_length=1, description="Lista de UINT16 (0..65535)")

class WriteReadMultipleRegistersRequest(BaseModel):
    write_addr: int = Field(..., ge=0)
    write_values: List[int] = Field(..., min_length=1)
    read_addr: int = Field(..., ge=0)
    read_count: int = Field(1, ge=1, le=125)

class TypedValueResponse(BaseModel):
    table: str
    addr: int
    dtype: str
    endian: Optional[str] = None
    value: Union[int, float]

class TypedWriteValue(BaseModel):
    value: Union[int, float] = Field(..., description="Valor a escrever")

class TypedReadRequest(BaseModel):
    table: Literal["holding", "input"] = Field(..., description="Tabela de registradores: holding ou input")
    addr: int = Field(..., ge=0, description="Endereço inicial (0-based)")
    dtype: ModbusDataType = Field(..., description="Tipo (uint16/int16/uint32/int32/uint64/int64/float32/float64)")
    endian: Optional[Endian] = Field(
        Endian.BE,
        description=(
            "Ordem de words/bytes para tipos 32/64 bits (be/le/be_swap/le_swap). "
            "Se dtype for uint16 ou int16, este campo é ignorado."
        ),
    )

class TypedWriteRequest(BaseModel):
    dtype: ModbusDataType = Field(..., description="Tipo (uint16/int16/uint32/int32/uint64/int64/float32/float64)")
    endian: Optional[Endian] = Field(
        Endian.BE,
        description=(
            "Ordem de words/bytes para tipos 32/64 bits (be/le/be_swap/le_swap). "
            "Se dtype for uint16 ou int16, este campo é ignorado."
        ),
    )
    value: Union[int, float] = Field(..., description="Valor a escrever (int para inteiros; float para float32/float64)")

def validate_typed_value(dtype: ModbusDataType, value: int) -> None:
    v = int(value)

    if dtype.is_float:
        raise HTTPException(422, "Tipo float não deve cair em validate_typed_value")

    bits = dtype.bits
    if dtype.signed:
        min_v = -(2 ** (bits - 1))
        max_v = (2 ** (bits - 1)) - 1
    else:
        min_v = 0
        max_v = (2 ** bits) - 1

    if not (min_v <= v <= max_v):
        raise HTTPException(422, f"{dtype.value.upper()} fora do range ({min_v}..{max_v})")

def validate_float_value(value: float) -> None:
    v = float(value)
    if math.isnan(v) or math.isinf(v):
        raise HTTPException(status_code=422, detail="FLOAT inválido: NaN/Inf não permitido")

# App state
def _build_modbus_client() -> ModbusTCPResiliente:
    return ModbusTCPResiliente(
        host=MODBUS_HOST,
        port=MODBUS_PORT,
        unit_id=MODBUS_UNIT_ID,
        timeout=MODBUS_TIMEOUT,
        ping_addr=MODBUS_PING_ADDR,
        ping_count=MODBUS_PING_COUNT,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    api_logger.info("API iniciando")
    app.state.modbus = _build_modbus_client()
    # Opcional: valida conexão no startup (não bloqueia seu serviço, apenas tenta)
    try:
        app.state.modbus.is_connected()
    except Exception:
        pass
    yield
    api_logger.info("API finalizando")
    try:
        app.state.modbus.close()
    except Exception:
        pass


app = FastAPI(
    title="Modbus API",
    version="0.1.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
CORS_ALLOW_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "")
cors_origins = [o.strip() for o in CORS_ALLOW_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["X-API-Key", "Content-Type"],
)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    client_ip = request.client.host if request.client else "unknown"
    path = request.url.path

    api_logger.warning(
        f"RATE LIMIT exceeded path={path} ip={client_ip}"
    )

    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit excedido. Aguarde antes de tentar novamente."
        },
    )

def get_modbus(app: FastAPI) -> ModbusTCPResiliente:
    mb = getattr(app.state, "modbus", None)
    if mb is None:
        raise HTTPException(status_code=500, detail="Cliente Modbus não inicializado")
    return mb

@app.get(
    "/health/modbus",
    response_model=HealthResponse,
    summary="Modbus connection status",
    description="Verifica o estado da conexão Modbus TCP e retorna informações de conectividade.",
)
def health_modbus(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    mb = get_modbus(app)

    try:
        connected = bool(mb.is_connected())
    except Exception as e:
        api_logger.error(
            f"HEALTH modbus FAILED exception={e} ip={client_ip}"
        )
        connected = False

    # Log apenas se estiver desconectado
    if not connected:
        api_logger.error(
            f"HEALTH modbus NOT_CONNECTED host={MODBUS_HOST} port={MODBUS_PORT} unit={MODBUS_UNIT_ID} ip={client_ip}"
        )

    return HealthResponse(
        ok=True,
        connected=connected,
        host=MODBUS_HOST,
        port=MODBUS_PORT,
        unit_id=MODBUS_UNIT_ID,
        failure_count=int(getattr(mb, "failure_count", 0)),
        current_retry_delay=float(getattr(mb, "current_retry_delay", 0.0)),
    )


@app.post(
    "/modbus/close", 
    response_model=WriteResponse,
    dependencies=[Depends(validate_api_key)],
    summary="Close Modbus connection",
    description="Fecha manualmente a conexão Modbus TCP ativa.",
)
@limiter.limit("1/second")
def modbus_close(request: Request):
    client_ip = request.client.host if request.client else "unknown"

    # 1 Intenção
    api_logger.warning(
        f"MODBUS CLOSE requested ip={client_ip}"
    )

    mb = get_modbus(app)
    try:
        mb.close()

        # 2 Sucesso
        api_logger.info(
            f"MODBUS CLOSE OK ip={client_ip}"
        )
        return WriteResponse(ok=True)

    except Exception as e:
        # 3 Falha
        api_logger.error(
            f"MODBUS CLOSE FAILED ip={client_ip} err={e}"
        )
        raise HTTPException(
            status_code=500,
            detail="Falha ao fechar conexão Modbus"
        )


@app.post(
    "/modbus/reconnect",
    dependencies=[Depends(validate_api_key)], 
    response_model=HealthResponse,
    summary="Reconnect Modbus connection",
    description="Força a reconexão com o servidor Modbus TCP.",
)
@limiter.limit("1/second")
def modbus_reconnect(request: Request):
    client_ip = request.client.host if request.client else "unknown"

    # 1 Intenção
    api_logger.warning(
        f"MODBUS RECONNECT requested ip={client_ip}"
    )

    mb = get_modbus(app)

    # Fecha conexão atual (se existir)
    try:
        mb.close()
        api_logger.info(
            f"MODBUS RECONNECT previous connection closed ip={client_ip}"
        )
    except Exception:
        api_logger.warning(
            f"MODBUS RECONNECT no active connection to close ip={client_ip}"
        )

    # Tenta reconectar
    try:
        connected = bool(mb.is_connected())

        if connected:
            api_logger.info(
                f"MODBUS RECONNECT OK ip={client_ip}"
            )
        else:
            api_logger.error(
                f"MODBUS RECONNECT FAILED ip={client_ip}"
            )

    except Exception as e:
        api_logger.error(
            f"MODBUS RECONNECT ERROR ip={client_ip} err={e}"
        )
        connected = False

    return HealthResponse(
        ok=True,
        connected=connected,
        host=MODBUS_HOST,
        port=MODBUS_PORT,
        unit_id=MODBUS_UNIT_ID,
        failure_count=int(getattr(mb, "failure_count", 0)),
        current_retry_delay=float(getattr(mb, "current_retry_delay", 0.0)),
    )


@app.get(
    "/modbus/coils",
    response_model=ReadBitsResponse,
    summary="List coils",
    description="Lê coils a partir de um endereço inicial utilizando Modbus TCP.",
)
def read_coils(
    request: Request,
    addr: int = Query(..., ge=0, description="Endereço inicial (0-based)"),
    count: int = Query(1, ge=1, le=2000, description="Quantidade de coils"),
):
    client_ip = request.client.host if request.client else "unknown"
    mb = get_modbus(app)

    # 1 Intenção
    api_logger.info(
        f"READ coils requested addr={addr} count={count} ip={client_ip}"
    )

    values = mb.read_coils_safe(addr, count)

    # 2 Falha
    if values is None:
        api_logger.error(
            f"READ coils FAILED addr={addr} count={count} ip={client_ip}"
        )
        raise HTTPException(
            status_code=503,
            detail="Falha ao ler coils (conexão/endereçamento/timeout)"
        )

    # 3 Sucesso (não logar valores)
    api_logger.info(
        f"READ coils OK addr={addr} count={count} ip={client_ip}"
    )

    return ReadBitsResponse(
        addr=addr,
        count=count,
        values=[bool(v) for v in values],
    )

@app.get(
    "/modbus/discrete-inputs",
    response_model=ReadBitsResponse,
    summary="List discrete inputs",
    description="Lê discrete inputs a partir de um endereço inicial utilizando Modbus TCP.",
)
def read_discrete_inputs(
    request: Request,
    addr: int = Query(..., ge=0, description="Endereço inicial (0-based)"),
    count: int = Query(1, ge=1, le=2000, description="Quantidade de discrete inputs"),
):
    client_ip = request.client.host if request.client else "unknown"
    mb = get_modbus(app)

    # 1 Intenção
    api_logger.info(
        f"READ discrete_inputs requested addr={addr} count={count} ip={client_ip}"
    )

    values = mb.read_discrete_inputs_safe(addr, count)

    # 2 Falha
    if values is None:
        api_logger.error(
            f"READ discrete_inputs FAILED addr={addr} count={count} ip={client_ip}"
        )
        raise HTTPException(
            status_code=503,
            detail="Falha ao ler discrete inputs (conexão/endereçamento/timeout)"
        )

    # 3 Sucesso
    api_logger.info(
        f"READ discrete_inputs OK addr={addr} count={count} ip={client_ip}"
    )

    return ReadBitsResponse(
        addr=addr,
        count=count,
        values=[bool(v) for v in values],
    )

@app.put(
    "/modbus/coil",
    response_model=WriteResponse,
    dependencies=[Depends(validate_api_key)],
    summary="Update single coil",
    description="Escreve o valor de uma única coil no endereço informado utilizando Modbus TCP.",
)
@limiter.limit("5/second")
def write_single_coil(
    request: Request,
    addr: int = Query(..., ge=0, description="Endereço da coil (0-based)"),
    payload: WriteSingleCoilRequest = ...,
):
    client_ip = request.client.host if request.client else "unknown"

    # 1 LOG DA INTENÇÃO (antes de escrever)
    api_logger.warning(
        f"WRITE single coil requested addr={addr} value={payload.value} ip={client_ip}"
    )

    mb = get_modbus(app)
    ok = bool(mb.write_single_coil_safe(addr, payload.value))

    # 2 LOG DE FALHA
    if not ok:
        api_logger.error(
            f"WRITE single coil FAILED addr={addr} ip={client_ip}"
        )
        raise HTTPException(
            status_code=503,
            detail="Falha ao escrever single coil (conexão/endereçamento/timeout)"
        )

    # 3 LOG DE SUCESSO
    api_logger.info(
        f"WRITE single coil OK addr={addr} ip={client_ip}"
    )

    return WriteResponse(ok=True)

@app.put(
    "/modbus/coils",
    response_model=WriteResponse,
    dependencies=[Depends(validate_api_key)],
    summary="Update multiple coils",
    description="Escreve múltiplas coils consecutivas a partir de um endereço inicial utilizando Modbus TCP.",
)
@limiter.limit("2/second")
def write_multiple_coils(
    request: Request,
    addr: int = Query(..., ge=0, description="Endereço inicial (0-based)"),
    count: int = Query(1, ge=1, le=2000, description="Quantidade de coils a escrever"),
    payload: WriteMultipleCoilsRequest = ...,
):
    client_ip = request.client.host if request.client else "unknown"

    # 1 Validação + log
    if count != len(payload.values):
        api_logger.warning(
            f"WRITE multiple coils INVALID count addr={addr} count={count} values_len={len(payload.values)} ip={client_ip}"
        )
        raise HTTPException(
            status_code=422,
            detail=f"count ({count}) deve ser igual ao tamanho de values ({len(payload.values)})",
        )

    # 2 Intenção
    api_logger.warning(
        f"WRITE multiple coils requested addr={addr} count={count} ip={client_ip}"
    )

    mb = get_modbus(app)
    ok = bool(mb.write_multiple_coils_safe(addr, payload.values))

    # 3 Falha
    if not ok:
        api_logger.error(
            f"WRITE multiple coils FAILED addr={addr} count={count} ip={client_ip}"
        )
        raise HTTPException(
            status_code=503,
            detail="Falha ao escrever multiple coils (conexão/endereçamento/timeout)"
        )

    # 4 Sucesso
    api_logger.info(
        f"WRITE multiple coils OK addr={addr} count={count} ip={client_ip}"
    )

    return WriteResponse(ok=True)


@app.post(
    "/modbus/write-read-multiple-registers", 
    response_model=ReadRegistersResponse,
    dependencies=[Depends(validate_api_key)],
    summary="Write and read holding registers",
    description="Escreve registradores holding e, em seguida, realiza a leitura de registradores utilizando Modbus TCP.",
)
@limiter.limit("1/second")
def write_read_multiple_registers(
    request: Request,
    payload: WriteReadMultipleRegistersRequest,
):
    client_ip = request.client.host if request.client else "unknown"

    # 1 Validações + log
    if len(payload.write_values) > 123:
        api_logger.warning(
            f"WRITE/READ INVALID write_values_len={len(payload.write_values)} ip={client_ip}"
        )
        raise HTTPException(422, "write_values muito grande (limite prático típico ~123 regs)")

    if payload.read_count > 125:
        api_logger.warning(
            f"WRITE/READ INVALID read_count={payload.read_count} ip={client_ip}"
        )
        raise HTTPException(422, "read_count muito grande (limite típico 125 regs)")

    for v in payload.write_values:
        if not (0 <= int(v) <= 0xFFFF):
            api_logger.warning(
                f"WRITE/READ INVALID value={v} ip={client_ip}"
            )
            raise HTTPException(422, f"Valor fora do range UINT16: {v}")

    # 2 Intenção
    api_logger.warning(
        f"WRITE/READ requested write_addr={payload.write_addr} write_count={len(payload.write_values)} "
        f"read_addr={payload.read_addr} read_count={payload.read_count} ip={client_ip}"
    )

    mb = get_modbus(app)
    regs = mb.write_read_multiple_registers_safe(
        payload.write_addr,
        [int(v) for v in payload.write_values],
        payload.read_addr,
        payload.read_count,
    )

    # 3 Falha
    if regs is None:
        api_logger.error(
            f"WRITE/READ FAILED write_addr={payload.write_addr} read_addr={payload.read_addr} ip={client_ip}"
        )
        raise HTTPException(
            status_code=503,
            detail="Falha em Write/Read Multiple Registers (conexão/endereçamento/timeout)"
        )

    # 4 Sucesso
    api_logger.info(
        f"WRITE/READ OK write_addr={payload.write_addr} read_addr={payload.read_addr} "
        f"read_count={payload.read_count} ip={client_ip}"
    )

    return ReadRegistersResponse(
        addr=payload.read_addr,
        count=payload.read_count,
        values=[int(r) for r in regs],
    )

@app.get(
    "/modbus/registers/typed",
    response_model=TypedValueResponse,
    summary="Read typed registers",
    description="Lê registradores holding ou input interpretando o valor conforme o tipo de dado informado.",
)
def read_registers_typed(
    request: Request,
    table: Literal["holding", "input"] = Query(..., description="Tabela de registradores"),
    addr: int = Query(..., ge=0, description="Endereço inicial (0-based)"),
    dtype: ModbusDataType = Query(..., description="Tipo de dado"),
    endian: Endian = Query(Endian.BE, description="Endianness (apenas para 32/64 bits)"),
):
    client_ip = request.client.host if request.client else "unknown"
    mb = get_modbus(app)

    # endian irrelevante para 16 bits
    if dtype.registers == 1:
        en = Endian.BE
        endian_out: Optional[str] = None
    else:
        en = endian
        endian_out = endian.value

    api_logger.info(
        f"READ typed requested table={table} addr={addr} dtype={dtype.value} endian={en.value} ip={client_ip}"
    )

    if table == "holding":
        val = mb.read_holding_typed_safe(addr, dtype, en)
    else:
        val = mb.read_input_typed_safe(addr, dtype, en)

    if val is None:
        api_logger.error(
            f"READ typed FAILED table={table} addr={addr} dtype={dtype.value} ip={client_ip}"
        )
        raise HTTPException(
            status_code=503,
            detail="Falha ao ler registrador typed (conexão/endereçamento/timeout)",
        )

    out_val: Union[int, float] = float(val) if dtype.is_float else int(val)

    api_logger.info(
        f"READ typed OK table={table} addr={addr} dtype={dtype.value} value={out_val} ip={client_ip}"
    )

    return TypedValueResponse(
        table=table,
        addr=addr,
        dtype=dtype.value,
        endian=endian_out,
        value=out_val,
    )

@app.put(
    "/modbus/holding-registers/typed",
    response_model=WriteResponse,
    dependencies=[Depends(validate_api_key)],
    summary="Write typed holding registers",
    description="Escreve um valor em registradores holding utilizando tipo de dado definido.",
)
@limiter.limit("1/second")
def write_holding_register_typed(
    request: Request,
    addr: int = Query(..., ge=0, description="Endereço inicial (0-based)"),
    dtype: ModbusDataType = Query(..., description="Tipo de dado"),
    endian: Endian = Query(Endian.BE, description="Endianness (apenas para 32/64 bits)"),
    payload: TypedWriteValue = ...,
):
    client_ip = request.client.host if request.client else "unknown"
    mb = get_modbus(app)

    en = Endian.BE if dtype.registers == 1 else endian

    # 1 Intenção
    api_logger.warning(
        f"WRITE typed requested addr={addr} dtype={dtype.value} endian={en.value} value={payload.value} ip={client_ip}"
    )

    try:
        if dtype.is_float:
            validate_float_value(float(payload.value))
            ok = bool(
                mb.write_holding_typed_safe(addr, float(payload.value), dtype, en)
            )
        else:
            if isinstance(payload.value, float) and not float(payload.value).is_integer():
                api_logger.warning(
                    f"WRITE typed INVALID integer value={payload.value} ip={client_ip}"
                )
                raise HTTPException(
                    status_code=422,
                    detail="Valor inteiro inválido: não pode ter casas decimais"
                )

            validate_typed_value(dtype, int(payload.value))
            ok = bool(
                mb.write_holding_typed_safe(addr, int(payload.value), dtype, en)
            )

    except HTTPException:
        raise

    except Exception as e:
        api_logger.error(
            f"WRITE typed EXCEPTION addr={addr} dtype={dtype.value} error={e} ip={client_ip}"
        )
        raise HTTPException(500, "Erro interno ao escrever registrador typed")

    # 2 Falha
    if not ok:
        api_logger.error(
            f"WRITE typed FAILED addr={addr} dtype={dtype.value} ip={client_ip}"
        )
        raise HTTPException(
            status_code=503,
            detail="Falha ao escrever registrador typed (conexão/endereçamento/timeout)"
        )

    # 3 Sucesso
    api_logger.info(
        f"WRITE typed OK addr={addr} dtype={dtype.value} value={payload.value} ip={client_ip}"
    )

    return WriteResponse(ok=True)

