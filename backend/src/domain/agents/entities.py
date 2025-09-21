from dataclasses import dataclass
from typing import Self
from uuid import UUID, uuid4

from src.domain.common.exceptions import ValidationError


@dataclass(slots=True)
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
            raise ValidationError("Temperature must be between 0 and 1")

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
            raise ValidationError("Prompt cannot be empty")
        self.prompt = new_prompt

    def patch(self, **kwargs) -> Self:
        if temperature := kwargs.get("temperature"):
            if not isinstance(temperature, (int, float)):
                raise ValidationError("Temperature must be a number between 0 and 1")
            if not (0 <= temperature <= 1):
                raise ValidationError("Temperature must be between 0 and 1")
            self.temperature = temperature
        if prompt := kwargs.get("prompt"):
            if not prompt.strip():
                raise ValidationError("Prompt cannot be empty")
            self.prompt = kwargs["prompt"]
        if name := kwargs.get("name"):
            if not name.strip():
                raise ValidationError("Name cannot be empty")
            self.name = kwargs["name"]
        if description := kwargs.get("description"):
            self.description = description.strip()
        return self
