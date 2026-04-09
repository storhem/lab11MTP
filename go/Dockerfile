# Stage 1: сборка и тесты
FROM golang:1.22 AS builder

WORKDIR /app

COPY go.mod ./
RUN go mod download

COPY *.go ./

# Запуск тестов перед сборкой
RUN CGO_ENABLED=0 go test ./...

# Статическая сборка: CGO отключён, ldflags убирают отладочную информацию
RUN CGO_ENABLED=0 GOOS=linux go build \
    -a -installsuffix cgo \
    -ldflags="-s -w -extldflags '-static'" \
    -o server .

# Stage 2: минимальный scratch-образ
FROM scratch

# CA-сертификаты для HTTPS-запросов
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

COPY --from=builder /app/server /server

EXPOSE 8080

CMD ["/server"]
