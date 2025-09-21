class DomainError(Exception):
    """Базовое исключение доменной логики."""


class ValidationError(DomainError): ...


class NotFoundError(DomainError): ...


class UnauthorizedError(DomainError): ...


class UniqueError(DomainError):

    def __init__(self, message, *, field):
        super().__init__(message)
        self.message = message
        self.field = field


class PermissionDeniedError(DomainError): ...


class InvalidPipelineError(DomainError): ...


class RepositoryError(DomainError):
    """Базовое исключение репозитория."""


class ObjectNotFoundError(RepositoryError):
    """Объект не найден в репозитории."""
