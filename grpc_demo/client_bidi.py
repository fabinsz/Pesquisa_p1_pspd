"""
=============================================================
DEMO gRPC - Cliente: BIDI STREAMING (N requests ↔ N responses)
=============================================================
Cliente e servidor trocam streams simultaneamente e de forma
independente — nenhum precisa esperar o outro terminar.

Quando usar:
  - Aplicações de chat / mensagens em tempo real
  - Jogos multiplayer (estado do jogo em ambas direções)
  - Análise interativa (perguntas e respostas contínuas)
  - Protocolos de handshake complexos

Execute PRIMEIRO o servidor: python server.py
=============================================================
"""

import grpc
import demo_pb2 as pb
import demo_pb2_grpc as pb_grpc


def numero_generator(numeros: list[int]):
    """Gerador de requests do cliente."""
    import time
    for n in numeros:
        print(f"  [Cliente → Servidor] Enviando: {n}")
        yield pb.NumberRequest(number=n)
        time.sleep(0.3)  # simula cadência de envio


def run():
    with grpc.insecure_channel("localhost:50099") as channel:
        stub = pb_grpc.DemoServiceStub(channel)

        print("=" * 50)
        print("TIPO 4: BIDIRECTIONAL STREAMING")
        print("  → Cliente e servidor trocam streams livremente")
        print("=" * 50)

        numeros = [13, 14, 17, 18, 19, 24, 29, 30]

        print(f"\n→ Iniciando sessão bidirecional com {len(numeros)} números:\n")

        # O stub recebe um gerador e retorna um iterador
        # Ambos fluem simultaneamente em threads separadas
        responses = stub.InteractivePrimeCheck(numero_generator(numeros))

        for resp in responses:
            print(f"  [Servidor → Cliente] {resp.message}")

        print("\n Sessão bidirecional encerrada")


if __name__ == "__main__":
    run()
