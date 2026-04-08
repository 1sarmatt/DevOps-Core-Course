package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
)

func TestMainHandler(t *testing.T) {
	req, err := http.NewRequest("GET", "/", nil)
	if err != nil {
		t.Fatal(err)
	}

	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(mainHandler)
	handler.ServeHTTP(rr, req)

	// Check status code
	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v", status, http.StatusOK)
	}

	// Check content type
	if contentType := rr.Header().Get("Content-Type"); contentType != "application/json" {
		t.Errorf("handler returned wrong content type: got %v want %v", contentType, "application/json")
	}

	// Parse JSON response
	var response ServiceInfo
	if err := json.Unmarshal(rr.Body.Bytes(), &response); err != nil {
		t.Errorf("failed to parse JSON response: %v", err)
	}

	// Verify service info
	if response.Service.Name != "devops-info-service" {
		t.Errorf("wrong service name: got %v want %v", response.Service.Name, "devops-info-service")
	}

	if response.Service.Framework != "Go" {
		t.Errorf("wrong framework: got %v want %v", response.Service.Framework, "Go")
	}

	// Verify system info exists
	if response.System.Hostname == "" {
		t.Error("hostname should not be empty")
	}

	// Verify runtime info
	if response.Runtime.UptimeSeconds < 0 {
		t.Error("uptime should be non-negative")
	}

	if response.Runtime.Timezone != "UTC" {
		t.Errorf("wrong timezone: got %v want %v", response.Runtime.Timezone, "UTC")
	}

	// Verify request info
	if response.Request.Method != "GET" {
		t.Errorf("wrong method: got %v want %v", response.Request.Method, "GET")
	}

	if response.Request.Path != "/" {
		t.Errorf("wrong path: got %v want %v", response.Request.Path, "/")
	}

	// Verify endpoints list
	if len(response.Endpoint) < 2 {
		t.Errorf("expected at least 2 endpoints, got %d", len(response.Endpoint))
	}
}

func TestHealthHandler(t *testing.T) {
	req, err := http.NewRequest("GET", "/health", nil)
	if err != nil {
		t.Fatal(err)
	}

	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(healthHandler)
	handler.ServeHTTP(rr, req)

	// Check status code
	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v", status, http.StatusOK)
	}

	// Check content type
	if contentType := rr.Header().Get("Content-Type"); contentType != "application/json" {
		t.Errorf("handler returned wrong content type: got %v want %v", contentType, "application/json")
	}

	// Parse JSON response
	var response HealthResponse
	if err := json.Unmarshal(rr.Body.Bytes(), &response); err != nil {
		t.Errorf("failed to parse JSON response: %v", err)
	}

	// Verify health status
	if response.Status != "healthy" {
		t.Errorf("wrong status: got %v want %v", response.Status, "healthy")
	}

	// Verify timestamp format
	if _, err := time.Parse(time.RFC3339, response.Timestamp); err != nil {
		t.Errorf("invalid timestamp format: %v", err)
	}

	// Verify uptime
	if response.UptimeSeconds < 0 {
		t.Error("uptime should be non-negative")
	}
}

func TestPrettyPrint(t *testing.T) {
	req, err := http.NewRequest("GET", "/?pretty=true", nil)
	if err != nil {
		t.Fatal(err)
	}

	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(mainHandler)
	handler.ServeHTTP(rr, req)

	// Check that response contains indentation (pretty print)
	body := rr.Body.String()
	if len(body) == 0 {
		t.Error("response body should not be empty")
	}

	// Verify it's still valid JSON
	var response ServiceInfo
	if err := json.Unmarshal([]byte(body), &response); err != nil {
		t.Errorf("pretty printed response is not valid JSON: %v", err)
	}
}

func TestGetUptime(t *testing.T) {
	// Reset start time for testing
	originalStartTime := startTime
	startTime = time.Now().Add(-2 * time.Hour)
	defer func() { startTime = originalStartTime }()

	uptime := getUptime()

	if uptime.UptimeSeconds < 7200 { // 2 hours = 7200 seconds
		t.Errorf("uptime should be at least 7200 seconds, got %d", uptime.UptimeSeconds)
	}

	if uptime.UptimeHuman == "" {
		t.Error("uptime human readable string should not be empty")
	}

	if uptime.Timezone != "UTC" {
		t.Errorf("wrong timezone: got %v want %v", uptime.Timezone, "UTC")
	}
}

func TestGetSystemInfo(t *testing.T) {
	info := getSystemInfo()

	if info.Hostname == "" {
		t.Error("hostname should not be empty")
	}

	if info.Platform == "" {
		t.Error("platform should not be empty")
	}

	if info.Architecture == "" {
		t.Error("architecture should not be empty")
	}

	if info.CPUCount <= 0 {
		t.Error("CPU count should be positive")
	}
}

func TestGetClientIP(t *testing.T) {
	tests := []struct {
		name           string
		remoteAddr     string
		xForwardedFor  string
		xRealIP        string
		expectedIP     string
	}{
		{
			name:       "Direct connection",
			remoteAddr: "192.168.1.1:12345",
			expectedIP: "192.168.1.1",
		},
		{
			name:          "X-Forwarded-For header",
			remoteAddr:    "192.168.1.1:12345",
			xForwardedFor: "203.0.113.1",
			expectedIP:    "203.0.113.1",
		},
		{
			name:       "X-Real-IP header",
			remoteAddr: "192.168.1.1:12345",
			xRealIP:    "203.0.113.2",
			expectedIP: "203.0.113.2",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := httptest.NewRequest("GET", "/", nil)
			req.RemoteAddr = tt.remoteAddr

			if tt.xForwardedFor != "" {
				req.Header.Set("X-Forwarded-For", tt.xForwardedFor)
			}

			if tt.xRealIP != "" {
				req.Header.Set("X-Real-IP", tt.xRealIP)
			}

			ip := getClientIP(req)
			if ip != tt.expectedIP {
				t.Errorf("getClientIP() = %v, want %v", ip, tt.expectedIP)
			}
		})
	}
}

func TestGetEnv(t *testing.T) {
	tests := []struct {
		name         string
		key          string
		defaultValue string
		envValue     string
		expected     string
	}{
		{
			name:         "Environment variable not set",
			key:          "TEST_VAR_NOT_SET",
			defaultValue: "default",
			expected:     "default",
		},
		{
			name:         "Environment variable set",
			key:          "TEST_VAR_SET",
			defaultValue: "default",
			envValue:     "custom",
			expected:     "custom",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.envValue != "" {
				t.Setenv(tt.key, tt.envValue)
			}

			result := getEnv(tt.key, tt.defaultValue)
			if result != tt.expected {
				t.Errorf("getEnv() = %v, want %v", result, tt.expected)
			}
		})
	}
}

func TestPlural(t *testing.T) {
	tests := []struct {
		n        int64
		expected string
	}{
		{0, "s"},
		{1, ""},
		{2, "s"},
		{100, "s"},
	}

	for _, tt := range tests {
		result := plural(tt.n)
		if result != tt.expected {
			t.Errorf("plural(%d) = %v, want %v", tt.n, result, tt.expected)
		}
	}
}
