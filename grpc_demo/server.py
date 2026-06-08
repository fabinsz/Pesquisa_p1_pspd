"""
=============================================================
DEMO gRPC - Servidor Python
=============================================================
Demonstra os 4 tipos de comunicação do gRPC:
  1) Unary
  2) Server Streaming
  3) Client Streaming
  4) Bidirectional Streaming

Execute: python server.py
=============================================================
"""

import time
import math
import asyncio
import grpc
from concurrent import futures
import demo_pb2 as pb
import demo_pb2_grpc as pb_grpc


# ──────────────────────────────────────────────────────────
# Funções auxiliares
# ──────────────────────────────────────────────────────────

def is_prime(n: int) -> bool:
    """Verifica se n é primo."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def prime_factors(n: int) -> list[int]:
    """Retorna os fatores primos de n."""
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors


# ──────────────────────────────────────────────────────────
# Implementação do serviço
# ──────────────────────────────────────────────────────────

class DemoServiceServicer(pb_grpc.DemoServiceServicer):

    # ── 1) UNARY ───────────────────────────────────────────
    # Cliente envia UM request → servidor responde UMA vez
    # Análogo a uma chamada de função HTTP REST normal
    def CheckPrime(self, request, context):
        """
        UNARY CALL: verifica se um número é primo e retorna
        seus fatores. É o padrão mais simples e similar ao REST.
        """
        n = request.number
        prime = is_prime(n)
        factors = prime_factors(n) if not prime else [n]
        msg = f"{n} É primo! " if prime else f"{n} NÃO é primo. Fatores: {factors}"
        print(f"[Unary] CheckPrime({n}) → {msg}")

        return pb.PrimeCheckResponse(
            number=n,
            is_prime=prime,
            factors=factors,
            message=msg,
        )

    # ── 2) SERVER STREAMING ────────────────────────────────
    # Cliente envia UM request → servidor responde com STREAM
    # Útil para enviar grandes volumes de dados progressivamente
    def StreamPrimes(self, request, context):
        """
        SERVER STREAMING: cliente pede um intervalo e o servidor
        envia cada primo encontrado como uma mensagem separada.
        Permite que o cliente comece a processar antes do fim.
        """
        print(f"[Server Stream] StreamPrimes([{request.min}, {request.max}])")
        position = 0
        for n in range(request.min, request.max + 1):
            if context.is_active() and is_prime(n):
                position += 1
                print(f"  → Enviando primo #{position}: {n}")
                yield pb.PrimeNumber(value=n, position=position)
                time.sleep(0.01)  # simula processamento gradual

    # ── 3) CLIENT STREAMING ────────────────────────────────
    # Cliente envia STREAM de requests → servidor responde UMA vez
    # Útil para upload em lote ou agregação de dados
    def CountPrimesInBatch(self, request_iterator, context):
        """
        CLIENT STREAMING: cliente envia vários números, um por um.
        O servidor acumula todos e ao final retorna o total de primos.
        Ideal para processamento em lote (batch processing).
        """
        received = []
        primes_found = []

        for req in request_iterator:
            received.append(req.number)
            if is_prime(req.number):
                primes_found.append(req.number)
            print(f"[Client Stream] Recebido: {req.number} | primo={is_prime(req.number)}")

        print(f"[Client Stream] Lote finalizado: {len(received)} números, {len(primes_found)} primos")
        return pb.BatchPrimeCountResponse(
            total_received=len(received),
            prime_count=len(primes_found),
            primes_found=primes_found,
        )

    # ── 4) BIDIRECTIONAL STREAMING ─────────────────────────
    # Cliente e servidor trocam STREAMS simultaneamente
    # Útil para chat, jogos em tempo real, análises interativas
    def InteractivePrimeCheck(self, request_iterator, context):
        """
        BIDI STREAMING: cliente e servidor se comunicam de forma
        totalmente bidirecional. Para cada número enviado, o servidor
        responde imediatamente sem esperar o fim do stream do cliente.
        """
        for req in request_iterator:
            n = req.number
            prime = is_prime(n)
            factors = prime_factors(n) if not prime else [n]
            msg = f" {n} é primo" if prime else f" {n} = {'×'.join(map(str, factors))}"
            print(f"[Bidi Stream] {msg}")
            yield pb.PrimeCheckResponse(
                number=n,
                is_prime=prime,
                factors=factors,
                message=msg,
            )


# ──────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb_grpc.add_DemoServiceServicer_to_server(DemoServiceServicer(), server)
    server.add_insecure_port("[::]:50099")
    server.start()
    print("  Demo Server rodando na porta 50099")
    print("   Use os clientes para testar cada tipo de comunicação:\n")
    print("   python client_unary.py")
    print("   python client_server_streaming.py")
    print("   python client_client_streaming.py")
    print("   python client_bidi.py\n")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
