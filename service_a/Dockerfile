FROM golang:1.23-alpine AS builder

RUN apk add --no-cache protobuf protobuf-dev git
RUN go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.34.2 && \
    go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.4.0

WORKDIR /app

# Copia o proto e gera o código Go
COPY proto/prime_service.proto .
RUN mkdir -p primeservice && \
    protoc --go_out=primeservice --go_opt=paths=source_relative \
           --go-grpc_out=primeservice --go-grpc_opt=paths=source_relative \
           prime_service.proto

# Copia o código-fonte do serviço
COPY service_a/main.go .
COPY service_a/go.mod .
RUN go mod tidy && go build -o service_a .

FROM alpine:latest
WORKDIR /app
COPY --from=builder /app/service_a .
EXPOSE 50051
CMD ["./service_a"]
