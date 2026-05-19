# London Crime Intelligence Platform (LCIP)

An **open-source, fully local, zero-subscription AI analytics platform** for exploring, forecasting, and explaining crime patterns in London.

This project is designed to run entirely on a developer machine using **free and open-source tools only**, with no dependency on paid cloud services, SaaS AI APIs, or subscriptions.

It focuses on:
- crime analytics
- forecasting
- anomaly detection
- local LLM-based AI investigation assistant (RAG)
- enterprise-grade observability and auditability (locally hosted)

---

# 1. Scope (Local-First Design)

## 1.1 What This Project Does

The platform enables a data analyst to:

- Explore London crime trends (borough-level)
- Forecast short-term crime patterns
- Detect anomalies in crime activity
- Ask natural language questions locally (no cloud AI)
- Get explainable, evidence-backed insights
- Trace every AI output to source data

---

# 2. Local-Only Technology Stack

## 2.1 Backend
- ASP.NET Core (.NET 8)
- Minimal APIs or Clean Architecture
- Dapper or EF Core
- Serilog (logging)

---

## 2.2 Data Engineering
- Python 3.11
- Pandas
- Polars (optional for performance)
- Apache Airflow (Dockerized locally OR simple cron alternative)
- Great Expectations (data validation)

---

## 2.3 AI / LLM Layer (Fully Local)

### Local LLM Runtime
- Ollama (local inference engine)

### Models (free)
- Llama 3 (8B)
- Mistral 7B
- Phi-3 Mini

### Embeddings
- sentence-transformers (BGE-small / MiniLM)

### Orchestration
- Semantic Kernel (.NET)

---

## 2.4 Vector Database
- pgvector extension on PostgreSQL

(No Pinecone, no cloud vector DBs)

---

## 2.5 Forecasting / ML
- Prophet (baseline forecasting)
- scikit-learn
- XGBoost (optional)

---

## 2.6 Database
- PostgreSQL (local Docker container)

---

## 2.7 Frontend
- React
- Plotly (charts)
- Mapbox (optional, free tier OR OpenStreetMap fallback)

---

## 2.8 Observability (Fully Local)
- Prometheus
- Grafana
- Loki
- OpenTelemetry

---

## 2.9 Infrastructure
- Docker Compose (primary)
- Kubernetes (optional via k3d or kind, local only)
- GitHub Actions (free tier CI only)

---

# 3. System Architecture (Local Execution)

```text
                +----------------------+
                | London Open Data     |
                | (Crime, TfL, etc.)   |
                +----------+-----------+
                           |
                           v
                +----------------------+
                | Python Ingestion     |
                | (Local scripts)      |
                +----------+-----------+
                           |
                           v
                +----------------------+
                | PostgreSQL + pgvector|
                | (Local Docker)       |
                +----------+-----------+
                           |
         +-----------------+------------------+
         |                                    |
         v                                    v
+----------------------+        +------------------------+
| Forecast Engine      |        | AI Assistant (RAG)    |
| Prophet / ML models  |        | Ollama + Semantic K.   |
+----------+-----------+        +-----------+-----------+
           |                                    |
           +------------------+-----------------+
                              |
                              v
                   +----------------------+
                   | ASP.NET Core API     |
                   +----------+-----------+
                              |
                              v
                   +----------------------+
                   | React Dashboard      |
                   +----------------------+
