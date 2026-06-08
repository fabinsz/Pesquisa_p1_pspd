package main

import (
	"encoding/json"
	"log"
	"math"
	"net/http"
	"strconv"
	"time"
)

type StatsResponse struct {
	Sum               float64 `json:"sum"`
	Mean              float64 `json:"mean"`
	Variance          float64 `json:"variance"`
	StdDev            float64 `json:"std_dev"`
	Count             int64   `json:"count"`
	MinVal            int64   `json:"min_val"`
	MaxVal            int64   `json:"max_val"`
	ComputationTimeMs float64 `json:"computation_time_ms"`
}

func statsHandler(w http.ResponseWriter, r *http.Request) {
	minStr := r.URL.Query().Get("min")
	maxStr := r.URL.Query().Get("max")

	min, _ := strconv.ParseInt(minStr, 10, 64)
	max, _ := strconv.ParseInt(maxStr, 10, 64)

	start := time.Now()

	count := max - min + 1
	n := float64(count)
	sum := float64(count) * float64(min+max) / 2.0
	mean := sum / n
	variance := (float64(count)*float64(count) - 1.0) / 12.0
	stdDev := math.Sqrt(variance)

	var checksum int64
	for i := min; i <= max; i++ {
		checksum += i % 7
	}
	_ = checksum

	elapsed := float64(time.Since(start).Microseconds()) / 1000.0

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(StatsResponse{
		Sum:               sum,
		Mean:              mean,
		Variance:          variance,
		StdDev:            stdDev,
		Count:             count,
		MinVal:            min,
		MaxVal:            max,
		ComputationTimeMs: elapsed,
	})
}

func main() {
	http.HandleFunc("/stats", statsHandler)
	log.Println(" Serviço B REST rodando na porta 8082")
	log.Fatal(http.ListenAndServe(":8082", nil))
}
