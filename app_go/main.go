package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net"
	"net/http"
	"os"
	"runtime"
	"time"
)

// ServiceInfo represents the complete service information response
type ServiceInfo struct {
	Service  Service  `json:"service"`
	System   System   `json:"system"`
	Runtime  Runtime  `json:"runtime"`
	Request  Request  `json:"request"`
	Endpoint []Endpoint `json:"endpoints"`
}

// Service represents service metadata
type Service struct {
	Name        string `json:"name"`
	Version     string `json:"version"`
	Description string `json:"description"`
	Framework   string `json:"framework"`
}

// System represents system information
type System struct {
	Hostname        string `json:"hostname"`
	Platform        string `json:"platform"`
	PlatformVersion string `json:"platform_version"`
	Architecture    string `json:"architecture"`
	CPUCount        int    `json:"cpu_count"`
	PythonVersion   string `json:"python_version"`
}

// Runtime represents runtime information
type Runtime struct {
	UptimeSeconds int64  `json:"uptime_seconds"`
	UptimeHuman   string `json:"uptime_human"`
	CurrentTime   string `json:"current_time"`
	Timezone      string `json:"timezone"`
}

// Request represents request information
type Request struct {
	ClientIP  string `json:"client_ip"`
	UserAgent string `json:"user_agent"`
	Method    string `json:"method"`
	Path      string `json:"path"`
}

// Endpoint represents endpoint information
type Endpoint struct {
	Path        string `json:"path"`
	Method      string `json:"method"`
	Description string `json:"description"`
}

// HealthResponse represents health check response
type HealthResponse struct {
	Status        string `json:"status"`
	Timestamp     string `json:"timestamp"`
	UptimeSeconds int64  `json:"uptime_seconds"`
}

var startTime = time.Now()

func main() {
	// Configuration
	host := getEnv("HOST", "0.0.0.0")
	port := getEnv("PORT", "8080")
	
	// Setup routes
	http.HandleFunc("/", mainHandler)
	http.HandleFunc("/health", healthHandler)
	
	// Start server
	addr := fmt.Sprintf("%s:%s", host, port)
	log.Printf("Starting DevOps Info Service on %s", addr)
	log.Printf("Go version: %s", runtime.Version())
	
	if err := http.ListenAndServe(addr, nil); err != nil {
		log.Fatal("Server failed to start:", err)
	}
}

func mainHandler(w http.ResponseWriter, r *http.Request) {
	log.Printf("Request to main endpoint from %s", getClientIP(r))
	
	uptime := getUptime()
	systemInfo := getSystemInfo()
	requestInfo := getRequestInfo(r)
	
	response := ServiceInfo{
		Service: Service{
			Name:        "devops-info-service",
			Version:     "1.0.0",
			Description: "DevOps course info service",
			Framework:   "Go",
		},
		System:   systemInfo,
		Runtime:  uptime,
		Request:  requestInfo,
		Endpoint: []Endpoint{
			{Path: "/", Method: "GET", Description: "Service information"},
			{Path: "/health", Method: "GET", Description: "Health check"},
		},
	}
	
	// Check for pretty parameter
	pretty := r.URL.Query().Get("pretty") == "true"
	
	w.Header().Set("Content-Type", "application/json")
	if pretty {
		encoder := json.NewEncoder(w)
		encoder.SetIndent("", "    ")
		encoder.Encode(response)
	} else {
		json.NewEncoder(w).Encode(response)
	}
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	uptime := getUptime()
	
	response := HealthResponse{
		Status:        "healthy",
		Timestamp:     time.Now().UTC().Format(time.RFC3339),
		UptimeSeconds: uptime.UptimeSeconds,
	}
	
	// Check for pretty parameter
	pretty := r.URL.Query().Get("pretty") == "true"
	
	w.Header().Set("Content-Type", "application/json")
	if pretty {
		encoder := json.NewEncoder(w)
		encoder.SetIndent("", "    ")
		encoder.Encode(response)
	} else {
		json.NewEncoder(w).Encode(response)
	}
}

func getUptime() Runtime {
	elapsed := time.Since(startTime)
	seconds := int64(elapsed.Seconds())
	
	hours := seconds / 3600
	minutes := (seconds % 3600) / 60
	remainingSeconds := seconds % 60
	
	var uptimeHuman string
	if hours > 0 {
		uptimeHuman = fmt.Sprintf("%d hour%s, %d minute%s", hours, plural(hours), minutes, plural(minutes))
	} else if minutes > 0 {
		uptimeHuman = fmt.Sprintf("%d minute%s, %d second%s", minutes, plural(minutes), remainingSeconds, plural(remainingSeconds))
	} else {
		uptimeHuman = fmt.Sprintf("%d second%s", remainingSeconds, plural(remainingSeconds))
	}
	
	return Runtime{
		UptimeSeconds: seconds,
		UptimeHuman:   uptimeHuman,
		CurrentTime:   time.Now().UTC().Format(time.RFC3339),
		Timezone:      "UTC",
	}
}

func getSystemInfo() System {
	hostname, _ := os.Hostname()
	
	return System{
		Hostname:        hostname,
		Platform:        runtime.GOOS,
		PlatformVersion: getPlatformVersion(),
		Architecture:    runtime.GOARCH,
		CPUCount:        runtime.NumCPU(),
		PythonVersion:   "N/A (Go application)",
	}
}

func getRequestInfo(r *http.Request) Request {
	return Request{
		ClientIP:  getClientIP(r),
		UserAgent: r.Header.Get("User-Agent"),
		Method:    r.Method,
		Path:      r.URL.Path,
	}
}

func getClientIP(r *http.Request) string {
	// Check X-Forwarded-For header first (for reverse proxies)
	if xff := r.Header.Get("X-Forwarded-For"); xff != "" {
		return xff
	}
	
	// Check X-Real-IP header
	if xri := r.Header.Get("X-Real-IP"); xri != "" {
		return xri
	}
	
	// Fall back to RemoteAddr
	host, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		return r.RemoteAddr
	}
	return host
}

func getPlatformVersion() string {
	// For simplicity, return runtime info
	// In a real application, you might use platform-specific libraries
	return fmt.Sprintf("%s %s", runtime.GOOS, runtime.GOARCH)
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func plural(n int64) string {
	if n == 1 {
		return ""
	}
	return "s"
}
