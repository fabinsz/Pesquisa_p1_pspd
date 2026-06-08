"""
=============================================================
DEMO gRPC - Cliente: CLIENT STREAMING (N requests → 1 response)
=============================================================
O cliente envia múltiplas mensagens; o servidor acumula tudo
e responde apenas uma vez ao final.

Quando usar:
  - Upload de dados em partes (chunked upload)
  - Batch processing (enviar lote para processamento)
  - Telemetria / coleta de métricas em série
  - Logs de sessão

Execute PRIMEIRO o servidor: python server.py
=============================================================
"""

import grpc
import demo_pb2 as pb
import demo_pb2_grpc as pb_grpc


def numero_generator(numeros: list[int]):
    """Gerador que simula o cliente enviando números um por um."""
    for n in numeros:
        print(f"   → Enviando número: {n}")
        yield pb.NumberRequest(number=n)


def run():
    with grpc.insecure_channel("localhost:50099") as channel:
        stub = pb_grpc.DemoServiceStub(channel)

        print("=" * 50)
        print("TIPO 3: CLIENT STREAMING")
        print("  → Cliente envia N requests, recebe 1 response")
        print("=" * 50)

        # Lista de números a enviar em lote
        lote = [2, 3, 4, 5, 10, 11, 17, 20, 23, 30, 31]

        print(f"\n→ Enviando lote com {len(lote)} números:")
        print("  (o servidor acumula tudo e responde ao final)\n")

        # Passa o gerador para o stub — ele transmite automaticamente
        response = stub.CountPrimesInBatch(numero_generator(lote))

        print(f"\n✅ Resposta do servidor:")
        print(f"   Total recebido: {response.total_received}")
        print(f"   Primos no lote: {response.prime_count}")
        print(f"   Primos: {list(response.primes_found)}")


if __name__ == "__main__":
    run()
