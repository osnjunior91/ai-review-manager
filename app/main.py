from fastapi import FastAPI
from typing_extensions import Final

API_VERSION: Final[str] = "1.0.0"

app = FastAPI(
        title="AI Review Manager", 
        description="AI-powered customer review management API", 
        version=API_VERSION
    )

@app.get("/health")
def read_health():
    return {
        "status": "healthy",
        "service": "ai-review-manager",
        "version": API_VERSION
    }