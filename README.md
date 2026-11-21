# AI Review Manager

**AI-Powered Customer Feedback Analysis & Intelligent Review Management**

AI Review Manager is a Python/FastAPI REST API project for turning customer reviews into actionable insights using large language models (LLMs). It supports mock review retrieval, MongoDB connectivity, Gemini/OpenAI integrations, structured Gemini output validation, and a MongoDB repository with atomic review-processing reservations.

> **Project status:** Work in progress. AI analysis is available through local Python tests, not yet through a public analysis endpoint. The MongoDB repository and reservation/completion primitives exist, but the end-to-end AI processing orchestration, failure handler, and analytics API are not yet integrated.

## Implemented Features

- **FastAPI API** with OpenAPI/Swagger documentation.
- **100 synthetic customer reviews** in `data/reviews_mock.json`, exposed through the reviews endpoint.
- **MongoDB connectivity** via PyMongo, including a database health check.
- **Pluggable AI providers** through an abstract `AIProvider` contract, concrete Gemini/OpenAI adapters, and an `AIProviderFactory`.
- **Environment-based configuration** with Pydantic Settings.
- **External brand prompt** loaded from `app/prompts/review_analysis_prompt.md`.
- **AI-powered review analysis** that asks for sentiment, satisfaction score, reasoning, keywords, praises, criticisms, and a suggested public reply.
- **Token usage tracking** for input, output, and total tokens when reported by the provider.
- **Structured Gemini responses** using `AIAnalysisResult` as the response schema, with Pydantic validation.
- **MongoDB review analysis model and repository**, including `save()`, `find()`, `try_acquire()`, and `complete()`.
- **Compound unique index** on `(tenant_id, platform, external_review_id)` to prevent duplicate review identities.
- **Atomic processing reservations** with UUID tokens, a five-minute default lease, and recovery of `FAILED` or expired `PROCESSING` records.
- **Token-checked completion** to prevent stale workers from overwriting a newer processing attempt.
- **Local AI smoke test** in `test_ai.py`.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.13 | Backend runtime |
| FastAPI / Uvicorn | HTTP API and OpenAPI documentation |
| Pydantic / Pydantic Settings | Models and configuration |
| Google Gen AI SDK | Gemini integration |
| OpenAI Python SDK | OpenAI integration |
| MongoDB / PyMongo | Database connectivity, analysis persistence, and processing coordination |
| Docker | Optional local MongoDB environment |
| JSON | Synthetic review dataset |

## Architecture

```text
                          +----------------------+
                          | FastAPI Controllers  |
                          | health / reviews     |
                          +----------+-----------+
                                     |
                     +---------------+----------------+
                     |                                |
                     v                                v
              Mock Review Data                MongoDatabase
              (100 JSON reviews)              (health / ping)

                Local test_ai.py
                       |
                       v
               AIAnalysisService
                       |
             Load Markdown prompt
                       |
                       v
               AIProviderFactory
                       |
                AIProvider (ABC)
                 /           \
                v             v
         GeminiProvider   OpenAIProvider
                \             /
                 v           v
                AIProviderResponse
           (content, model, token usage)
```

**Implemented components:** Gemini schema validation and MongoDB `review_analyses` repository with processing reservation/completion methods. **Planned end-to-end path:** FastAPI analysis endpoint → processing service calls `try_acquire()` → Gemini/OpenAI analysis → validated result → `complete()` → stored result lookup and analytics. The repository does not currently invoke the AI service automatically.

The AI service accepts an injected provider, making it easier to test or replace model integrations without changing the orchestration code.

## Project Structure

```text
ai-review-manager/
├── app/
│   ├── clients/                # External review client layer
│   ├── controllers/            # Health and review routes
│   ├── core/
│   │   ├── config.py           # Pydantic Settings
│   │   └── database.py         # MongoDB connection abstraction
│   ├── models/
│   │   ├── ai_analysis_result.py # Validated AI response schema
│   │   └── review_analysis.py   # Stored analysis / processing state
│   ├── prompts/
│   │   └── review_analysis_prompt.md
│   ├── providers/
│   │   ├── base.py             # AIProvider / AIProviderResponse
│   │   ├── factory.py          # Provider selection
│   │   ├── gemini_provider.py
│   │   └── openai_provider.py
│   ├── repositories/
│   │   └── review_analysis_repository.py
│   ├── services/
│   │   └── ai_analysis_service.py
│   └── main.py
├── data/
│   └── reviews_mock.json
├── test_ai.py                  # Manual integration smoke test
├── .env.example
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.13
- Git
- Docker **or** a reachable MongoDB instance
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/api-keys) or an OpenAI API key

### 1. Clone and install

```powershell
git clone https://github.com/osnjunior91/ai-review-manager.git
cd ai-review-manager
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On macOS/Linux, activate the environment with `source .venv/bin/activate`.

### 2. Configure environment variables

Copy the example configuration:

```powershell
Copy-Item .env.example .env
```

For the **Gemini** provider, use:

```dotenv
APP_NAME="AI Review Manager"
API_VERSION="1.0.0"
APP_DESCRIPTION="AI-powered customer review management API"

MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=ai_review_manager

AI_PROVIDER=gemini
AI_MODEL=gemini-3.5-flash-lite
AI_PROMPT_PATH=app/prompts/review_analysis_prompt.md

GEMINI_API_KEY=your_real_key_here
```

> **Model availability changes.** `gemini-3.5-flash-lite` was verified in a local integration test, but check availability and quota for your own account. The repository's `.env.example` may still show an older model; use an available model in your local `.env`.

To switch providers, set `AI_PROVIDER=openai`, choose an OpenAI model available to your API account, and configure `OPENAI_API_KEY`. Only the selected provider's key is required.

**Never commit `.env` or real API keys.** The two providers have separate API billing and quotas; a ChatGPT subscription does not include OpenAI API credits.

### 3. Start MongoDB (optional for the AI smoke test)

With Docker:

```powershell
docker run -d --name ai-review-mongodb -p 127.0.0.1:27017:27017 -v ai-review-mongo-data:/data/db mongo:8
```

The standalone AI smoke test does not require a database connection.

### 4. Start the API

```powershell
python -m uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs

### 5. Run an AI analysis

From the project root, with the virtual environment active and the API key configured:

```powershell
python test_ai.py
```

The script sends this sample review:

> O açaí estava delicioso, mas demorou muito para chegar!

It prints the generated analysis text, selected model, and token usage. A successful test with Gemini classified the review as `MIXED` and assigned a satisfaction score of `6/10`.

## API Endpoints

### Available now

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Application health |
| GET | `/health/database` | MongoDB connectivity |
| GET | `/version` | API version |
| GET | `/reviews/` | Retrieve synthetic customer reviews |
| POST | `/reviews/analyze` | Analyze random synthetic reviews with idempotent processing |
| GET | `/reviews/analyses` | List stored analyses with filters and MongoDB pagination |
| GET | `/reviews/analyses/{id}` | Fetch one analysis by MongoDB ObjectId |
| GET | `/reviews/statistics` | Aggregated sentiment, satisfaction, severity, keyword, criticism, and category statistics |
| GET | `/reviews/usage` | Recorded token usage and estimated model cost |

### Planned (not yet implemented)

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/reviews/{review_id}/analyze` | Analyze a review |
| GET | `/analytics/sentiment` | Sentiment breakdown |
| GET | `/analytics/topics` | Frequent praise/criticism topics |

### Query and report endpoints

`GET /reviews/analyses` accepts `page` (default `1`), `page_size` (default `20`, maximum `100`), `tenant_id`, `platform`, `status` (`PROCESSING`, `COMPLETED`, or `FAILED`), `sentiment`, `severity`, `requires_attention`, `start_date`, and `end_date`. Dates are interpreted as UTC. The reporting date interval starts inclusively and ends exclusively, using `processed_at` when available and otherwise `created_at`.

Example:

```text
GET /reviews/analyses?page=1&page_size=20&tenant_id=nuvem-roxa-001&platform=IFOOD&status=COMPLETED&sentiment=POSITIVE
```

`GET /reviews/analyses/{id}` requires a valid MongoDB ObjectId. An optional `tenant_id` restricts the lookup to that tenant. Invalid IDs return `400`; missing documents return `404`.

`GET /reviews/statistics` accepts `tenant_id`, `platform`, `start_date`, and `end_date`. It returns status totals, sentiment/severity distributions, average satisfaction, attention count, negative percentage, top keywords and criticisms, and category counts. Sentiment, satisfaction, severity, keywords, criticisms, and categories use only `COMPLETED` documents with a valid `analysis`. The negative percentage denominator is the count of those valid completed analyses.

`GET /reviews/usage` accepts `tenant_id`, `ai_provider`, `ai_model`, `start_date`, `end_date`, and `group_by` (`day`, `month`, `model`, or `provider`). Input, output, and total tokens are aggregated with MongoDB pipelines. Missing or null token fields are not converted to zero and are reported as unknown metrics.

Model pricing is centralized in `app/core/model_rates.py`. It is intentionally empty until verified USD-per-million input/output tariffs are configured. When a tariff is absent or a document lacks complete metrics, cost is omitted or `null` and `cost_is_complete` is `false`; a group containing complete and unknown metrics may show a partial estimate while remaining explicitly incomplete. Costs are estimates, not billed charges. Recorded usage may exclude tokens consumed by requests that failed before MongoDB persistence.

## AI Analysis

The brand-specific prompt currently describes **Nuvem Roxa**, a fictional Brazilian açaí and ice cream shop. It instructs the model to classify customer feedback objectively and generate concise, empathetic public replies without inventing facts or promises.

The Gemini integration requests and validates these fields using the `AIAnalysisResult` Pydantic schema:

| Field | Meaning |
|---|---|
| `sentiment` | `POSITIVE`, `NEGATIVE`, `NEUTRAL`, or `MIXED` |
| `satisfaction_score` | Estimated score from 1 to 10 |
| `score_reason` | Short justification |
| `keywords` | Relevant terms |
| `praises` | Positive aspects |
| `criticisms` | Negative aspects |
| `suggested_reply` | Suggested customer-facing reply |
| `categories` | One or more of `PRODUCT`, `DELIVERY`, `SERVICE`, `PRICE`, `OTHER` |
| `severity` | `LOW`, `MEDIUM`, or `HIGH` |
| `requires_attention` | Whether human attention is required |

Example of a model-generated response:

```json
{
  "sentiment": "MIXED",
  "satisfaction_score": 6,
  "score_reason": "O cliente elogiou o sabor do açaí, mas criticou o tempo de espera para a entrega.",
  "keywords": ["açaí", "delicioso", "demora", "entrega"],
  "praises": ["sabor do açaí"],
  "criticisms": ["demora na entrega"],
  "categories": ["PRODUCT", "DELIVERY"],
  "severity": "MEDIUM",
  "requires_attention": false,
  "suggested_reply": "Que bom que você gostou do nosso açaí! 💜 Sentimos muito pela demora na entrega e agradecemos pelo feedback."
}
```

**Current behavior:** `GeminiProvider` requests JSON matching `AIAnalysisResult`, validates it with Pydantic, and serializes the validated result into `AIProviderResponse.content`. The shared provider response still carries JSON as a string. Do not assume the OpenAI adapter has the same schema enforcement without verifying it separately. Suggested replies should be reviewed before publication.

### Provider Contract

`AIProvider.generate(instructions, content)` returns:

```python
@dataclass
class AIProviderResponse:
    content: str
    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    model: str
```

Provider implementations adapt their respective SDK usage metadata to this common response. Token counts may be `None` if unavailable, and some models may report additional internal reasoning tokens.

## Token Optimization

A local before/after test used the **same review and model** with a shorter system prompt:

| Metric | Original prompt | Optimized prompt | Reduction |
|---|---:|---:|---:|
| Input tokens | 1,418 | 418 | 70.5% |
| Output tokens | 207 | 176 | 15.0% |
| **Total tokens** | **1,625** | **594** | **63.4%** |

These are observations from **one test case**, not a guaranteed average. Input tokens decreased primarily by removing repetitive prompt instructions. Future evaluations should compare both token consumption and response quality across a larger review set.

The current integration tracks usage but **does not calculate prices or persist usage records**. API prices, free-tier quotas, and model availability are subject to provider changes.

## MongoDB Persistence and Idempotency

The `ReviewAnalysis` Pydantic model (`app/models/review_analysis.py`) represents a stored analysis and its processing state. It contains:

- Identity: `tenant_id`, `platform`, `external_review_id`.
- Processing: `status` (`PROCESSING`, `COMPLETED`, `FAILED`), `processing_token`, `lease_until`, `last_error`.
- Result: optional `analysis: AIAnalysisResult`.
- Metadata: `ai_provider`, `ai_model`, input/output/total tokens.
- Reply approval: `reply_status` (`PENDING_APPROVAL`, `APPROVED`, `REJECTED`).
- Timestamps: `created_at`, `updated_at`, `processed_at`.

### Repository operations

`ReviewAnalysisRepository` in `app/repositories/review_analysis_repository.py` uses the `review_analyses` collection:

| Method | Behavior |
|---|---|
| `save(review)` | Inserts a Pydantic model and returns the MongoDB ID as a string |
| `find(tenant_id, platform, external_review_id)` | Looks up one analysis by its composite identity |
| `try_acquire(..., lease_seconds=300)` | Attempts an atomic processing reservation; returns a UUID token or `None` |
| `complete(..., processing_token, analysis)` | Completes only an active, unexpired reservation with a matching token; returns `bool` |

The repository constructor creates the unique compound index `uq_tenant_platform_review` on `(tenant_id, platform, external_review_id)`. The index prevents two documents with the same review identity and ensures competing initial inserts cannot both succeed. Index creation fails if existing documents violate that uniqueness constraint.

### Reservation flow

1. `try_acquire()` first attempts to insert a `PROCESSING` record with a UUID `processing_token` and a lease expiry (300 seconds by default).
2. If the identity already exists, MongoDB raises `DuplicateKeyError`. The repository then uses `find_one_and_update()` to atomically acquire an existing `FAILED` record or a `PROCESSING` record with an expired lease.
3. A `COMPLETED` record or a `PROCESSING` record with a valid lease cannot be acquired and yields `None`.
4. After an AI result is available, `complete()` updates the record only if the status is `PROCESSING`, the token matches, and `lease_until` is still in the future. It writes `analysis`, sets `status=COMPLETED`, records `completed_at`, and unsets the temporary reservation fields.

**Concurrency scope:** The insert plus unique index and the conditional MongoDB updates protect the *reservation*. They do not make the external Gemini call transactional. If a worker calls Gemini but crashes before completing the record, a later attempt may call Gemini again after the lease expires. A lease expiring while a worker is still running can also lead to overlapping external calls; the token check prevents a stale worker from committing its result.

**Current gaps:** There is not yet a `fail()` method, lease renewal/heartbeat, a processing service that orchestrates `try_acquire() → AI → complete()`, or an API endpoint that returns a cached completed analysis. The model defines `processed_at`, while the current `complete()` method writes `completed_at`; these timestamp names should be aligned. The repository's `find()` validates MongoDB documents as Pydantic models; integration tests should cover BSON `_id` and schema consistency.

### Manual reservation test

With MongoDB running, the project root active, and the virtual environment enabled, create a temporary script such as `test_acquire.py`:

```python
from uuid import uuid4

from app.core.database import MongoDatabase
from app.repositories.review_analysis_repository import ReviewAnalysisRepository

db = MongoDatabase()
try:
    repository = ReviewAnalysisRepository(db)
    review_id = str(uuid4())

    first = repository.try_acquire("loja-001", "IFOOD", review_id)
    second = repository.try_acquire("loja-001", "IFOOD", review_id)

    print("First reservation:", first)   # UUID
    print("Second reservation:", second) # None

    if first is not None:
        completed = repository.complete(
            "loja-001", "IFOOD", review_id, first,
            {"sentiment": "POSITIVE", "satisfaction_score": 10}
        )
        print("Completed:", completed)  # True
        print("After completion:", repository.try_acquire(
            "loja-001", "IFOOD", review_id
        ))  # None
finally:
    db.close()
```

Run `python test_acquire.py`. The minimal `analysis` dictionary here demonstrates repository persistence only; real Gemini results should conform to the complete `AIAnalysisResult` schema. For recovery testing, set a test document's `status` to `FAILED` in MongoDB Compass and call `try_acquire()` again. This test file is an example to create locally, not a committed automated test.

## Automated tests

Run the isolated pytest suite without any Gemini or OpenAI calls:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install pytest
python -m pytest -q tests
```

The tests use mocks for repository and service behavior and verify endpoint schemas and parameter validation.

## Roadmap

- [x] FastAPI foundation and health endpoints
- [x] MongoDB connectivity health check
- [x] Synthetic review dataset and reviews endpoint
- [x] Provider-independent OpenAI and Gemini adapters
- [x] Markdown-based AI prompt
- [x] AI analysis smoke test
- [x] Input/output/total token tracking
- [x] Initial prompt optimization
- [x] Schema-enforced Gemini structured outputs with Pydantic
- [ ] Automated unit and integration tests
- [ ] Review analysis API endpoint
- [x] MongoDB analysis model, repository, and direct persistence methods
- [x] Unique compound review identity index
- [x] Atomic processing reservation with token and lease expiry
- [x] Token-checked processing completion
- [ ] Failure handling and retry policy (`fail()`)
- [ ] End-to-end idempotent AI orchestration and cached result retrieval
- [ ] Token cost estimation and per-client usage reporting
- [ ] Sentiment/topic analytics
- [ ] External review provider integration

## Security and Privacy

Use synthetic data during development, keep API keys out of source control, and evaluate provider data-handling terms before sending real customer reviews. Model-generated replies can be inaccurate or imply commitments that the business has not made; human review is recommended before publishing.

## License

MIT License. See `LICENSE` for details.

---

**AI Review Manager** — *Transforming customer feedback into intelligent business insights.*
