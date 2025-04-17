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
docker-compose up --build -d