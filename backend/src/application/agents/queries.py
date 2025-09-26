from dataclasses import dataclass


@dataclass
class AgentsQuery:
    page: int
    page_size: int
    search: str | None = None
    temp_lt: float | None = None
    temp_gt: float | None = None
