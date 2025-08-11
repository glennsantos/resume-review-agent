# Resume Review Agent

A microservices-based system that compares resumes against job descriptions and provides AI-powered scoring and analysis.

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
docker compose up --build -d
```

## Features

### Core Functionality
- **Resume Upload & Processing**: Accepts PDF/DOC/DOCX files and extracts text content
- **AI-Powered Comparison**: Uses OpenAI GPT-4o-mini to analyze resume fit against job descriptions
- **Structured Scoring**: Returns criteria-based scoring with detailed explanations
- **Job Description Management**: Create, read, update job descriptions with persistent storage

### Architecture (Event-Driven Microservices)
- **Ingestion Service**: FastAPI backend handling uploads, job descriptions, and comparisons
- **Normalizer Service**: Converts resumes to JSON Resume schema using OpenAI
- **Frontend**: React SPA called "CV<>JD" for user interaction
- **Message Bus**: NATS for event-driven communication between services
- **Database**: SQLite for job descriptions storage

### Key Features
- **File Support**: PDF extraction via PyPDF2, text cleaning/preprocessing
- **Smart Resume Processing**: Uses JSON Resume schema standard, fallback to cleaned raw text
- **Real-time Analysis**: Immediate AI-powered comparison results
- **Job Description Management**: Full CRUD operations with editing capabilities
- **Event Publishing**: Publishes `resume.uploaded` events for processing pipeline

### Technical Stack
- **Backend**: Python FastAPI, OpenAI API, SQLAlchemy, NATS
- **Frontend**: React, Axios for API calls
- **Infrastructure**: Docker Compose orchestration, CORS enabled
- **Data**: SQLite database, file uploads to local storage

### Workflow
1. User uploads resume and selects job description via React frontend
2. Ingestion service processes file and publishes event to NATS
3. Normalizer service converts resume to structured JSON format
4. Comparison endpoint analyzes resume against job description using GPT-4o-mini
5. Results displayed showing criteria scores and summary analysis

## Usage

1. Open http://localhost:4000 in your browser
2. Create or select a job description
3. Upload a resume file (PDF, DOC, or DOCX)
4. Click "Compare" to get AI-powered analysis and scoring

## Developer Documentation

### Guiding Principles
- **Separation of Concerns**: Ingestion → Normalization → Scoring → Presentation
- **Contract‑First**: Resume JSON MUST adhere to https://jsonresume.org/schema
- **Plug‑and‑Play Engine**: Core scoring via OpenAI LLM microservice
- **Event‑Driven**: Use lightweight, open‑source, easy‑scale message bus (e.g. NATS)
- **Audit & Observability**: Full traceability; logs & metrics in Grafana; semantic versioning of prompts/logic

### Persistence
- **Vector DB**: Pinecone or similar (Future)
- **Relational DB**: Resumes, JDs, audit logs, semantic versions (Future)

### Log Aggregation & Metrics
- **Grafana**: Dashboards for monitoring (Future)
- **Prometheus/Loki**: Log aggregation and metrics (Future)

### Testing & Observability
- **Testing**: Unit tests on every service from Day 1; integration tests on event flows
- **Observability**: Instrument latency/error metrics; log all stages; visualize in Grafana
- **Error Handling**: Retry manual on OpenAI timeouts; surface failures via email/dashboard

### Deployment & Scaling
- **Local‑First**: Docker for dev; CI pipeline builds images
- **Future Production**: Kubernetes cluster with auto‑scaling for ingestion & scoring
- **Monitoring**: Grafana alerts on latency, error rates, queue depth
