"""
=============================================================
DEMO gRPC - Cliente: SERVER STREAMING (1 request → N responses)
=============================================================
O servidor envia múltiplas respostas para uma única requisição.
O cliente as recebe progressivamente, sem precisar esperar tudo.

Quando usar:
  - Retornar listas grandes de dados
  - Feed de eventos em tempo real (logs, notificações)
  - Download de arquivos em chunks
  - Progresso de processamento longo

Execute PRIMEIRO o servidor: python server.py
=============================================================
"""

import grpc
import demo_pb2 as pb
import demo_pb2_grpc as pb_grpc


def run():
    with grpc.insecure_channel("localhost:50099") as channel:
        stub = pb_grpc.DemoServiceStub(channel)

        print("=" * 50)
        print("TIPO 2: SERVER STREAMING")
        print("  → Cliente envia 1 request, recebe N responses")
        print("=" * 50)

        # Pede primos no intervalo [1, 50]
        request = pb.RangeRequest(min=1, max=50)

        print(f"\n→ Pedindo primos no intervalo [1, 50]:")
        print("   (o servidor envia cada primo assim que encontrado)\n")

        # O stub retorna um iterador — cada chamada ao `for` recebe uma mensagem
        for prime in stub.StreamPrimes(request):
            print(f"   Recebido primo #{prime.position}: {prime.value}")

        print("\n✅ Stream encerrado pelo servidor")


if __name__ == "__main__":
    run()
