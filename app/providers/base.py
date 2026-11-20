from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class AIProviderResponse:
    content: str
    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    model: str


class AIProvider(ABC):

    @abstractmethod
    def generate(
        self,
        instructions: str,
        content: str
    ) -> AIProviderResponse:
        pass