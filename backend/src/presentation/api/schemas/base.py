from pydantic import BaseModel


class PaginatedResultSchema[T](BaseModel):
    count: int
    results: list[T]
