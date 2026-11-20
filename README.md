# AI Review Manager

**AI-Powered Customer Feedback Analysis & Intelligent Review Management**

AI Review Manager is a Python/FastAPI REST API project for turning customer reviews into actionable insights using large language models (LLMs). It currently supports local mock review retrieval, MongoDB connectivity checks, and **working AI analysis through Google Gemini or OpenAI** with a provider-independent interface.

> **Project status:** Work in progress. AI analysis is currently available through a Python test script, not yet through a public analysis API endpoint. Automated persistence, structured-output validation, analytics, and production integrations are planned.

## Implemented Features

- **FastAPI API** with OpenAPI/Swagger documentation.
- **100 synthetic customer reviews** in `data/reviews_mock.json`, exposed through the reviews endpoint.
- **MongoDB connectivity** via PyMongo, including a database health check.
- **Pluggable AI providers** through an abstract `AIProvider` contract, concrete Gemini/OpenAI adapters, and an `AIProviderFactory`.
- **Environment-based configuration** with Pydantic Settings.
- **External brand prompt** loaded from `app/prompts/review_analysis_prompt.md`.
- **AI-powered review analysis** that asks for sentiment, satisfaction score, reasoning, keywords, praises, criticisms, and a suggested public reply.
- **Token usage tracking** for input, output, and total tokens when reported by the provider.
- **Local AI smoke test** in `test_ai.py`.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.13 | Backend runtime |
| FastAPI / Uvicorn | HTTP API and OpenAPI documentation |
| Pydantic / Pydantic Settings | Models and configuration |
| Google Gen AI SDK | Gemini integration |
| OpenAI Python SDK | OpenAI integration |
| MongoDB / PyMongo | Database connectivity; planned analysis persistence |
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

**Planned processing path:** FastAPI analysis endpoint → review processing service → AI analysis → Pydantic-validated structured result → MongoDB `review_analyses` repository → reporting and analytics.

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
│   ├── models/                 # Review-related Pydantic models
│   ├── prompts/
│   │   └── review_analysis_prompt.md
│   ├── providers/
│   │   ├── base.py             # AIProvider / AIProviderResponse
│   │   ├── factory.py          # Provider selection
│   │   ├── gemini_provider.py
│   │   └── openai_provider.py
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

### Planned (not yet implemented)

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/reviews/{review_id}/analyze` | Analyze a review |
| GET | `/reviews/analyses` | List stored analyses |
| GET | `/reviews/{review_id}/analysis` | Fetch an analysis |
| GET | `/analytics/sentiment` | Sentiment breakdown |
| GET | `/analytics/topics` | Frequent praise/criticism topics |

## AI Analysis

The brand-specific prompt currently describes **Nuvem Roxa**, a fictional Brazilian açaí and ice cream shop. It instructs the model to classify customer feedback objectively and generate concise, empathetic public replies without inventing facts or promises.

The prompt requests these fields:

| Field | Meaning |
|---|---|
| `sentiment` | `POSITIVE`, `NEGATIVE`, `NEUTRAL`, or `MIXED` |
| `satisfaction_score` | Estimated score from 1 to 10 |
| `score_reason` | Short justification |
| `keywords` | Relevant terms |
| `praises` | Positive aspects |
| `criticisms` | Negative aspects |
| `suggested_reply` | Suggested customer-facing reply |

Example of a model-generated response:

```json
{
  "sentiment": "MIXED",
  "satisfaction_score": 6,
  "score_reason": "O cliente elogiou o sabor do açaí, mas criticou o tempo de espera para a entrega.",
  "keywords": ["açaí", "delicioso", "demora", "entrega"],
  "praises": ["sabor do açaí"],
  "criticisms": ["demora na entrega"],
  "suggested_reply": "Que bom que você gostou do nosso açaí! 💜 Sentimos muito pela demora na entrega e agradecemos pelo feedback."
}
```

**Current limitation:** The provider returns this JSON as **text** in `AIProviderResponse.content`. Schema-enforced structured outputs and Pydantic validation of the model response are **not implemented yet**. Suggested replies should be reviewed before publication.

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

## MongoDB and Data Roadmap

MongoDB connectivity is implemented, but automated analysis persistence is planned. The intended `review_analyses` collection will hold the original review reference, validated analysis fields, provider/model metadata, timestamps, and token usage.

Planned safeguards include avoiding duplicate processing, tracking prompt/model versions, and using stored analyses when a review has already been processed under the same configuration.

## Roadmap

- [x] FastAPI foundation and health endpoints
- [x] MongoDB connectivity health check
- [x] Synthetic review dataset and reviews endpoint
- [x] Provider-independent OpenAI and Gemini adapters
- [x] Markdown-based AI prompt
- [x] AI analysis smoke test
- [x] Input/output/total token tracking
- [x] Initial prompt optimization
- [ ] Schema-enforced structured outputs with Pydantic
- [ ] Automated unit and integration tests
- [ ] Review analysis API endpoint
- [ ] MongoDB analysis repository and persistence
- [ ] Idempotent processing and caching
- [ ] Token cost estimation and per-client usage reporting
- [ ] Sentiment/topic analytics
- [ ] External review provider integration

## Security and Privacy

Use synthetic data during development, keep API keys out of source control, and evaluate provider data-handling terms before sending real customer reviews. Model-generated replies can be inaccurate or imply commitments that the business has not made; human review is recommended before publishing.

## License

MIT License. See `LICENSE` for details.

---

**AI Review Manager** — *Transforming customer feedback into intelligent business insights.*
