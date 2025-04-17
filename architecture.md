# Architecture Blueprint

## 1. Guiding Principles
- **Separation of Concerns**: Ingestion → Normalization → Scoring → Presentation
- **Contract‑First**: Resume JSON MUST adhere to https://jsonresume.org/schema
- **Plug‑and‑Play Engine**: Core scoring via OpenAI LLM microservice
- **Event‑Driven**: Use lightweight, open‑source, easy‑scale message bus (e.g. NATS)
- **Audit & Observability**: Full traceability; logs & metrics in Grafana; semantic versioning of prompts/logic

## 2. High‑Level Architecture
see architecture.drawio

### Components
- **Ingestion Service**: accepts PDF/DOC/DOCX, extracts raw text, emits to bus
- **Normalizer Service**: transforms to JSON‑Resume schema, segments sections, maps skills via O*NET
- **Message Bus**: NATS (lightweight, durable, auto‑scaling)
- **Scoring Engine**: GPT‑based microservice, prompt injects resume+JD, returns overall & per‑dim scores + verbose rationale. Scores should be deterministic (match/no match) with confidence scores.
- **Notification Service**: subscribes to scored events, sends email alerts
- **Persistence**:
  - Vector DB (Pinecone or similar)
  - Relational DB (resumes, JDs, audit logs, semantic versions)
- **Log Aggregation & Metrics**: Grafana for dashboards; integrate Prometheus/Loki

## 3. Testing & Observability
- **Testing**: unit tests on every service from Day 1; integration tests on event flows
- **Observability**: instrument latency/error metrics; log all stages; visualize in Grafana
- **Error Handling**: retry manual on OpenAI timeouts; surface failures via email/dashboard

## 4. Deployment & Scaling
- **Local‑First**: Docker for dev; CI pipeline builds images
- **Future Production**: Kubernetes cluster with auto‑scaling for ingestion & scoring
- **Monitoring**: Grafana alerts on latency, error rates, queue depth

*End of Blueprint*