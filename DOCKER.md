# Docker Deployment Guide

This repository now includes a lightweight containerised stack so you can run the
ESP32 backend and dashboard with a single command.

## 1. Prerequisites

- Docker Desktop or Docker Engine 24+
- `docker compose` plugin (or `docker-compose`)

## 2. Prepare environment variables

Create a `.env` file in the project root (next to `docker-compose.yml`) with all
required secrets:

```dotenv
# Backend / IoT
THING_NAME=ESP32_SmartDevice
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_IOT_ENDPOINT=...amazonaws.com

# Flask specific
FLASK_ENV=production

# Optional: override default
# BACKEND_API_URL=http://backend:5000/api
```

> In Docker networking, the backend service is reachable at `http://backend:5000`,
> so no extra change is needed unless you have a different host.

## 3. Build & run the stack

From the repository root:

```bash
docker compose up --build
```

Services that start:

| Service   | Description                           | Port |
| --------- | ------------------------------------- | ---- |
| `backend` | Flask REST API + IoT dashboard assets | 5000 |

All logs stream to the terminal. Press `Ctrl+C` to stop the stack.

## 4. Use the system

1. Open the IoT dashboard: http://localhost:5000  
2. Use the dashboard controls (or the `/api/*` endpoints) to read sensor data
   and toggle relays. All functionality is available directly through the
   backend without any additional voice components.

## 5. Development workflow

During local development you can still run services individually (e.g. only the
backend) while keeping the Docker configuration as reference. For production,
point DNS or reverse proxies at the three exposed ports or adapt the compose
file to your environment.

## 6. Troubleshooting

- **Backend unhealthy:** ensure the container can reach AWS IoT Core (verify the
  credentials in `.env` and inspect `docker compose logs backend`).
- **Dashboard not loading:** confirm port `5000` is free locally and the backend
  container is running.

Feel free to tailor the compose file to your infrastructure (TLS termination,
custom domains, etc.). Once everything is configured you can run the full stack
whenever you need with:

```bash
docker compose up
```


