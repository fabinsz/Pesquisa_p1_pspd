package main

import (
	"context"
	"log"
	"math"
	"net"
	"time"

	pb "service_a/primeservice"

	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"
)

// --------------------------------------------------
// Implementação do servidor gRPC - Serviço A (Primos)
// --------------------------------------------------

const port = ":50051"

// server implementa a interface PrimeServiceServer gerada pelo protoc
type server struct {
	pb.UnimplementedPrimeServiceServer
}

// isPrime verifica se n é primo (algoritmo simples)
func isPrime(n int64) bool {
	if n < 2 {
		return false
	}
	if n == 2 {
		return true
	}
	if n%2 == 0 {
		return false
	}
	limit := int64(math.Sqrt(float64(n)))
	for i := int64(3); i <= limit; i += 2 {
		if n%i == 0 {
			return false
		}
	}
	return true
}

// GetPrimes - chamada UNARY: recebe um intervalo e retorna todos os primos
func (s *server) GetPrimes(ctx context.Context, req *pb.RangeRequest) (*pb.PrimesResponse, error) {
	log.Printf("[Serviço A] Recebida requisição: intervalo [%d, %d]", req.Min, req.Max)
	start := time.Now()

	var primes []int64
	for n := req.Min; n <= req.Max; n++ {
		if isPrime(n) {
			primes = append(primes, n)
		}
	}

	elapsed := float64(time.Since(start).Microseconds()) / 1000.0
	log.Printf("[Serviço A] Encontrados %d primos em %.2f ms", len(primes), elapsed)

	return &pb.PrimesResponse{
		Primes:            primes,
		Count:             int64(len(primes)),
		ComputationTimeMs: elapsed,
	}, nil
}

func main() {
	lis, err := net.Listen("tcp", port)
	if err != nil {
		log.Fatalf("Falha ao escutar na porta %s: %v", port, err)
	}

	grpcServer := grpc.NewServer()
	pb.RegisterPrimeServiceServer(grpcServer, &server{})

	// Habilita reflection para facilitar debug com ferramentas como grpcurl
	reflection.Register(grpcServer)

	log.Printf(" Serviço A (Primos) rodando em %s", port)
	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("Falha ao iniciar servidor: %v", err)
	}
}
