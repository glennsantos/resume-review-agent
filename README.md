# Resume Review Agent

A system to compare resumes against job descriptions and score fit.

## Prerequisites
- Python 3.11+
- pip3
- NATS server (install via your package manager or Docker):
  - apt: `sudo apt-get install nats-server`
  - brew: `brew install nats-server`
  - Docker: `docker run -d --name nats -p 4222:4222 nats:2.9.19`
- Docker & Docker Compose plugin (for local container orchestration)
- To run Docker commands without sudo, add your user to the "docker" group:
  ```bash
  sudo usermod -aG docker $USER
  # Then log out and back in (or run `newgrp docker`)
  ```

## Setup
```bash
# 1. Ingestion service
cd services/ingestion
pip3 install -r requirements.txt

# 2. Start NATS server
nats-server -DV &

# 3. Run ingestion API
uvicorn ingestion.main:app --reload --host 0.0.0.0 --port 8000

# OR using Docker Compose
cd <project-root>
docker compose up -d --build
```

## Running the Normalizer Service

```bash
# 4. Normalizer service (local)
cd services/normalizer
pip3 install -r requirements.txt
python3 src/normalizer/main.py

# OR using Docker Compose
docker compose up -d normalizer