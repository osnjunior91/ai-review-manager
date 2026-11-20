# AI Review Manager

### AI-Powered Customer Feedback Analysis & Intelligent Review Management

AI Review Manager is a Python-based REST API designed to transform customer reviews into actionable business insights using **Artificial Intelligence (AI)** and **Natural Language Processing (NLP)**.

The application is designed to retrieve customer feedback from external data providers, analyze customer sentiment, identify praised and criticized products or service aspects, generate contextual reply suggestions, and persist structured analysis results in MongoDB.

The project emphasizes **clean code, modular architecture, maintainability, extensibility, and provider-independent integrations**.

## Key Features

- **Customer Review Integration** — Retrieve and validate customer reviews through a provider-independent integration layer.
- **Sentiment Analysis** — Classify customer feedback as positive, negative, neutral, or mixed.
- **Keyword and Topic Extraction** — Identify relevant terms, recurring subjects, and customer concerns.
- **Praise and Criticism Detection** — Extract products, services, and specific aspects mentioned positively or negatively.
- **AI-Powered Reply Suggestions** — Generate contextual, personalized responses to customer feedback.
- **MongoDB Persistence** — Store structured AI analysis results for subsequent retrieval and reporting.
- **Review Processing Management** — Coordinate analysis workflows and prevent unnecessary duplicate processing.
- **Customer Satisfaction Analytics** — Explore sentiment trends, frequently criticized items, and recurring positive experiences.
- **Health Monitoring** — Provide application and MongoDB connectivity health checks.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.13 | Backend development |
| FastAPI | RESTful API development and OpenAPI documentation |
| Pydantic | Typed data models, validation, and serialization |
| Pydantic Settings | Environment-based application configuration |
| MongoDB | Persistent storage for review analysis results |
| PyMongo | MongoDB database connectivity |
| Docker | Local MongoDB development environment |
| NLP / LLMs | AI-powered feedback analysis and reply generation |
| JSON | Synthetic customer review dataset |
| Postman | API testing and request collections |
| pytest | Automated testing |

## System Architecture

The application follows a layered architecture that separates external review retrieval, business logic, AI processing, and data persistence.

```text
             External Review Provider
                       |
                       v
                ReviewApiClient
                       |
                       v
                  FastAPI API
                       |
                       v
             ReviewProcessingService
                       |
             +---------+---------+
             |                   |
             v                   v
     ReviewAnalysisRepository  AIAnalysisService
             |                   |
             v                   +------------------+
          MongoDB                |                  |
             ^                   v                  v
             |             Sentiment Analysis   Topic Detection
             |                   |                  |
             |                   +--------+---------+
             |                            |
             |                            v
             |                   Praise / Criticism
             |                         Extraction
             |                            |
             |                            v
             |                    AI Reply Suggestion
             |                            |
             +----------------------------+
                       |
                       v
                Stored AI Analysis
                       |
                       v
               REST API / Analytics
```

### Architecture Principles

- Separation of concerns
- Layered and modular service design
- Dependency injection
- Strongly typed Pydantic models
- Provider-independent data integration
- Dedicated database access layer
- Environment-based configuration
- Explicit API contracts and error handling
- Testability and extensibility
- Reusable database connections and efficient resource management

## Project Structure

```text
ai-review-manager/
├── app/
│   ├── clients/
│   │   └── review_api_client.py
│   ├── controllers/
│   │   ├── health_controller.py
│   │   └── reviews_controller.py
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   ├── models/
│   │   ├── review.py
│   │   ├── review_order.py
│   │   ├── review_reply.py
│   │   ├── reviews_response.py
│   │   └── review_analysis.py
│   ├── repositories/
│   │   └── review_analysis_repository.py
│   ├── services/
│   │   ├── review_processing_service.py
│   │   └── ai_analysis_service.py
│   └── main.py
├── data/
│   └── reviews_mock.json
├── postman/
├── .env.example
├── .gitignore
├── requirements.txt
├── LICENSE
└── README.md
```

*The structure represents the modular application design, including components intended for AI processing and database persistence.*

## MongoDB Integration

MongoDB is used as the persistence layer for AI-generated customer feedback analyses.

The application separates the original customer review data from the structured analysis produced by the AI processing pipeline.

### Data Responsibilities

**External Review Data**

Customer reviews are retrieved from external providers or loaded from the synthetic dataset. They include review identifiers, ratings, comments, timestamps, order information, statuses, and reply histories.

**AI Analysis Data**

The application is designed to persist:

- Original review references
- Sentiment classification
- Extracted keywords
- Praised products and service aspects
- Criticized products and service aspects
- AI-generated reply suggestions
- Processing metadata and timestamps

The intended MongoDB collection is `review_analyses`.

### Example Analysis Document

```json
{
  "review_id": "review-001",
  "sentiment": "mixed",
  "keywords": [
    "product quality",
    "delivery",
    "waiting time"
  ],
  "praises": [
    "Product quality"
  ],
  "criticisms": [
    "Delivery delay"
  ],
  "suggested_reply": "Thank you for your feedback! We're glad you enjoyed the product quality, and we apologize for the delivery delay. Your feedback helps us improve our service.",
  "processed_at": "2026-11-20T15:00:00Z"
}
```

*This example illustrates the intended persisted analysis structure.*

## Application Configuration

Application settings are managed through **Pydantic Settings**, using environment variables and a local `.env` file.

Create a `.env` file based on `.env.example`:

```dotenv
APP_NAME="AI Review Manager"
API_VERSION="1.0.0"
APP_DESCRIPTION="AI-powered customer review management API"

MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=ai_review_manager
```

Sensitive configuration values should not be committed to version control.

## Getting Started

### Prerequisites

- Python 3.13 or compatible version
- Docker, or an accessible MongoDB instance
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-review-manager
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env` and adjust the MongoDB connection settings if necessary.

### 5. Start MongoDB

Run MongoDB locally with Docker:

```bash
docker run -d \
  --name ai-review-mongodb \
  -p 127.0.0.1:27017:27017 \
  -v ai-review-mongo-data:/data/db \
  mongo:8
```

For Windows PowerShell, use the single-line equivalent:

```powershell
docker run -d --name ai-review-mongodb -p 127.0.0.1:27017:27017 -v ai-review-mongo-data:/data/db mongo:8
```

### 6. Start the API

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

## API Endpoints

### Application Health

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Retrieve application health information |
| GET | `/health/database` | Verify MongoDB connectivity |
| GET | `/version` | Retrieve the current API version |

### Review Management

| Method | Endpoint | Description |
|---|---|---|
| GET | `/reviews/` | Retrieve paginated customer reviews |

### Planned AI Processing and Analytics

| Method | Endpoint | Description |
|---|---|---|
| POST | `/reviews/{review_id}/analyze` | Process a review using AI |
| GET | `/reviews/analyses` | Retrieve stored AI analysis results |
| GET | `/reviews/{review_id}/analysis` | Retrieve the analysis of a specific review |
| GET | `/analytics/sentiment` | Retrieve sentiment distribution |
| GET | `/analytics/topics` | Retrieve frequently praised and criticized topics |

## Health Monitoring

The API provides separate health endpoints for application availability and database connectivity.

### Application Health

`GET /health`

Example response:

```json
{
  "status": "healthy",
  "service": "AI Review Manager",
  "description": "AI-powered customer review management API",
  "version": "1.0.0"
}
```

### MongoDB Health

`GET /health/database`

Successful response:

```json
{
  "status": "healthy",
  "database": "mongodb",
  "connection": "connected"
}
```

If MongoDB is unavailable, the database health endpoint returns HTTP `503 Service Unavailable`.

This separation allows the application to distinguish API availability from database readiness.

## Synthetic Review Dataset

The project includes **100 synthetic customer reviews** designed to simulate realistic feedback scenarios.

The dataset contains different ratings, comments, review statuses, timestamps, associated orders, and reply histories.

Synthetic data offers several advantages:

- **Privacy:** No real customer information is required.
- **Reproducibility:** Consistent test scenarios across development environments.
- **Controlled Testing:** Positive, negative, neutral, and mixed feedback scenarios.
- **Independence:** No external review platform credentials are required for local testing.

All review data is fictional and used exclusively for development, testing, and demonstration purposes.

## AI-Powered Review Analysis

The intended AI processing workflow transforms unstructured customer feedback into structured business information.

### Example Customer Review

```json
{
  "id": "review-001",
  "score": 3,
  "comment": "The product quality was excellent, but delivery took much longer than expected."
}
```

### Example Analysis Result

```json
{
  "review_id": "review-001",
  "sentiment": "mixed",
  "keywords": [
    "product quality",
    "delivery time"
  ],
  "praises": [
    "Product quality"
  ],
  "criticisms": [
    "Delivery delay"
  ],
  "suggested_reply": "Thank you for your feedback! We're glad you enjoyed the product quality, and we apologize for the delivery delay. Your feedback helps us improve our service."
}
```

*This example demonstrates the intended AI-generated output. AI processing and automated analysis persistence are part of the planned application capabilities.*

## Engineering Highlights

### Backend Engineering

RESTful API development with Python and FastAPI, strongly typed Pydantic models, structured responses, and environment-based configuration.

### Database Integration

MongoDB connectivity using PyMongo, with a dedicated database abstraction and health monitoring.

### Software Architecture

Separation between controllers, data providers, services, models, and repositories to support independent evolution of the application components.

### AI Integration

A modular design for sentiment classification, keyword extraction, aspect-based feedback analysis, and contextual reply generation.

### Data Privacy and Testing

Synthetic datasets enable reproducible testing and demonstrations without exposing real customer information.

## Use Cases

AI Review Manager can be adapted to:

- Customer experience monitoring
- Product feedback analysis
- Customer support assistance
- Service quality evaluation
- Brand reputation analysis
- Customer satisfaction reporting
- Automated feedback classification
- Business intelligence and trend detection

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

**AI Review Manager**

*Transforming customer feedback into intelligent business insights.*