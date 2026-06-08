"""
=============================================================
Serviço P - API Gateway (Python + FastAPI)
=============================================================
Este módulo recebe requisições HTTP/REST do cliente web e as
traduz em chamadas gRPC para os Serviços A e B (Go).

Arquitetura:
  Browser → HTTP → FastAPI (P) → gRPC → Serviço A (Go) [Primos]
                               → gRPC → Serviço B (Go) [Estatísticas]
=============================================================
"""

import os
import time
import asyncio
import grpc
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Importa os stubs gerados pelo protoc
import prime_service_pb2 as prime_pb2
import prime_service_pb2_grpc as prime_pb2_grpc
import stats_service_pb2 as stats_pb2
import stats_service_pb2_grpc as stats_pb2_grpc

# ──────────────────────────────────────────────────────────
# Configuração
# ──────────────────────────────────────────────────────────
SERVICE_A_ADDR = os.getenv("SERVICE_A_ADDR", "service-a:50051")
SERVICE_B_ADDR = os.getenv("SERVICE_B_ADDR", "service-b:50052")

app = FastAPI(
    title="Analisador de Intervalos Numéricos",
    description="API Gateway que orquestra chamadas gRPC aos microserviços A e B",
    version="1.0.0",
)

# ──────────────────────────────────────────────────────────
# Modelos de dados (Pydantic)
# ──────────────────────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    min_val: int
    max_val: int

class AnalyzeResponse(BaseModel):
    min_val: int
    max_val: int
    # Do Serviço A (Primos)
    primes: list[int]
    prime_count: int
    prime_computation_ms: float
    # Do Serviço B (Estatísticas)
    sum: float
    mean: float
    variance: float
    std_dev: float
    count: int
    stats_computation_ms: float
    # Tempo total
    total_time_ms: float

# ──────────────────────────────────────────────────────────
# Endpoints REST
# ──────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve a interface web principal."""
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    """
    Endpoint principal: recebe um intervalo [min, max] e retorna
    primos (Serviço A) + estatísticas (Serviço B) em paralelo.
    """
    if req.min_val > req.max_val:
        req.min_val, req.max_val = req.max_val, req.min_val

    if req.max_val - req.min_val > 500_000:
        raise HTTPException(
            status_code=400,
            detail="Intervalo muito grande (máximo 500.000). Use um intervalo menor."
        )

    total_start = time.time()

    # Chama os dois serviços em paralelo usando asyncio
    try:
        prime_result, stats_result = await asyncio.gather(
            _call_service_a(req.min_val, req.max_val),
            _call_service_b(req.min_val, req.max_val),
        )
    except grpc.RpcError as e:
        raise HTTPException(status_code=503, detail=f"Erro gRPC: {e.details()}")

    total_ms = (time.time() - total_start) * 1000

    return AnalyzeResponse(
        min_val=req.min_val,
        max_val=req.max_val,
        primes=list(prime_result.primes),
        prime_count=prime_result.count,
        prime_computation_ms=prime_result.computation_time_ms,
        sum=stats_result.sum,
        mean=stats_result.mean,
        variance=stats_result.variance,
        std_dev=stats_result.std_dev,
        count=stats_result.count,
        stats_computation_ms=stats_result.computation_time_ms,
        total_time_ms=round(total_ms, 2),
    )


@app.get("/health")
async def health():
    """Health check para o Kubernetes liveness probe."""
    return {"status": "ok", "service": "P - API Gateway"}


# ──────────────────────────────────────────────────────────
# Funções auxiliares: chamadas gRPC
# ──────────────────────────────────────────────────────────

async def _call_service_a(min_val: int, max_val: int):
    """Chama o Serviço A (Go) via gRPC — obtém números primos."""
    async with grpc.aio.insecure_channel(SERVICE_A_ADDR) as channel:
        stub = prime_pb2_grpc.PrimeServiceStub(channel)
        request = prime_pb2.RangeRequest(min=min_val, max=max_val)
        return await stub.GetPrimes(request)


async def _call_service_b(min_val: int, max_val: int):
    """Chama o Serviço B (Go) via gRPC — obtém estatísticas."""
    async with grpc.aio.insecure_channel(SERVICE_B_ADDR) as channel:
        stub = stats_pb2_grpc.StatsServiceStub(channel)
        request = stats_pb2.RangeRequest(min=min_val, max=max_val)
        return await stub.ComputeStats(request)
