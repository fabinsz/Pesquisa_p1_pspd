FROM python:3.11-slim

WORKDIR /app

COPY service_p/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia os protos e gera stubs Python
COPY proto/prime_service.proto .
COPY proto/stats_service.proto .
RUN python -m grpc_tools.protoc \
    -I. \
    --python_out=. \
    --grpc_python_out=. \
    prime_service.proto stats_service.proto

# Copia o código do serviço P
COPY service_p/main.py .
COPY service_p/templates/ templates/

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
