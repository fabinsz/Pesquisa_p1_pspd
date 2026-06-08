"""
=============================================================
Serviço P REST - API Gateway via REST/JSON
(versão alternativa para comparação de performance com gRPC)
=============================================================
"""

import os
import time
import asyncio
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

SERVICE_A_URL = os.getenv("SERVICE_A_REST_URL", "http://localhost:8081")
SERVICE_B_URL = os.getenv("SERVICE_B_REST_URL", "http://localhost:8082")

app = FastAPI(title="Analisador de Intervalos — versão REST")


class AnalyzeRequest(BaseModel):
    min_val: int
    max_val: int


@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    if req.min_val > req.max_val:
        req.min_val, req.max_val = req.max_val, req.min_val

    total_start = time.time()

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Chama A e B em paralelo via HTTP/JSON (sem gRPC, sem protobuf)
        prime_task = client.get(f"{SERVICE_A_URL}/primes",
                                params={"min": req.min_val, "max": req.max_val})
        stats_task = client.get(f"{SERVICE_B_URL}/stats",
                                params={"min": req.min_val, "max": req.max_val})

        prime_resp, stats_resp = await asyncio.gather(prime_task, stats_task)

    if prime_resp.status_code != 200:
        raise HTTPException(503, "Erro no Serviço A REST")
    if stats_resp.status_code != 200:
        raise HTTPException(503, "Erro no Serviço B REST")

    prime_data = prime_resp.json()
    stats_data = stats_resp.json()

    total_ms = (time.time() - total_start) * 1000

    return {
        "min_val": req.min_val,
        "max_val": req.max_val,
        "primes": prime_data["primes"],
        "prime_count": prime_data["count"],
        "prime_computation_ms": prime_data["computation_time_ms"],
        "sum": stats_data["sum"],
        "mean": stats_data["mean"],
        "variance": stats_data["variance"],
        "std_dev": stats_data["std_dev"],
        "count": stats_data["count"],
        "stats_computation_ms": stats_data["computation_time_ms"],
        "total_time_ms": round(total_ms, 2),
    }


@app.get("/health")
async def health():
    return {"status": "ok", "version": "REST"}
