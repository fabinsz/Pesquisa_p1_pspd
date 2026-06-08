package main

import (
	"context"
	"log"
	"math"
	"net"
	"time"

	pb "service_b/statsservice"

	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"
)

// --------------------------------------------------
// Implementação do servidor gRPC - Serviço B (Estatísticas)
// --------------------------------------------------

const port = ":50052"

type server struct {
	pb.UnimplementedStatsServiceServer
}

// ComputeStats - chamada UNARY: calcula estatísticas do intervalo
func (s *server) ComputeStats(ctx context.Context, req *pb.RangeRequest) (*pb.StatsResponse, error) {
	log.Printf("[Serviço B] Recebida requisição: intervalo [%d, %d]", req.Min, req.Max)
	start := time.Now()

	if req.Max < req.Min {
		req.Min, req.Max = req.Max, req.Min
	}

	count := req.Max - req.Min + 1
	n := float64(count)

	// Fórmulas fechadas para eficiência (evita loop para intervalos grandes)
	// Soma: n*(min + max)/2
	sum := float64(count) * float64(req.Min+req.Max) / 2.0
	mean := sum / n

	// Variância de uma progressão aritmética: (n^2 - 1) / 12
	variance := (float64(count)*float64(count) - 1.0) / 12.0
	stdDev := math.Sqrt(variance)

	// Simula algum trabalho computacional para o benchmark
	// (percorre o array como em uma análise real)
	var checksum int64
	for i := req.Min; i <= req.Max; i++ {
		checksum += i % 7 // operação arbitrária para simular carga
	}
	_ = checksum

	elapsed := float64(time.Since(start).Microseconds()) / 1000.0
	log.Printf("[Serviço B] Estatísticas calculadas em %.2f ms", elapsed)

	return &pb.StatsResponse{
		Sum:               sum,
		Mean:              mean,
		Variance:          variance,
		StdDev:            stdDev,
		Count:             count,
		MinVal:            req.Min,
		MaxVal:            req.Max,
		ComputationTimeMs: elapsed,
	}, nil
}

func main() {
	lis, err := net.Listen("tcp", port)
	if err != nil {
		log.Fatalf("Falha ao escutar na porta %s: %v", port, err)
	}

	grpcServer := grpc.NewServer()
	pb.RegisterStatsServiceServer(grpcServer, &server{})
	reflection.Register(grpcServer)

	log.Printf("🚀 Serviço B (Estatísticas) rodando em %s", port)
	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("Falha ao iniciar servidor: %v", err)
	}
}
