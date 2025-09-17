from dataclasses import dataclass
from typing import Self
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class Agent:
    id: UUID
    name: str
    description: str
    prompt: str
    temperature: float = 0.7

    @classmethod
    def create(cls, name: str, description: str, prompt: str, temperature: float = 0.7) -> Self:
        """Фабричный метод — создание агента с валидацией."""
        if not (0 <= temperature <= 1):
            raise ValueError("Temperature must be between 0 and 1")

        return cls(
            id=uuid4(),
            name=name,
            description=description,
            prompt=prompt,
            temperature=temperature,
        )

    def update_prompt(self, new_prompt: str) -> None:
        """Изменить prompt агента."""
        if not new_prompt.strip():
            raise ValueError("Prompt cannot be empty")
        self.prompt = new_prompt
