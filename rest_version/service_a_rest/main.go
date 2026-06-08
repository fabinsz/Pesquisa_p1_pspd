package main

import (
	"encoding/json"
	"log"
	"math"
	"net/http"
	"strconv"
	"time"
)

// --------------------------------------------------
// Serviço A REST - Primos (versão alternativa sem gRPC)
// Usado para comparar performance com a versão gRPC
// --------------------------------------------------

type PrimesResponse struct {
	Primes           []int64 `json:"primes"`
	Count            int64   `json:"count"`
	ComputationTimeMs float64 `json:"computation_time_ms"`
}

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

func primesHandler(w http.ResponseWriter, r *http.Request) {
	minStr := r.URL.Query().Get("min")
	maxStr := r.URL.Query().Get("max")

	min, _ := strconv.ParseInt(minStr, 10, 64)
	max, _ := strconv.ParseInt(maxStr, 10, 64)

	start := time.Now()

	var primes []int64
	for n := min; n <= max; n++ {
		if isPrime(n) {
			primes = append(primes, n)
		}
	}

	elapsed := float64(time.Since(start).Microseconds()) / 1000.0

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(PrimesResponse{
		Primes:           primes,
		Count:            int64(len(primes)),
		ComputationTimeMs: elapsed,
	})
}

func main() {
	http.HandleFunc("/primes", primesHandler)
	log.Println(" Serviço A REST rodando na porta 8081")
	log.Fatal(http.ListenAndServe(":8081", nil))
}
