"""
=============================================================
Script de Benchmark: gRPC vs REST/JSON
=============================================================
Compara o tempo de resposta das duas versões sob as mesmas
condições — 30 requisições por intervalo, 5 intervalos de teste.

Uso:
  1) Inicie todos os 6 serviços (gRPC e REST)
  2) Execute: python benchmark.py
  3) Os resultados são exibidos em tabela e salvos em benchmark_results.csv
=============================================================
"""

import time
import asyncio
import statistics
import httpx
import csv
import subprocess
from dataclasses import dataclass

def discover_grpc_gateway() -> str:
    """Descobre dinamicamente a URL do gRPC Gateway via Minikube."""
    fallback_url = "http://192.168.49.2:30080"
    try:
        # Executa o comando do minikube para obter a URL do serviço
        result = subprocess.run(
            ["minikube", "service", "service-p", "-n", "pspd", "--url"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout:
            # Pega a primeira linha válida gerada pelo comando
            url = result.stdout.strip().split("\n")[0]
            if url.startswith("http"):
                print(f"📡 URL gRPC autodetectada via Minikube: {url}")
                return url
        
        print(f"⚠️ Não foi possível detectar a URL via Minikube. Usando fallback: {fallback_url}")
        return fallback_url
    except Exception as e:
        print(f"⚠️ Erro ao tentar rodar o comando do Minikube ({e}). Usando fallback: {fallback_url}")
        return fallback_url

# Descoberta da URL em tempo de execução
GRPC_GATEWAY = discover_grpc_gateway()  # Serviço P (gRPC) detectado dinamicamente
REST_GATEWAY  = "http://localhost:8003"  # Serviço P (REST)

NUM_REQUESTS = 30  # requisições por intervalo

TEST_INTERVALS = [
    (1,    10_000),
    (1,    50_000),
    (1,   100_000),
    (1,   200_000),
    (5000, 100_000),
]


@dataclass
class BenchResult:
    interval: str
    version: str
    mean_ms: float
    median_ms: float
    min_ms: float
    max_ms: float
    std_ms: float


async def measure(client: httpx.AsyncClient, url: str, min_v: int, max_v: int) -> float:
    """Faz uma requisição e retorna o tempo em ms."""
    start = time.perf_counter()
    resp = await client.post(url + "/analyze",
                              json={"min_val": min_v, "max_val": max_v},
                              timeout=120.0)
    elapsed = (time.perf_counter() - start) * 1000
    if resp.status_code != 200:
        raise Exception(f"HTTP {resp.status_code}: {resp.text[:200]}")
    return elapsed


async def run_benchmark():
    results: list[BenchResult] = []

    print("\n" + "=" * 65)
    print(" BENCHMARK: gRPC vs REST/JSON")
    print(f" {NUM_REQUESTS} requisições por intervalo")
    print("=" * 65)

    async with httpx.AsyncClient() as client:
        for min_v, max_v in TEST_INTERVALS:
            label = f"[{min_v:,}, {max_v:,}]"
            print(f"\n🔄 Testando intervalo {label} …")

            for version, url in [("gRPC", GRPC_GATEWAY), ("REST", REST_GATEWAY)]:
                times = []
                for i in range(NUM_REQUESTS):
                    try:
                        ms = await measure(client, url, min_v, max_v)
                        times.append(ms)
                        print(f"   [{version}] req {i+1:02d}: {ms:.1f} ms")
                    except Exception as e:
                        print(f"   [{version}] req {i+1:02d}: ERRO — {e}")

                if times:
                    r = BenchResult(
                        interval=label,
                        version=version,
                        mean_ms=statistics.mean(times),
                        median_ms=statistics.median(times),
                        min_ms=min(times),
                        max_ms=max(times),
                        std_ms=statistics.stdev(times) if len(times) > 1 else 0,
                    )
                    results.append(r)

    # ── Exibe tabela de resultados ───────────────────────────
    print("\n\n" + "=" * 65)
    print(" RESULTADOS")
    print("=" * 65)
    print(f"{'Intervalo':<22} {'Versão':<8} {'Média(ms)':<12} {'Mediana':<10} {'Min':<8} {'Max':<8} {'StdDev':<8}")
    print("-" * 65)

    for r in results:
        print(f"{r.interval:<22} {r.version:<8} {r.mean_ms:<12.1f} {r.median_ms:<10.1f} "
              f"{r.min_ms:<8.1f} {r.max_ms:<8.1f} {r.std_ms:<8.1f}")

    # ── Salva CSV ────────────────────────────────────────────
    with open("benchmark_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Intervalo","Versao","Media_ms","Mediana_ms","Min_ms","Max_ms","StdDev_ms"])
        for r in results:
            writer.writerow([r.interval, r.version, f"{r.mean_ms:.2f}", f"{r.median_ms:.2f}",
                             f"{r.min_ms:.2f}", f"{r.max_ms:.2f}", f"{r.std_ms:.2f}"])

    print("\n📄 Resultados salvos em benchmark_results.csv")
    return results


if __name__ == "__main__":
    asyncio.run(run_benchmark())