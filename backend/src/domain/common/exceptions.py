class DomainError(Exception):
    """Базовое исключение доменной логики."""


class ValidationError(DomainError):
    pass


class NotFoundError(DomainError):
    pass


class UnauthorizedError(DomainError):
    pass


class AgentUnavailableError(DomainError):
    pass
