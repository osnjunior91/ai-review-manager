from openai import OpenAI

from app.providers.base import AIProvider, AIProviderResponse


class OpenAIProvider(AIProvider):

    def __init__(self, api_key: str, model: str):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(
        self,
        instructions: str,
        content: str
    ) -> AIProviderResponse:

        response = self.client.responses.create(
            model=self.model,
            instructions=instructions,
            input=content
        )

        usage = response.usage

        return AIProviderResponse(
            content=response.output_text,
            input_tokens=usage.input_tokens if usage else None,
            output_tokens=usage.output_tokens if usage else None,
            total_tokens=usage.total_tokens if usage else None,
            model=self.model
        )