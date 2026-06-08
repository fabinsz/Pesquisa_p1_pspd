"""
=============================================================
DEMO gRPC - Cliente: UNARY CALL (1 request → 1 response)
=============================================================
O tipo mais simples de comunicação gRPC.
Similar a uma chamada HTTP REST convencional.

Quando usar:
  - Consultas simples onde o resultado cabe em uma resposta
  - CRUD básico (criar, ler, atualizar, deletar)
  - Operações sem estado

Execute PRIMEIRO o servidor: python server.py
=============================================================
"""

import grpc
import demo_pb2 as pb
import demo_pb2_grpc as pb_grpc


def run():
    # Conecta ao servidor gRPC
    with grpc.insecure_channel("localhost:50099") as channel:
        stub = pb_grpc.DemoServiceStub(channel)

        print("=" * 50)
        print("TIPO 1: UNARY CALL")
        print("  → Cliente envia 1 request, recebe 1 response")
        print("=" * 50)

        numeros = [7, 10, 13, 100, 97, 1, 2]

        for n in numeros:
            # Cria o request com o número a verificar
            request = pb.NumberRequest(number=n)

            # Faz a chamada unary (bloqueante, aguarda resposta)
            response = stub.CheckPrime(request)

            # Exibe o resultado
            print(f"\n→ Número {n}:")
            print(f"   É primo?  {response.is_prime}")
            print(f"   Fatores:  {list(response.factors)}")
            print(f"   Mensagem: {response.message}")


if __name__ == "__main__":
    run()
