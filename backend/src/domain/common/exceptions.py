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


class RepositoryError(DomainError):
    pass


class UniqueError(DomainError):

    def __init__(self, message, *, field):
        super().__init__(message)
        self.message = message
        self.field = field
