from google import genai
from google.genai import types

from app.providers.base import AIProvider, AIProviderResponse


class GeminiProvider(AIProvider):

    def __init__(self, api_key: str, model: str):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate(
        self,
        instructions: str,
        content: str
    ) -> AIProviderResponse:

        response = self.client.models.generate_content(
            model=self.model,
            contents=content,
            config=types.GenerateContentConfig(
                system_instruction=instructions
            )
        )

        usage = response.usage_metadata

        return AIProviderResponse(
            content=response.text or "",
            input_tokens=(
                usage.prompt_token_count
                if usage else None
            ),
            output_tokens=(
                usage.candidates_token_count
                if usage else None
            ),
            total_tokens=(
                usage.total_token_count
                if usage else None
            ),
            model=self.model
        )