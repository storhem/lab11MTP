package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

// ── Вспомогательные функции ───────────────────────────────────────────────────

func makeRequest(t *testing.T, method, path string) *httptest.ResponseRecorder {
	t.Helper()
	req := httptest.NewRequest(method, path, nil)
	w := httptest.NewRecorder()
	newMux().ServeHTTP(w, req)
	return w
}

func parseJSON(t *testing.T, w *httptest.ResponseRecorder) map[string]string {
	t.Helper()
	var result map[string]string
	if err := json.NewDecoder(w.Body).Decode(&result); err != nil {
		t.Fatalf("не удалось распарсить JSON: %v", err)
	}
	return result
}

// ── GET / ─────────────────────────────────────────────────────────────────────

func TestRoot_StatusOK(t *testing.T) {
	w := makeRequest(t, http.MethodGet, "/")
	if w.Code != http.StatusOK {
		t.Errorf("ожидали 200, получили %d", w.Code)
	}
}

func TestRoot_ContentType(t *testing.T) {
	w := makeRequest(t, http.MethodGet, "/")
	ct := w.Header().Get("Content-Type")
	if !strings.HasPrefix(ct, "application/json") {
		t.Errorf("ожидали application/json, получили %q", ct)
	}
}

func TestRoot_HasMessage(t *testing.T) {
	w := makeRequest(t, http.MethodGet, "/")
	body := parseJSON(t, w)
	if _, ok := body["message"]; !ok {
		t.Error("ответ не содержит поле 'message'")
	}
}

func TestRoot_HasRoutes(t *testing.T) {
	w := makeRequest(t, http.MethodGet, "/")
	body := parseJSON(t, w)
	if _, ok := body["routes"]; !ok {
		t.Error("ответ не содержит поле 'routes'")
	}
}

func TestRoot_ValidJSON(t *testing.T) {
	w := makeRequest(t, http.MethodGet, "/")
	var v any
	if err := json.Unmarshal(w.Body.Bytes(), &v); err != nil {
		t.Errorf("тело ответа не является валидным JSON: %v", err)
	}
}

// ── GET /ping ─────────────────────────────────────────────────────────────────

func TestPing_StatusOK(t *testing.T) {
	w := makeRequest(t, http.MethodGet, "/ping")
	if w.Code != http.StatusOK {
		t.Errorf("ожидали 200, получили %d", w.Code)
	}
}

func TestPing_ContentType(t *testing.T) {
	w := makeRequest(t, http.MethodGet, "/ping")
	ct := w.Header().Get("Content-Type")
	if !strings.HasPrefix(ct, "application/json") {
		t.Errorf("ожидали application/json, получили %q", ct)
	}
}

func TestPing_MessageIsPong(t *testing.T) {
	w := makeRequest(t, http.MethodGet, "/ping")
	body := parseJSON(t, w)
	if body["message"] != "pong" {
		t.Errorf("ожидали 'pong', получили %q", body["message"])
	}
}

func TestPing_HasTimestamp(t *testing.T) {
	w := makeRequest(t, http.MethodGet, "/ping")
	body := parseJSON(t, w)
	if _, ok := body["timestamp"]; !ok {
		t.Error("ответ не содержит поле 'timestamp'")
	}
}

func TestPing_TimestampNotEmpty(t *testing.T) {
	w := makeRequest(t, http.MethodGet, "/ping")
	body := parseJSON(t, w)
	if body["timestamp"] == "" {
		t.Error("timestamp не должен быть пустым")
	}
}

func TestPing_ValidJSON(t *testing.T) {
	w := makeRequest(t, http.MethodGet, "/ping")
	var v any
	if err := json.Unmarshal(w.Body.Bytes(), &v); err != nil {
		t.Errorf("тело ответа не является валидным JSON: %v", err)
	}
}

// ── GET /health ───────────────────────────────────────────────────────────────

func TestHealth_StatusOK(t *testing.T) {
	w := makeRequest(t, http.MethodGet, "/health")
	if w.Code != http.StatusOK {
		t.Errorf("ожидали 200, получили %d", w.Code)
	}
}

func TestHealth_ContentType(t *testing.T) {
	w := makeRequest(t, http.MethodGet, "/health")
	ct := w.Header().Get("Content-Type")
	if !strings.HasPrefix(ct, "application/json") {
		t.Errorf("ожидали application/json, получили %q", ct)
	}
}

func TestHealth_StatusIsOk(t *testing.T) {
	w := makeRequest(t, http.MethodGet, "/health")
	body := parseJSON(t, w)
	if body["status"] != "ok" {
		t.Errorf("ожидали status='ok', получили %q", body["status"])
	}
}

func TestHealth_ValidJSON(t *testing.T) {
	w := makeRequest(t, http.MethodGet, "/health")
	var v any
	if err := json.Unmarshal(w.Body.Bytes(), &v); err != nil {
		t.Errorf("тело ответа не является валидным JSON: %v", err)
	}
}

// ── GET /info ─────────────────────────────────────────────────────────────────

func TestInfo_StatusOK(t *testing.T) {
	w := makeRequest(t, http.MethodGet, "/info")
	if w.Code != http.StatusOK {
		t.Errorf("ожидали 200, получили %d", w.Code)
	}
}

func TestInfo_ContentType(t *testing.T) {
	w := makeRequest(t, http.MethodGet, "/info")
	ct := w.Header().Get("Content-Type")
	if !strings.HasPrefix(ct, "application/json") {
		t.Errorf("ожидали application/json, получили %q", ct)
	}
}

func TestInfo_HasHostname(t *testing.T) {
	w := makeRequest(t, http.MethodGet, "/info")
	body := parseJSON(t, w)
	if _, ok := body["hostname"]; !ok {
		t.Error("ответ не содержит поле 'hostname'")
	}
}

func TestInfo_HasGoVersion(t *testing.T) {
	w := makeRequest(t, http.MethodGet, "/info")
	body := parseJSON(t, w)
	if _, ok := body["go_version"]; !ok {
		t.Error("ответ не содержит поле 'go_version'")
	}
}

func TestInfo_GoVersionNotEmpty(t *testing.T) {
	w := makeRequest(t, http.MethodGet, "/info")
	body := parseJSON(t, w)
	if body["go_version"] == "" {
		t.Error("go_version не должен быть пустым")
	}
}

func TestInfo_HasOS(t *testing.T) {
	w := makeRequest(t, http.MethodGet, "/info")
	body := parseJSON(t, w)
	if _, ok := body["os"]; !ok {
		t.Error("ответ не содержит поле 'os'")
	}
}

func TestInfo_HasArch(t *testing.T) {
	w := makeRequest(t, http.MethodGet, "/info")
	body := parseJSON(t, w)
	if _, ok := body["arch"]; !ok {
		t.Error("ответ не содержит поле 'arch'")
	}
}

func TestInfo_ValidJSON(t *testing.T) {
	w := makeRequest(t, http.MethodGet, "/info")
	var v any
	if err := json.Unmarshal(w.Body.Bytes(), &v); err != nil {
		t.Errorf("тело ответа не является валидным JSON: %v", err)
	}
}

// ── Таблица: все маршруты возвращают 200 ─────────────────────────────────────

func TestAllRoutes_Return200(t *testing.T) {
	routes := []string{"/", "/ping", "/health", "/info"}
	for _, route := range routes {
		t.Run(route, func(t *testing.T) {
			w := makeRequest(t, http.MethodGet, route)
			if w.Code != http.StatusOK {
				t.Errorf("%s: ожидали 200, получили %d", route, w.Code)
			}
		})
	}
}

// ── Таблица: все маршруты возвращают JSON ─────────────────────────────────────

func TestAllRoutes_ReturnJSON(t *testing.T) {
	routes := []string{"/", "/ping", "/health", "/info"}
	for _, route := range routes {
		t.Run(route, func(t *testing.T) {
			w := makeRequest(t, http.MethodGet, route)
			ct := w.Header().Get("Content-Type")
			if !strings.HasPrefix(ct, "application/json") {
				t.Errorf("%s: ожидали application/json, получили %q", route, ct)
			}
		})
	}
}

// ── Метод не GET → 405 ────────────────────────────────────────────────────────

func TestMethodNotAllowed(t *testing.T) {
	cases := []struct {
		method string
		path   string
	}{
		{http.MethodPost, "/ping"},
		{http.MethodDelete, "/health"},
		{http.MethodPut, "/info"},
		{http.MethodPost, "/"},
	}
	for _, tc := range cases {
		t.Run(tc.method+" "+tc.path, func(t *testing.T) {
			w := makeRequest(t, tc.method, tc.path)
			if w.Code != http.StatusMethodNotAllowed {
				t.Errorf("%s %s: ожидали 405, получили %d", tc.method, tc.path, w.Code)
			}
		})
	}
}

// ── Несуществующий маршрут → 404 ─────────────────────────────────────────────

func TestNotFound(t *testing.T) {
	routes := []string{"/unknown", "/api/v1", "/notes"}
	for _, route := range routes {
		t.Run(route, func(t *testing.T) {
			w := makeRequest(t, http.MethodGet, route)
			if w.Code != http.StatusNotFound {
				t.Errorf("%s: ожидали 404, получили %d", route, w.Code)
			}
		})
	}
}
