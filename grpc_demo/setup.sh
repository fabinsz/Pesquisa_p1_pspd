#!/bin/bash
set -e

echo " Verificando Python..."
python3 --version

# Cria o venv se não existir
if [ ! -d ".venv" ]; then
  echo ""
  echo " Criando ambiente virtual (.venv)..."
  python3 -m venv .venv
fi

echo " Ativando ambiente virtual..."
source .venv/bin/activate

echo ""
echo " Instalando dependências no venv..."
pip install --upgrade pip --quiet
pip install "grpcio>=1.68.0" "grpcio-tools>=1.68.0" "protobuf>=5.0.0"

echo ""
echo "  Gerando stubs Python do demo.proto..."
python -m grpc_tools.protoc \
  -I. \
  --python_out=. \
  --grpc_python_out=. \
  demo.proto

echo ""
echo " Stubs gerados: demo_pb2.py e demo_pb2_grpc.py"
echo ""
echo "═══════════════════════════════════════════════"
echo "IMPORTANTE: ative o venv antes de rodar:"
echo "  source .venv/bin/activate"
echo ""
echo "Depois, em terminais separados:"
echo "  Terminal 1: python server.py"
echo "  Terminal 2: python client_unary.py"
echo "              python client_server_streaming.py"
echo "              python client_client_streaming.py"
echo "              python client_bidi.py"
echo "═══════════════════════════════════════════════"
