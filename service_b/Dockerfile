FROM golang:1.23-alpine AS builder

RUN apk add --no-cache protobuf protobuf-dev git
RUN go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.34.2 && \
    go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.4.0

WORKDIR /app

COPY proto/stats_service.proto .
RUN mkdir -p statsservice && \
    protoc --go_out=statsservice --go_opt=paths=source_relative \
           --go-grpc_out=statsservice --go-grpc_opt=paths=source_relative \
           stats_service.proto

COPY service_b/main.go .
COPY service_b/go.mod .
RUN go mod tidy && go build -o service_b .

FROM alpine:latest
WORKDIR /app
COPY --from=builder /app/service_b .
EXPOSE 50052
CMD ["./service_b"]
