# London Crime Intelligence Platform (LCIP)

> A local-first, end-to-end AI engineering project for forecasting, exploring, and explaining London crime patterns with structured analytics, machine learning, retrieval, and a locally hosted language model.

LCIP is designed as a **zero-subscription, open-source analytics platform** that can run on a developer workstation without paid cloud AI services. It demonstrates how statistical forecasting, machine learning, retrieval-augmented generation, geospatial analysis, APIs, observability, and application engineering fit together in a production-oriented system.

> [!IMPORTANT]
> This repository is an evolving learning and portfolio project. This README describes the intended MVP architecture and engineering principles. Individual capabilities should be marked as implemented, in progress, or planned as the branch develops.

---

## Contents

- [Purpose](#purpose)
- [What LCIP does](#what-lcip-does)
- [Core design](#core-design)
- [System architecture](#system-architecture)
- [Forecasting and machine learning](#forecasting-and-machine-learning)
- [Natural-language investigation assistant](#natural-language-investigation-assistant)
- [Retrieval-Augmented Generation](#retrieval-augmented-generation)
- [Entity, geography, and time resolution](#entity-geography-and-time-resolution)
- [Structured and unstructured data](#structured-and-unstructured-data)
- [Model training, deployment, and persistence](#model-training-deployment-and-persistence)
- [Technology stack](#technology-stack)
- [Repository structure](#repository-structure)
- [Evaluation](#evaluation)
- [Observability, auditability, and security](#observability-auditability-and-security)
- [Delivery roadmap](#delivery-roadmap)
- [Guiding principles](#guiding-principles)

---

## Purpose

LCIP is a self-learning and portfolio project intended to demonstrate enterprise-relevant AI engineering rather than only model experimentation.

The project covers the complete path from source data to a usable product:

- ingesting and validating public data;
- preparing analytical and machine-learning features;
- training, evaluating, and versioning forecast models;
- deploying trained model artefacts for inference;
- storing structured forecast records;
- exposing results through APIs, charts, and maps;
- interpreting natural-language questions with a local off-the-shelf language model;
- retrieving authoritative evidence before generating answers;
- tracing predictions and generated explanations to their sources;
- monitoring data pipelines, models, APIs, retrieval, and AI outputs.

The objective is not to maximise the number of technologies used. It is to demonstrate sound engineering judgement, reproducibility, observability, security, and clear boundaries between probabilistic AI and deterministic application services.

---

## What LCIP does

LCIP aims to enable an analyst to:

- explore London crime trends at borough and, later, finer geographic levels;
- forecast short-term crime counts by location, category, and time period;
- detect unusual changes in crime activity;
- compare forecasts across areas and periods;
- ask questions in natural language using a locally hosted LLM;
- receive evidence-backed answers rather than unsupported chatbot responses;
- inspect the model, data, definition, and source versions behind a result.

Example questions:

```text
What is the predicted burglary count for Barnet next month?

Compare robbery forecasts for boroughs bordering Enfield.

Was the summer forecast higher than the period before New Year?

What evidence may help explain the predicted increase?
```

### What LCIP does not do

LCIP is not intended to:

- let an LLM freely generate and execute unrestricted production SQL;
- treat the LLM's pretrained knowledge as an authoritative data source;
- silently redefine crime categories, locations, or time periods;
- automatically retrain itself during normal user queries;
- claim causal explanations from correlation or retrieved news coverage;
- replace human judgement in operational or public-safety decisions.

---

## Core design

LCIP separates **predictive analytics** from **generative AI**.

```text
Historical structured data
        |
        v
Statistical / ML forecasting
        |
        v
Structured, versioned forecast records
        |
        +------------------------------------+
                                             |
User question                                |
        |                                    |
        v                                    |
Local off-the-shelf language model           |
        |                                    |
        v                                    |
Typed and validated domain request           |
        |                                    |
        v                                    |
SQL / PostGIS / domain services -------------+
        |
        v
Retrieved evidence
        |
        v
Evidence-augmented generation
        |
        v
Human-readable answer with provenance
```

The forecast model and the language model have different responsibilities.

| Responsibility | Primary component |
|---|---|
| Learn patterns from historical numeric data | Statistical or machine-learning model |
| Produce counts, ranges, anomaly scores, and model metadata | Forecast engine |
| Understand varied user wording | Local off-the-shelf LLM |
| Define official LCIP terminology | Domain model and reference data |
| Resolve boroughs and spatial relationships | Geographic resolver and PostGIS |
| Resolve dates, seasons, and event-relative periods | Temporal and event resolvers |
| Retrieve authoritative facts | SQL, APIs, search, and domain services |
| Generate a readable explanation | Local LLM |
| Enforce validation, permissions, and auditability | Application layer |

The LLM is a language interface and explanation engine. It is not the database, model registry, geographic authority, or policy engine.

---

## System architecture

```text
+------------------------------+
| London open/public data      |
| crime, geography, TfL, etc.  |
+--------------+---------------+
               |
               v
+------------------------------+
| Ingestion and validation     |
| Python / Airflow             |
+--------------+---------------+
               |
               v
+------------------------------+
| PostgreSQL / PostGIS         |
| raw, curated, features       |
+--------+---------------------+
         |
         +-------------------------------+
         |                               |
         v                               v
+------------------------------+   +------------------------------+
| Forecast training            |   | Reference and retrieval      |
| baselines / ML / evaluation  |   | taxonomy / search / events   |
+--------------+---------------+   +--------------+---------------+
               |                                  |
               v                                  |
+------------------------------+                  |
| Model registry / artefacts   |                  |
+--------------+---------------+                  |
               |                                  |
               v                                  |
+------------------------------+                  |
| Batch or online inference    |                  |
| structured forecast records  |                  |
+--------------+---------------+                  |
               |                                  |
               +------------------+---------------+
                                  |
                                  v
                     +------------------------------+
                     | ASP.NET Core application/API |
                     | validation, policy, tools    |
                     +--------------+---------------+
                                    |
                      +-------------+-------------+
                      |                           |
                      v                           v
            +--------------------+      +---------------------------+
            | React dashboard    |      | Local LLM assistant       |
            | charts and maps    |      | tools + grounded answers  |
            +--------------------+      +---------------------------+
```

### Logical data flow

```text
Source APIs/files
      -> raw data
      -> validated/normalised data
      -> spatially joined and curated data
      -> modelling features
      -> trained model artefact
      -> forecast records
      -> API/dashboard/assistant
```

---

## Forecasting and machine learning

LCIP uses established statistical, time-series, and machine-learning methodologies over structured historical data.

Candidate model families include:

- seasonal-naive and moving-average baselines;
- regression models;
- Prophet-style time-series forecasting;
- tree-based models from scikit-learn;
- gradient-boosted models such as XGBoost;
- anomaly-detection models.

LCIP does not attempt to create a new forecasting algorithm. It uses off-the-shelf algorithm implementations and trains them on LCIP-specific data.

```text
Off-the-shelf algorithm implementation
                 +
Versioned LCIP training dataset
                 |
                 v
LCIP-specific trained model artefact
```

### Example structured forecast record

```json
{
  "borough_id": "E09000003",
  "crime_type_id": "burglary",
  "period_start": "2026-07-01",
  "period_end": "2026-07-31",
  "predicted_count": 30,
  "lower_bound": 24,
  "upper_bound": 37,
  "model_version": "crime-forecast-v1.0",
  "generated_at": "2026-06-11T09:00:00Z"
}
```

The forecast is ordinary structured application data. It can be queried by APIs, dashboards, reports, and the investigation assistant.

### Training output versus inference output

Training produces a deployable **model artefact**:

```text
Historical data + training algorithm -> trained model artefact
```

Inference loads that artefact and produces forecasts:

```text
Trained model artefact + new input -> prediction
```

A production artefact may contain:

- learned coefficients or tree structures;
- preprocessing and feature transformations;
- category mappings;
- model and library versions;
- training-data references;
- evaluation metrics;
- input and output schemas.

Preprocessing and the trained estimator should normally be packaged as one versioned pipeline so production inference applies the same transformations used during training.

### Batch-first inference

For an MVP, batch inference is the preferred starting point:

```text
Scheduled pipeline
      -> load approved model artefact
      -> score every borough/category/period
      -> store forecast records in PostgreSQL
      -> serve records through API and dashboard
```

This is simpler to audit, reproduce, and operate than introducing a real-time model service before it is required.

---

## Natural-language investigation assistant

LCIP uses a locally hosted, off-the-shelf LLM for language interpretation and answer generation.

The model does not inherently know LCIP's identifiers, current forecasts, definitions, or business rules. LCIP supplies those through schemas, tools, reference data, and retrieved evidence.

```text
OTS language model
+
LCIP instructions
+
LCIP tool schemas
+
LCIP reference data
+
LCIP validation
=
LCIP-aware natural-language interface
```

### Example query flow

User question:

```text
How many break-ins are expected in Barnet next month?
```

The LLM extracts a candidate request:

```json
{
  "intent": "get_crime_prediction",
  "crime_phrase": "break-ins",
  "place_phrase": "Barnet",
  "time_phrase": "next month"
}
```

LCIP resolvers map the phrases to canonical values:

```json
{
  "crime_type_id": "burglary",
  "borough_id": "E09000003",
  "period": "2026-07"
}
```

A controlled service retrieves the forecast:

```json
{
  "predicted_count": 30,
  "model_version": "crime-forecast-v1.0"
}
```

The LLM receives the original question and the retrieved evidence, then generates:

```text
LCIP predicts approximately 30 burglary incidents in Barnet during
July 2026, using forecast model crime-forecast-v1.0.
```

### Why not direct text-to-SQL?

LCIP intentionally avoids this architecture:

```text
Natural language -> unrestricted LLM-generated SQL -> production database
```

It is difficult to secure, test, audit, and govern. It can produce invalid joins, invented columns, unsafe operations, or incorrect business interpretations.

LCIP instead uses:

```text
Natural language
      -> typed domain request
      -> schema validation and policy checks
      -> controlled query builder or domain service
      -> SQL / PostGIS / model API
```

The LLM may propose intent and parameters. Application code owns execution.

---

## Retrieval-Augmented Generation

Retrieval-Augmented Generation, or **RAG**, means:

```text
Retrieval + Augmentation + Generation
```

### Retrieval

Find information required for the current question from an external source.

LCIP retrieval may use:

- exact identifier lookup;
- SQL over forecast and reference tables;
- PostgreSQL full-text search;
- PostGIS spatial queries;
- model-registry lookups;
- event-catalogue searches;
- vector or hybrid search over documents and reports.

A vector database is therefore one possible retrieval mechanism, not the definition of RAG.

### Augmentation

Add retrieved evidence to the input context supplied to the LLM.

```text
Original context:
- system instructions
- user question

Augmented context:
- system instructions
- user question
- resolved entities
- retrieved forecast records
- supporting definitions or documents
- source and model metadata
```

The base model's weights are not normally changed. Its context is temporarily augmented for the current request.

### Generation

Use the LLM to turn the evidence into a readable answer, explanation, comparison, or summary.

A precise description of LCIP is:

> A schema-constrained, tool-using local LLM with structured retrieval, optional semantic document retrieval, and evidence-grounded response generation.

---

## Entity, geography, and time resolution

The forecasting model and the LLM do not need identical internal representations. They communicate through LCIP-defined contracts and stable identifiers.

### Canonical entities

```text
crime_type_id = burglary
borough_id = E09000003
```

Human labels and aliases remain separate:

```text
"burglary"
"burglaries"
"break-ins"
"house break-ins"
        |
        v
crime_type_id = burglary
```

The same principle applies to locations, periods, event types, and model versions.

### Beyond alias tables

Simple aliases do not scale to expressions such as:

```text
the borough next to Enfield
an area inside Barnet
within five kilometres of Camden
the place previously known as X
before New Year
during summer
during the riots
```

LCIP therefore translates language into a small set of reusable operations:

```text
inside(place)
adjacent_to(place)
within_distance(place, distance)
before(time_or_event)
after(time_or_event)
during(time_or_event)
overlaps(interval)
```

The LLM acts as a semantic parser. Deterministic services execute the operations.

### Typed domain request example

```json
{
  "intent": "compare_predictions",
  "crime": {
    "candidate_name": "robbery"
  },
  "location": {
    "operator": "adjacent_to",
    "reference_place": "Enfield",
    "result_type": "borough"
  },
  "time": {
    "operator": "during",
    "period": {
      "type": "season",
      "name": "summer",
      "year": 2025,
      "region": "GB"
    }
  }
}
```

### Geography

PostGIS provides authoritative operations for:

- containment;
- adjacency;
- intersection;
- distance;
- overlap.

Examples:

```text
"boroughs next to Enfield" -> boundary adjacency query
"areas inside Barnet" -> containment query
"within 5 km of Camden" -> distance query
```

### Time

Natural expressions are resolved into concrete intervals.

```text
"summer 2025"
        |
        v
2025-06-01 to 2025-08-31
```

Definitions such as meteorological or astronomical summer must be explicit and versioned.

### Named events

```text
"during the riots"
```

cannot be resolved safely from language alone. LCIP needs an event catalogue or approved source containing:

- stable event ID;
- event type and names;
- geographic scope;
- start and end times;
- provenance and confidence metadata.

If several events match, the assistant must expose the ambiguity rather than silently guess.

---

## Structured and unstructured data

LCIP uses the simplest reliable retrieval mechanism for each type of information.

| Information | Preferred mechanism |
|---|---|
| Forecast values | SQL |
| Borough boundaries and adjacency | PostGIS |
| Crime taxonomy | Reference tables or taxonomy service |
| Current model version | Model-registry lookup |
| Historical event dates | Event catalogue |
| Methodology and policy documents | Full-text or hybrid search |
| Semantically similar reports | Vector search |
| Final explanation | Local LLM |

### Future unstructured-data extension

Future versions may ingest approved public news or social-media feeds related to crime, transport disruption, major events, public disorder, or local conditions.

```text
Article or public post
        -> cleaning and deduplication
        -> provenance, location, and time tagging
        -> embedding model
        -> vector stored in pgvector
        -> semantic or hybrid retrieval
```

There are two distinct uses.

#### 1. Explanation enrichment

Retrieved articles or posts can provide supporting context for a structured forecast.

```text
Structured forecast
+
Retrieved contextual evidence
        -> evidence-backed explanation
```

The response must make clear that retrieved context did not necessarily cause or influence the forecast.

#### 2. Prediction enhancement

To make unstructured data influence the forecast, LCIP must convert the text into structured, time- and location-aligned features and retrain the predictive model.

```text
Unstructured sources
        -> classification / clustering / event extraction
        -> numeric features by borough and time window
        -> join to historical modelling dataset
        -> retrain and backtest forecast model
```

Example derived feature record:

```json
{
  "borough_id": "E09000003",
  "week": "2026-W26",
  "burglary_related_post_count": 142,
  "verified_news_article_count": 8,
  "public_disorder_event_flag": 1,
  "transport_disruption_score": 0.65
}
```

Vector retrieval alone does not improve a forecast. Any predictive improvement must be demonstrated through controlled training, temporal backtesting, leakage prevention, and evaluation.

---

## Model training, deployment, and persistence

### Model lifecycle

```text
Train candidate
      -> evaluate against baselines
      -> approve model version
      -> save artefact and metadata
      -> deploy for inference
      -> monitor data and forecast quality
      -> retrain under controlled conditions
```

Production inference normally does not modify the model weights. New data are collected and used in a separate retraining workflow.

### Runtime form

A trained model exists as a persisted artefact, for example:

```text
crime-forecast-v1.0.joblib
model.onnx
model.pkl
```

At runtime, an inference process loads the artefact into memory.

```text
Persisted model artefact -> in-memory model instance -> predictions
```

Several processes may load the same approved artefact. This produces multiple runtime instances of one model version.

### Server and container restarts

When a server or container stops:

- the in-memory model instance disappears;
- the persisted model artefact remains;
- stored forecast records remain;
- the restarted process reloads the artefact.

Training is lost only when the artefact and necessary metadata were never persisted or are deleted.

Containers are treated as disposable. Model artefacts, databases, metadata, and logs must live on persistent storage or in a versioned registry.

---

## Technology stack

### Backend

- ASP.NET Core / .NET 8
- Minimal APIs or Clean Architecture
- Dapper or Entity Framework Core
- Serilog

### Data engineering

- Python 3.11+
- Pandas
- Polars where useful
- Apache Airflow, with a simpler scheduler as an MVP alternative
- Great Expectations or equivalent validation

### Forecasting and machine learning

- naive and statistical baselines
- Prophet-style forecasting
- scikit-learn
- XGBoost where justified
- versioned serialised model artefacts
- experiment and model metadata

### Local AI layer

- Ollama or another local inference runtime
- a suitable local instruction-following model
- sentence-transformers for embeddings
- Semantic Kernel or a lightweight custom orchestrator
- structured output and schema-constrained tool calling

### Data and retrieval

- PostgreSQL
- PostGIS
- pgvector
- PostgreSQL full-text search

### Frontend

- React
- Plotly
- OpenStreetMap-compatible mapping

### Observability

- OpenTelemetry
- Prometheus
- Grafana
- Loki

### Infrastructure

- Docker Compose as the primary local runtime
- GitHub Actions for CI
- Kubernetes only as an optional later demonstration

---

## Repository structure

```text
lcip/
├── .github/
│   └── workflows/
├── contracts/                 # Shared JSON/Protobuf contracts
├── data/
│   ├── raw/                   # Immutable source payloads
│   ├── processed/             # Cleaned and spatially joined data
│   ├── curated/               # Analytical aggregates
│   ├── features/              # Training and inference features
│   └── shapefiles/            # Geographic boundaries
├── docs/
│   ├── architecture/          # Architecture diagrams and narratives
│   ├── decisions/             # Architecture Decision Records
│   ├── data-dictionary/       # Canonical fields and definitions
│   └── model-cards/           # Model purpose, metrics, and limitations
├── src/
│   ├── data_pipeline/
│   │   ├── run_pipeline.py
│   │   ├── pipeline_state.py
│   │   └── ...
│   ├── ml_engine/
│   │   ├── training/
│   │   ├── evaluation/
│   │   ├── inference/
│   │   ├── registry/
│   │   └── experiments/
│   ├── ai_assistant/
│   │   ├── parsing/
│   │   ├── tools/
│   │   ├── retrieval/
│   │   ├── prompts/
│   │   └── evaluation/
│   ├── backend/
│   │   ├── LCIP.Api/
│   │   ├── LCIP.Application/
│   │   ├── LCIP.Domain/
│   │   ├── LCIP.Infrastructure/
│   │   └── LCIP.sln
│   └── frontend/
├── tests/
│   ├── data/
│   ├── models/
│   ├── retrieval/
│   ├── assistant/
│   └── integration/
└── docker/
    ├── init/
    │   └── db/
    ├── observability/
    └── docker-compose.yml
```

The directory tree represents the intended structure. Keep it synchronised with the repository as components are implemented.

---

## Evaluation

LCIP evaluates the predictive model and AI assistant separately.

### Forecast evaluation

- time-based train, validation, and test splits;
- rolling-origin backtesting;
- comparison against naive baselines;
- MAE, RMSE, MASE, or other justified metrics;
- prediction-interval coverage;
- error analysis by borough, crime type, and season;
- data and performance drift monitoring.

Random train/test splitting must not be used for time-dependent forecasting when it would leak future information into training.

### Query, retrieval, and generation evaluation

- intent accuracy;
- entity-resolution accuracy;
- temporal-resolution accuracy;
- tool-selection accuracy;
- retrieval precision and recall;
- valid-schema rate;
- provenance and citation correctness;
- grounded-answer accuracy;
- ambiguity handling and abstention quality.

### End-to-end test set

Maintain a versioned set of natural-language questions with expected:

- canonical entities;
- resolved time windows;
- authorised tool calls;
- retrieved records;
- final factual answers.

---

## Observability, auditability, and security

Every generated answer should be traceable to:

- the original user question;
- the parsed domain request;
- resolver candidates and selected IDs;
- tool calls and query parameters;
- retrieved evidence;
- forecast and model versions;
- source document versions;
- LLM, prompt, and orchestration versions;
- the final answer and timestamp.

Operational evidence and decision records are required; private model reasoning traces are not.

### Security principles

- The LLM never receives unrestricted database credentials.
- The LLM cannot bypass application permissions.
- Unrestricted generated SQL is not executed.
- Retrieval is filtered by user permissions and data classification.
- External text is treated as untrusted input.
- Retrieved prompt-injection instructions are ignored by design.
- Major ambiguity is exposed rather than silently resolved.
- Forecasts include model versions and uncertainty where available.
- Generated explanations distinguish retrieved evidence from inference.

---

## Delivery roadmap

### Phase 1 — Data foundation

- ingest London crime data;
- define canonical borough and crime identifiers;
- validate and persist curated datasets;
- establish reproducible local infrastructure.

### Phase 2 — Forecast baseline

- implement naive and statistical baselines;
- add time-aware backtesting;
- persist versioned forecast records;
- expose forecasts through an API and dashboard.

### Phase 3 — Model lifecycle

- evaluate alternative machine-learning models;
- introduce experiment tracking and a model registry;
- package preprocessing with trained artefacts;
- implement controlled promotion and rollback.

### Phase 4 — Natural-language assistant

- host a local off-the-shelf LLM;
- define typed domain-query schemas;
- implement controlled tools for forecasts and reference data;
- generate evidence-grounded responses.

### Phase 5 — Geographic and temporal reasoning

- add PostGIS boundary operations;
- implement explicit temporal definitions;
- add an event catalogue and ambiguity handling;
- evaluate compositional questions.

### Phase 6 — Unstructured retrieval

- ingest approved news or public-text sources;
- add provenance, deduplication, embeddings, and pgvector;
- implement hybrid retrieval and evidence citations;
- keep explanation enrichment separate from predictive influence.

### Phase 7 — Predictive enrichment

- derive time- and location-aligned features from unstructured data;
- retrain and backtest forecasting models;
- retain new features only when they produce reliable and explainable improvement.

---

## Guiding principles

1. **Use deterministic systems for deterministic facts.**
2. **Use the LLM for language, not as the database.**
3. **Prefer stable identifiers over display strings.**
4. **Retrieve evidence before generating factual answers.**
5. **Validate every model-to-system boundary with typed schemas.**
6. **Treat trained models as versioned deployable artefacts.**
7. **Keep explanation enrichment separate from forecast enhancement.**
8. **Evaluate the forecasting model and AI assistant independently.**
9. **Expose uncertainty and ambiguity rather than hiding them.**
10. **Build the smallest architecture that preserves trust, testability, and growth.**

---

## Project status

LCIP is under active development. The repository should clearly distinguish between:

- implemented functionality;
- active work;
- planned capabilities;
- optional future extensions.

A useful status convention is:

| Marker | Meaning |
|---|---|
| ✅ | Implemented and demonstrable |
| 🚧 | In progress |
| 🗓️ | Planned |
| 💡 | Optional future extension |

---

## Licence

Add the selected open-source licence in a top-level `LICENSE` file.
