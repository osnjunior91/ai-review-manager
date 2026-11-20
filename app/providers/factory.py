from app.core.config import get_settings
from app.providers.base import AIProvider
from app.providers.openai_provider import OpenAIProvider
from app.providers.gemini_provider import GeminiProvider


class AIProviderFactory:

    @staticmethod
    def create() -> AIProvider:
        settings = get_settings()

        provider = settings.ai_provider.strip().lower()

        match provider:
            case "openai":
                if not settings.openai_api_key:
                    raise ValueError("OPENAI_API_KEY is not configured")

                return OpenAIProvider(
                    api_key=settings.openai_api_key,
                    model=settings.ai_model
                )

            case "gemini":
                if not settings.gemini_api_key:
                    raise ValueError("GEMINI_API_KEY is not configured")

                return GeminiProvider(
                    api_key=settings.gemini_api_key,
                    model=settings.ai_model
                )

            case _:
                raise ValueError(
                    f"Unsupported AI provider: {provider}"
                )