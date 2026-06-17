# PSPD — Projeto de Pesquisa Parte 1

Video: https://unbbr-my.sharepoint.com/:v:/g/personal/190039116_aluno_unb_br/IQAk0AR18L3bQpkj1ptYbjQxAYHdoYF_Id3z_nUg6212fsM?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=idJhcQ

## Analisador de Intervalos Numéricos com gRPC + Kubernetes

**UnB/FCTE — Engenharia de Software | Prof. Fernando W. Cruz**

---

##  Arquitetura

```
[HClient]                    [HServ - Minikube K8s]
Browser ──HTTP──► [Pod P: FastAPI + gRPC Stub] ──gRPC──► [Pod A: Go - Primos]
                                                ──gRPC──► [Pod B: Go - Stats]
```

**Módulo P** (Python/FastAPI): Recebe requisições HTTP do browser, chama A e B via gRPC em paralelo.

**Módulo A** (Go): Encontra todos os números primos em um intervalo [min, max].

**Módulo B** (Go): Calcula estatísticas do intervalo (soma, média, variância, desvio padrão).

---

##  Estrutura do Projeto

```
projeto_pspd/
├── proto/                  # Definições protobuf
│   ├── prime_service.proto
│   └── stats_service.proto
├── service_a/              # Serviço A — Go (Primos)
│   ├── main.go
│   ├── go.mod
│   └── Dockerfile
├── service_b/              # Serviço B — Go (Estatísticas)
│   ├── main.go
│   ├── go.mod
│   └── Dockerfile
├── service_p/              # Serviço P — Python/FastAPI (Gateway)
│   ├── main.py
│   ├── requirements.txt
│   ├── templates/index.html
│   └── Dockerfile
├── grpc_demo/              # B.1 — Demonstração dos 4 tipos gRPC
│   ├── demo.proto
│   ├── server.py
│   ├── client_unary.py
│   ├── client_server_streaming.py
│   ├── client_client_streaming.py
│   ├── client_bidi.py
│   └── setup.sh
├── rest_version/           # Versão REST para comparação
│   ├── service_a_rest/main.go
│   ├── service_b_rest/main.go
│   ├── service_p_rest/main.py
│   └── benchmark.py
└── k8s/                    # Manifestos Kubernetes
    ├── namespace.yaml
    ├── service-a.yaml
    ├── service-b.yaml
    └── service-p.yaml
```

---

##  Pré-requisitos

```bash
# Instalar Docker
sudo apt-get install -y docker.io
sudo usermod -aG docker $USER   # reinicie a sessão após isso

# Instalar minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Instalar kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Instalar Go (para rodar/editar os serviços Go localmente)
sudo apt-get install -y golang-go

# Instalar Python 3.11+
sudo apt-get install -y python3 python3-pip
```

---

##  Como rodar no Minikube (passo a passo)

### Passo 1 — Iniciar o Minikube

```bash
minikube start --driver=docker --memory=2048 --cpus=2
minikube status   # deve mostrar: Running
```

### Passo 2 — Apontar Docker para o registry do Minikube

```bash
# Importante: as imagens precisam estar acessíveis pelo minikube
eval $(minikube docker-env)
```

### Passo 3 — Construir as imagens Docker

```bash
# Na raiz do projeto
docker build -t pspd/service-a:latest ./service_a/
docker build -t pspd/service-b:latest ./service_b/
docker build -t pspd/service-p:latest ./service_p/

# Verificar imagens
docker images | grep pspd
```

### Passo 4 — Aplicar os manifestos Kubernetes

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/service-a.yaml
kubectl apply -f k8s/service-b.yaml
kubectl apply -f k8s/service-p.yaml

# Verificar status dos pods
kubectl get pods -n pspd
kubectl get services -n pspd
```

### Passo 5 — Acessar a aplicação

```bash
# Obtém a URL de acesso externo do minikube
minikube service service-p -n pspd --url

# Acesse a URL retornada no browser do HClient
# Exemplo: http://192.168.49.2:30080
```

---

##  Demonstração dos 4 Tipos gRPC (B.1)

```bash
cd grpc_demo

# Instala dependências e gera stubs
bash setup.sh

# Terminal 1: inicia o servidor
python server.py

# Terminal 2: testa cada tipo de comunicação
python client_unary.py
python client_server_streaming.py
python client_client_streaming.py
python client_bidi.py
```

---

##  Benchmark gRPC vs REST

```bash
# 1) Inicie a versão gRPC (Minikube)
# 2) Inicie os serviços REST:
cd rest_version
go run service_a_rest/main.go &
go run service_b_rest/main.go &
pip install fastapi uvicorn httpx
uvicorn service_p_rest.main:app --port 8003 &

# 3) Rode o benchmark
pip install httpx
python benchmark.py
```

---

##  Comandos úteis Kubernetes

```bash
# Ver logs dos pods
kubectl logs -f deployment/service-p -n pspd
kubectl logs -f deployment/service-a -n pspd
kubectl logs -f deployment/service-b -n pspd

# Ver detalhes de um pod
kubectl describe pod -l app=service-p -n pspd

# Ver uso de recursos
kubectl top pods -n pspd

# Reiniciar um deployment
kubectl rollout restart deployment/service-p -n pspd

# Deletar tudo
kubectl delete namespace pspd
minikube stop
```

---

##  Endpoints da API

| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/` | Interface web |
| POST | `/analyze` | Analisa um intervalo |
| GET | `/health` | Health check |
| GET | `/docs` | Documentação OpenAPI |

### Exemplo de requisição:
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"min_val": 1, "max_val": 10000}'
```
