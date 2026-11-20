from pathlib import Path

from app.core.config import get_settings
from app.providers.base import AIProvider, AIProviderResponse
from app.providers.factory import AIProviderFactory


class AIAnalysisService:

    def __init__(self, provider: AIProvider | None = None):
        self.settings = get_settings()
        self.provider = provider or AIProviderFactory.create()

    def analyze(self, review_comment: str) -> AIProviderResponse:

        instructions = Path(
            self.settings.ai_prompt_path
        ).read_text(encoding="utf-8")

        return self.provider.generate(
            instructions=instructions,
            content=review_comment
        )